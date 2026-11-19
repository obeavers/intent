#!/usr/bin/env python3
"""Check that delivery resequencing retains every Atomic plan obligation.

This checks traceability, not implementation completion or runtime qualification.
Use --inventory to generate the normalized source definitions and protection pins.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'docs/plans/atomic-substrate-adoption-2026-11-12.md'
MAP = ROOT / 'docs/plans/atomic-substrate-delivery-map.json'
STAGES = {'T1', 'T2', 'T3', 'T4', 'T5', 'POST'}
DISPOSITIONS = {
    'preserved', 'implemented_and_reused', 'integration_required',
    'unimplemented', 'blocked', 'unknown',
}
# The accepted pre-resequencing plan's 361 identifiers, including Q1--Q8.
# New definitions may be added, but deleting old obligations requires an explicit
# reviewed change to this pin as well as the source and delivery map.
RETAINED_ID_SET_SHA256 = 'a86103e40dd697903b7b7c0b3932fe2057dd4aae6eca2273b89fc04bf13cab0a'
LEGACY_COUNTS = {'D': 19, 'W': 42, 'A': 40, 'V': 45, 'Q': 8}
LEGACY_REQUIREMENTS = (
    'HOST:12 MAN:4 OP:5 EXT:3 BASE:4 BAR:4 CHILD:5 SEL:5 REC:11 CMP:7 '
    'REV:3 ADO:5 RWD:2 READ:6 CKP:11 PRJ:6 PUB:6 EXP:3 LAT:13 TASK:4 '
    'INT:10 BIND:5 SET:3 PROV:5 TRI:6 IND:5 EVD:4 CONF:8 KNOW:9 AGT:3 '
    'MEM:6 USE:4 OUT:5 SKL:5 STORE:6 SAFE:4'
)
PROTECTED_SPANS = [
    ('scope', '## 1. Goal and scope', '## 2. Summary'),
    ('existing-contracts', '### 4.1 Contracts that stay binding',
     '### 4.2 What exists in Intent, and what does not'),
    ('architecture', '## 5. Architecture: repository mechanics', '## 12. Delivery'),
    ('failure-recovery', '## 16. Failure and recovery matrix',
     '## 17. Risks and open questions'),
    ('pilot-retirement', '**Pilot scenario.**', '## 13. Work-item index'),
]
NAMED = re.compile(r'^(?:- |\d+\. )`([A-Z][A-Z0-9]*-\d+)`')
QUESTION = re.compile(r'^- \*\*(Q\d+)\b')
ROW = re.compile(r'^\|\s*((?:D|A|V)\d+|W\d{2})\s*\|')
SECTION_FAMILY = {'3': 'D', '13': 'W', '14': 'A', '15': 'V'}


class InvalidPlan(ValueError):
    """The plan or map cannot establish complete traceability."""


def normal_digest(text):
    """Line wrapping/indentation are irrelevant; requirement words remain pinned."""
    return hashlib.sha256(' '.join(text.split()).encode()).hexdigest()


def id_set_digest(identifiers):
    return hashlib.sha256('\n'.join(sorted(identifiers)).encode()).hexdigest()


def legacy_ids():
    result = {f'{family}{number:02}' if family == 'W' else f'{family}{number}'
              for family, count in LEGACY_COUNTS.items() for number in range(1, count + 1)}
    for entry in LEGACY_REQUIREMENTS.split():
        prefix, count = entry.split(':')
        result.update(f'{prefix}-{number}' for number in range(1, int(count) + 1))
    return sorted(result)


def verification_refs(text):
    result = set()
    pattern = r'\bV(\d+)(?:\s*(?:to|through|[–—-])\s*V?(\d+))?\b'
    for match in re.finditer(pattern, text):
        low = int(match[1])
        high = int(match[2]) if match[2] else low
        if high < low or high - low > 1000:
            raise InvalidPlan('invalid verification range: ' + match[0])
        result.update('V' + str(number) for number in range(low, high + 1))
    return sorted(result, key=lambda value: int(value[1:]))


def definitions(text):
    """Read definitions, not references in delivery tables or fenced examples."""
    lines = text.splitlines()
    found = []
    seen = set()
    section = None
    fence = None
    for index, line in enumerate(lines):
        fenced = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fenced:
            marker = fenced[1][0]
            fence = None if fence == marker else marker
            continue
        if fence:
            continue
        heading = re.match(r'^## (\d+)\.', line)
        if heading:
            section = heading[1]
        match = ROW.match(line)
        named = NAMED.match(line)
        question = QUESTION.match(line) if section == '17' else None
        family = None
        end = index + 1
        if match and SECTION_FAMILY.get(section) == match[1][0]:
            identifier = match[1]
            family = identifier[0]
        elif named or question:
            identifier = (named or question)[1]
            family = 'requirement' if named else 'Q'
            # Named list items can own indented paragraphs, nested lists/tables
            # and blank lines. The next unindented block is not their content.
            while end < len(lines) and (not lines[end].strip() or lines[end][0].isspace()):
                end += 1
        if family is None:
            continue
        if identifier in seen:
            raise InvalidPlan('duplicate source definition: ' + identifier)
        seen.add(identifier)
        definition = '\n'.join(lines[index:end]).rstrip()
        found.append({
            'id': identifier, 'family': family, 'line': index + 1,
            'definition': definition, 'definitionSha256': normal_digest(definition),
            'gates': verification_refs(definition),
        })
    if not found:
        raise InvalidPlan('no canonical plan definitions found')
    return found


def protected_text(text, start, end):
    if not isinstance(start, str) or not isinstance(end, str) or not start or not end:
        raise InvalidPlan('protection markers must be nonempty strings')
    if text.count(start) != 1 or text.count(end) != 1:
        raise InvalidPlan('protection markers must each occur exactly once: ' + start)
    first = text.index(start)
    last = text.index(end)
    if first >= last:
        raise InvalidPlan('protection markers are reversed: ' + start)
    return text[first:last]


def inventory(text):
    entries = definitions(text)
    identifiers = legacy_ids()
    blocks = [dict(id=name, start=start, end=end,
                   sha256=normal_digest(protected_text(text, start, end)))
              for name, start, end in PROTECTED_SPANS]
    return {
        'schemaVersion': 1, 'definitions': entries,
        'counts': dict(sorted(Counter(entry['family'] for entry in entries).items())),
        'retainedIds': identifiers, 'retainedIdSetSha256': id_set_digest(identifiers),
        'protectedBlocks': blocks,
    }


def objects_by_id(values, name):
    if not isinstance(values, list):
        raise InvalidPlan(name + ' must be a list')
    result = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get('id'), str) or not value['id']:
            raise InvalidPlan(name + ' entries must have a nonempty id')
        if value['id'] in result:
            raise InvalidPlan('duplicate ' + name + ' id: ' + value['id'])
        result[value['id']] = value
    return result


def unique_refs(values, allowed, name, nonempty=False):
    if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
        raise InvalidPlan(name + ' must be a list of identifiers')
    if len(set(values)) != len(values):
        raise InvalidPlan(name + ' contains duplicate identifiers')
    unknown = set(values) - set(allowed)
    if unknown:
        raise InvalidPlan(name + ' has unknown identifiers: ' + ', '.join(sorted(unknown)))
    if nonempty and not values:
        raise InvalidPlan(name + ' must not be empty')
    return set(values)


def load_mapping(text):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InvalidPlan('duplicate JSON field: ' + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique_keys)


def validate(text, mapping):
    if (not isinstance(mapping, dict) or type(mapping.get('schemaVersion')) is not int
            or mapping.get('schemaVersion') != 1):
        raise InvalidPlan('delivery map schemaVersion must be 1')
    source = {entry['id']: entry for entry in definitions(text)}
    retained = unique_refs(mapping.get('retainedIds'), source, 'retainedIds', True)
    if (mapping.get('retainedIdSetSha256') != RETAINED_ID_SET_SHA256
            or id_set_digest(retained) != RETAINED_ID_SET_SHA256):
        raise InvalidPlan('retained legacy identifier set changed; review the frozen ID pin')
    stages = objects_by_id(mapping.get('stages'), 'stage')
    if set(stages) != STAGES:
        raise InvalidPlan('stages must be exactly T1, T2, T3, T4, T5 and POST')
    dependencies = {}
    for identifier, stage in stages.items():
        dependencies[identifier] = unique_refs(stage.get('dependsOn', []), stages,
                                               identifier + '.dependsOn')
    visiting, visited = set(), set()

    def visit(identifier):
        if identifier in visiting:
            raise InvalidPlan('stage dependency cycle at ' + identifier)
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in dependencies[identifier]:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in stages:
        visit(identifier)
    items = objects_by_id(mapping.get('items'), 'item')
    missing, phantom = set(source) - set(items), set(items) - set(source)
    if missing or phantom:
        raise InvalidPlan('item coverage mismatch; missing: ' + ', '.join(sorted(missing))
                          + '; unknown: ' + ', '.join(sorted(phantom)))
    known_gates = {identifier for identifier in source if source[identifier]['family'] == 'V'}
    for identifier, item in items.items():
        if item.get('stage') not in stages:
            raise InvalidPlan(identifier + ' has an unknown stage')
        if item.get('disposition') not in DISPOSITIONS:
            raise InvalidPlan(identifier + ' has an unknown disposition')
        if item.get('definitionSha256') != source[identifier]['definitionSha256']:
            raise InvalidPlan(identifier + ' definition changed or its preservation hash is stale')
        gates = unique_refs(item.get('gates'), known_gates, identifier + '.gates')
        if not set(source[identifier]['gates']) <= gates:
            raise InvalidPlan(identifier + ' lost a referenced verification gate')
    blocks = objects_by_id(mapping.get('protectedBlocks'), 'protected block')
    for name, start, end in PROTECTED_SPANS:
        block = blocks.get(name)
        if not block or block.get('start') != start or block.get('end') != end:
            raise InvalidPlan('missing or changed protected source span: ' + name)
    for name, block in blocks.items():
        actual = normal_digest(protected_text(text, block.get('start'), block.get('end')))
        if block.get('sha256') != actual:
            raise InvalidPlan('protected source obligations changed: ' + name)
    tracer = mapping.get('firstTracer')
    if not isinstance(tracer, dict) or tracer.get('stage') != 'T1':
        raise InvalidPlan('firstTracer must be scoped to T1')
    if tracer.get('fullWorkItemsClosed') is not False:
        raise InvalidPlan('a first-tracer subset must not claim full work-item completion')
    known_work = {identifier for identifier in source if source[identifier]['family'] == 'W'}
    work = unique_refs(tracer.get('workItems'), known_work, 'firstTracer.workItems', True)
    coverage = objects_by_id(tracer.get('verification'), 'first-tracer verification')
    if not coverage:
        raise InvalidPlan('firstTracer must name its scoped verification subsets')
    for identifier, case in coverage.items():
        if identifier not in known_gates or case.get('coverage') != 'subset':
            raise InvalidPlan('first tracer may claim only named verification subsets: ' + identifier)
    tickets = objects_by_id(tracer.get('tickets'), 'first-tracer ticket')
    if len(tickets) != 3:
        raise InvalidPlan('the active first-tracer queue must contain exactly three tickets')
    for identifier, ticket in tickets.items():
        unique_refs(ticket.get('workItems'), work, identifier + '.workItems', True)
    return dict(definitions=len(source), retained=len(retained), stages=len(stages),
                workItems=len(known_work), verificationCases=len(known_gates),
                firstTracerTickets=len(tickets))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=PLAN)
    parser.add_argument('--map', type=Path, default=MAP)
    parser.add_argument('--inventory', action='store_true')
    args = parser.parse_args(argv)
    try:
        text = args.plan.read_text(encoding='utf-8')
        if args.inventory:
            print(json.dumps(inventory(text), indent=2))
            return 0
        result = validate(text, load_mapping(args.map.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError) as error:
        print('atomic-delivery-plan: ' + str(error), file=sys.stderr)
        return 1
    print('atomic-delivery-plan: {definitions} definitions retained and mapped; '
          '{workItems} work items, {verificationCases} verification cases, '
          '{stages} milestones, {firstTracerTickets} active tracer tickets; '
          'no implementation completion inferred'.format(**result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
