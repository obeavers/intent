#!/usr/bin/env python3
"""Preserve Atomic aggregate/worker source without changing their Git state.

The checkpoint contains changed file payloads (including untracked and intent-to-add
files), binary diffs, exact indexes, deletion/mode metadata, and complete ref bundles.
Its verifier checks archived payloads and bundle integrity without restoring over a
source tree. This is a recovery artifact, not implementation qualification.
"""

import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / 'docs/plans/atomic-reconciliation-inventory-2026-11-18.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def git(path, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    run = subprocess.run(
        ['git', '--no-optional-locks', '-C', str(path), *args],
        env=env, capture_output=True, check=False,
    )
    if run.returncode:
        raise RuntimeError(f'git {args[0]} failed in {path}: '
                           f'{run.stderr.decode(errors="replace").strip()}')
    return run.stdout


def permitted(relative):
    path = Path(relative)
    return (not path.is_absolute() and '..' not in path.parts and bool(path.parts)
            and path.parts[0] not in {'.git', '.reconciliation'})


def current_status(path):
    return git(path, 'status', '--porcelain=v1', '-z', '--untracked-files=all',
               '--', '.', ':(exclude).reconciliation')


def source_index(path):
    raw = git(path, 'rev-parse', '--path-format=absolute', '--git-path', 'index')
    index_path = Path(os.fsdecode(raw).strip())
    return index_path.read_bytes() if index_path.exists() else b''


def capture_tree(tree, directory):
    path = Path(tree['path'])
    directory.mkdir(parents=True, mode=0o700)
    head = git(path, 'rev-parse', 'HEAD').decode().strip()
    status_before = current_status(path)
    index_before = source_index(path)
    paths = set(tree['inventoryPaths'])
    for args in [('diff', '--name-only', '-z', 'HEAD'),
                 ('ls-files', '--others', '--exclude-standard', '-z')]:
        paths.update(os.fsdecode(p) for p in git(path, *args).split(b'\0') if p)
    paths = sorted(p for p in paths if permitted(p))
    tracked_modes = {}
    for record in git(path, 'ls-files', '--stage', '-z').split(b'\0'):
        if record:
            metadata, name = record.split(b'\t', 1)
            tracked_modes[os.fsdecode(name)] = metadata.split()[0].decode()
    files = []
    archive = directory / 'payload.tar.gz'
    with tarfile.open(archive, 'w:gz', format=tarfile.PAX_FORMAT) as output:
        for relative in paths:
            source = path / relative
            row = {'path': relative}
            try:
                info = source.lstat()
            except FileNotFoundError:
                row['kind'] = 'deleted'
                files.append(row)
                continue
            row['mode'] = stat.S_IMODE(info.st_mode)
            row['mtimeNs'] = info.st_mtime_ns
            if stat.S_ISDIR(info.st_mode):
                if tracked_modes.get(relative) != '160000':
                    raise RuntimeError(f'Unexpected source directory: {source}')
                row.update(kind='gitlink', head=git(source, 'rev-parse', 'HEAD')
                           .decode().strip())
                files.append(row)
                continue
            member = tarfile.TarInfo('payload/' + relative)
            member.mode = row['mode']
            member.mtime = info.st_mtime
            if stat.S_ISLNK(info.st_mode):
                target = os.readlink(source)
                row.update(kind='symlink', target=target,
                           sha256=digest(os.fsencode(target)))
                member.type = tarfile.SYMTYPE
                member.linkname = target
                output.addfile(member)
            elif stat.S_ISREG(info.st_mode):
                descriptor = os.open(source, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
                with os.fdopen(descriptor, 'rb') as stream:
                    opened = os.fstat(stream.fileno())
                    if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                        raise RuntimeError(f'Source identity changed: {source}')
                    data = stream.read()
                    closed = os.fstat(stream.fileno())
                    if (opened.st_size, opened.st_mtime_ns) != (
                            closed.st_size, closed.st_mtime_ns):
                        raise RuntimeError(f'Source changed while reading: {source}')
                row.update(kind='file', bytes=len(data), sha256=digest(data))
                member.size = len(data)
                output.addfile(member, io.BytesIO(data))
            else:
                raise RuntimeError(f'Unsupported source object: {source}')
            files.append(row)
    (directory / 'index.bin').write_bytes(index_before)
    (directory / 'status.porcelain.z').write_bytes(status_before)
    for name, args in [
        ('working-vs-head.patch', ('diff', '--binary', '--full-index', 'HEAD')),
        ('staged.patch', ('diff', '--cached', '--binary', '--full-index')),
        ('unstaged.patch', ('diff', '--binary', '--full-index')),
    ]:
        (directory / name).write_bytes(git(path, *args, '--', '.',
                                         ':(exclude).reconciliation'))
    if current_status(path) != status_before or source_index(path) != index_before:
        raise RuntimeError(f'Source index/status changed during capture: {path}')
    if git(path, 'rev-parse', 'HEAD').decode().strip() != head:
        raise RuntimeError(f'Source HEAD changed during capture: {path}')
    for row in files:
        source = path / row['path']
        if row['kind'] == 'file' and file_digest(source) != row['sha256']:
            raise RuntimeError(f'Source bytes changed after capture: {source}')
        if row['kind'] == 'symlink' and os.readlink(source) != row['target']:
            raise RuntimeError(f'Source symlink changed after capture: {source}')
        if row['kind'] == 'deleted' and os.path.lexists(source):
            raise RuntimeError(f'Deleted source path reappeared: {source}')
    return {
        'name': tree['name'], 'repository': tree['repository'], 'path': str(path),
        'head': head, 'branch': git(path, 'branch', '--show-current').decode().strip(),
        'directory': str(directory.name), 'indexSha256': digest(index_before),
        'statusSha256': digest(status_before), 'files': files,
    }


def restore_repository(checkpoint, repository, destination):
    """Restore only into a new bare repository, including shallow boundaries."""
    destination = destination.resolve()
    if destination.exists():
        raise RuntimeError(f'Restore destination already exists: {destination}')
    destination.mkdir(parents=True, mode=0o700)
    git(destination, 'init', '--bare', '.')
    git(destination, 'bundle', 'unbundle', str(checkpoint / repository['bundle']))
    if repository.get('shallowFile'):
        (destination / 'shallow').write_bytes(
            (checkpoint / repository['shallowFile']).read_bytes())
    for ref, sha in repository['refs'].items():
        git(destination, 'update-ref', '--no-deref', ref, sha)
    git(destination, 'fsck', '--full', '--no-reflogs')
    for ref, sha in repository['refs'].items():
        if git(destination, 'rev-parse', ref).decode().strip() != sha:
            raise RuntimeError(f'Restored ref mismatch: {ref}')


def verify(checkpoint):
    manifest_path = checkpoint / 'manifest.json'
    manifest_bytes = manifest_path.read_bytes()
    expected = (checkpoint / 'manifest.sha256').read_text().split()[0]
    if digest(manifest_bytes) != expected:
        raise RuntimeError('Checkpoint manifest hash mismatch')
    manifest = json.loads(manifest_bytes)
    for artifact in manifest['artifacts']:
        if file_digest(checkpoint / artifact['path']) != artifact['sha256']:
            raise RuntimeError(f'Checkpoint artifact mismatch: {artifact["path"]}')
    verified_files = 0
    for tree in manifest['trees']:
        wanted = {row['path']: row for row in tree['files']
                  if row['kind'] in {'file', 'symlink'}}
        seen = set()
        with tarfile.open(checkpoint / 'trees' / tree['directory'] / 'payload.tar.gz',
                          'r:gz') as archive:
            for member in archive:
                if not member.name.startswith('payload/'):
                    raise RuntimeError('Unexpected archive member prefix')
                relative = member.name[len('payload/'):]
                if not permitted(relative) or relative not in wanted or relative in seen:
                    raise RuntimeError(f'Unexpected archive member: {relative}')
                seen.add(relative)
                row = wanted[relative]
                if member.mode != row['mode']:
                    raise RuntimeError(f'Archive mode mismatch: {relative}')
                if row['kind'] == 'symlink':
                    if not member.issym() or member.linkname != row['target']:
                        raise RuntimeError(f'Archive symlink mismatch: {relative}')
                elif not member.isfile() or digest(archive.extractfile(member).read()) != row['sha256']:
                    raise RuntimeError(f'Archive content mismatch: {relative}')
                verified_files += 1
        if seen != set(wanted):
            raise RuntimeError(f'Archive misses source paths for {tree["name"]}')
    for repository in manifest['repositories']:
        bundle = checkpoint / repository['bundle']
        git(Path(repository['path']), 'bundle', 'verify', str(bundle))
        actual_refs = dict(line.split(maxsplit=1)[::-1]
                           for line in git(Path(repository['path']), 'bundle',
                                           'list-heads', str(bundle)).decode().splitlines())
        for ref, sha in repository['refs'].items():
            if actual_refs.get(ref) != sha:
                raise RuntimeError(f'Bundle misses original ref {ref}')
        with tempfile.TemporaryDirectory(prefix='atomic-checkpoint-restore-') as scratch:
            restore_repository(checkpoint, repository, Path(scratch) / 'restored.git')
    return {'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'trees': len(manifest['trees']), 'repositories': len(manifest['repositories']),
            'verifiedFileVersions': verified_files,
            'independentRepositoryRestores': len(manifest['repositories']),
            'result': 'verified archives, artifacts, indexes, original refs and independent '
                      'bare restores with full fsck (including original shallow boundaries)'}


def create(inventory_path, checkpoint):
    inventory = json.loads(inventory_path.read_text())
    checkpoint.mkdir(parents=True, exist_ok=False, mode=0o700)
    trees = []
    repositories = []
    for repo in inventory['repositories']:
        trees.append({'name': repo['name'], 'repository': repo['name'],
                      'path': repo['path'],
                      'inventoryPaths': [row['path'] for row in repo['files']]})
        repositories.append({'name': repo['name'], 'path': repo['path']})
    for worker in inventory['workerAudit']['worktrees']:
        trees.append({'name': Path(worker['path']).name, 'repository': worker['repo'],
                      'path': worker['path'],
                      'inventoryPaths': [row['path'] for row in worker['files']]})
    captured = []
    for tree in trees:
        captured.append(capture_tree(tree, checkpoint / 'trees' / tree['name']))
        print(f'Captured {tree["name"]}: {len(captured[-1]["files"])} entries', flush=True)
    (checkpoint / 'bundles').mkdir(mode=0o700)
    for repository in repositories:
        source = Path(repository['path'])
        refs = dict(line.split(maxsplit=1)[::-1]
                    for line in git(source, 'show-ref').decode().splitlines())
        head = git(source, 'rev-parse', 'HEAD').decode().strip()
        refs['HEAD'] = head
        bundle = Path('bundles') / (repository['name'] + '.bundle')
        git(source, 'bundle', 'create', str(checkpoint / bundle), '--all')
        repository.update(bundle=str(bundle), refs=refs)
        shallow_path = Path(os.fsdecode(git(source, 'rev-parse', '--path-format=absolute',
                                             '--git-path', 'shallow')).strip())
        if shallow_path.exists():
            shallow_file = Path('bundles') / (repository['name'] + '.shallow')
            (checkpoint / shallow_file).write_bytes(shallow_path.read_bytes())
            repository['shallowFile'] = str(shallow_file)
            repository['shallowBoundaries'] = shallow_path.read_text().splitlines()
        print(f'Bundled {repository["name"]}: {len(refs)} refs', flush=True)
    (checkpoint / 'source-inventory.json').write_bytes(inventory_path.read_bytes())
    (checkpoint / 'RESTORE.md').write_text(
        '# Atomic source checkpoint\n\n'
        'This is a recovery artifact, not an integration branch or runtime qualification.\n'
        'Do not extract over an existing working tree, installed daemon or user database.\n\n'
        '1. Run the checkpoint script with --verify-existing pointing to this directory.\n'
        '2. Restore the relevant repository into a NEW bare directory using the checkpoint '
        'script: --restore-repository <name> --checkpoint <this-directory> '
        '--destination <new-bare-directory>. Component history is shallow; an ordinary '
        'git clone of the bundle omits the required shallow boundaries. The restore helper '
        'unbundles objects, restores those exact boundaries, restores refs and runs full fsck. '
        'The checkpoint preserves all history available in the original source; it does '
        'not invent history beyond original shallow boundaries.\n'
        '3. For an aggregate or worker version, locate its trees entry in manifest.json '
        'and check out that entry\'s exact head in a separate new working tree.\n'
        '4. Extract its trees/<name>/payload.tar.gz into that new tree, stripping the '
        'single payload/ prefix. Honor symlink/mode metadata. Remove only paths listed '
        'as kind deleted. Gitlink entries record component HEADs; restore components '
        'from their own bundles and payloads separately.\n'
        '5. The captured file payloads are authoritative current bytes, including '
        'untracked and intent-to-add files. The patch files and original index.bin are '
        'supplementary forensic records; do not apply patches a second time after '
        'extracting the payloads. Do not copy index.bin into another checkout.\n'
        '6. Verify restored file SHA-256, modes, links and deletions against manifest.json '
        'before any integration. Compare competing worker implementations rather than '
        'overlaying them onto the aggregate.\n\n'
        'No ignored dependency/build caches, credentials outside inventoried source, '
        'installed binaries or user databases are included.\n'
    )
    artifacts = []
    for path in sorted(checkpoint.rglob('*')):
        if path.is_file():
            artifacts.append({'path': str(path.relative_to(checkpoint)),
                              'bytes': path.stat().st_size, 'sha256': file_digest(path)})
    manifest = {'schemaVersion': 1,
                'capturedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'sourceInventory': str(inventory_path),
                'scope': 'Aggregate root/components plus all six registered workers; '
                         'complete refs and changed source payloads; no source Git mutations.',
                'repositories': repositories, 'trees': captured, 'artifacts': artifacts}
    data = (json.dumps(manifest, indent=2) + '\n').encode()
    (checkpoint / 'manifest.json').write_bytes(data)
    (checkpoint / 'manifest.sha256').write_text(digest(data) + '  manifest.json\n')
    result = verify(checkpoint)
    (checkpoint / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'checkpoint': str(checkpoint), **result}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify-existing', type=Path)
    parser.add_argument('--restore-repository', choices=['monorepo', 'intentd', 'cloudlands-fe'])
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    if args.restore_repository:
        if not args.checkpoint or not args.destination:
            parser.error('--restore-repository requires --checkpoint and --destination')
        checkpoint = args.checkpoint.resolve()
        verify(checkpoint)
        manifest = json.loads((checkpoint / 'manifest.json').read_text())
        repository = next(row for row in manifest['repositories']
                          if row['name'] == args.restore_repository)
        restore_repository(checkpoint, repository, args.destination)
        print(f'Restored {args.restore_repository} into {args.destination.resolve()}')
        return
    if args.verify_existing:
        print(json.dumps(verify(args.verify_existing.resolve()), indent=2))
        return
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = (args.output or ROOT / '.reconciliation/checkpoints' / timestamp).resolve()
    if ROOT.resolve() not in output.parents or '.reconciliation' not in output.parts:
        parser.error('Output must be a new directory under this repository/.reconciliation')
    create(args.inventory.resolve(), output)


if __name__ == '__main__':
    main()
