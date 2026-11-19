#!/usr/bin/env python3
"""Mutation checks for the Atomic delivery-plan traceability guard."""

from contextlib import redirect_stdout, redirect_stderr
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


PATH = Path(__file__).with_name('check-atomic-delivery-plan.py')
SPEC = importlib.util.spec_from_file_location('atomic_delivery_plan', PATH)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def complete_map(source):
    inventory = checker.inventory(source)
    return {
        'schemaVersion': 1,
        'retainedIds': inventory['retainedIds'],
        'retainedIdSetSha256': inventory['retainedIdSetSha256'],
        'stages': [
            {'id': stage, 'dependsOn': [previous] if previous else []}
            for stage, previous in [('T1', None), ('T2', 'T1'), ('T3', 'T2'),
                                    ('T4', 'T3'), ('T5', 'T4'), ('POST', 'T5')]
        ],
        'items': [dict(id=entry['id'], stage='T5', disposition='preserved',
                       definitionSha256=entry['definitionSha256'], gates=entry['gates'])
                  for entry in inventory['definitions']],
        'protectedBlocks': inventory['protectedBlocks'],
        'firstTracer': {
            'stage': 'T1', 'fullWorkItemsClosed': False,
            'workItems': ['W15', 'W17', 'W19', 'W31', 'W41'],
            'verification': [{'id': 'V4', 'coverage': 'subset'},
                             {'id': 'V36', 'coverage': 'subset'}],
            'tickets': [
                {'id': 'controller', 'workItems': ['W15', 'W17']},
                {'id': 'association', 'workItems': ['W19', 'W41']},
                {'id': 'display', 'workItems': ['W31']},
            ],
        },
    }


class DefinitionParsing(unittest.TestCase):
    def test_references_and_fenced_examples_are_not_definitions(self):
        source = '''## 3. Decisions
| D1 | The real decision | Why | Decided |
```text
| D2 | An example, not a definition | Why | Decided |
- `FAKE-1` This is fenced data.
```
## 12. Delivery
| D1 | A delivery cross-reference, not a second definition |
## 13. Work-item index
| W01 | Host | Build | V1 to V3 green | — | S |
## 14. Assumption register
| A1 | Assumption | Test | Fallback | W01 |
## 15. Verification matrix
| V1 | First | Host |
| V2 | Second | Host |
| V3 | Third | Host |
## 17. Risks and open questions
- **Q1 (before W01):** Open question.
'''
        entries = checker.definitions(source)
        self.assertEqual([entry['id'] for entry in entries],
                         ['D1', 'W01', 'A1', 'V1', 'V2', 'V3', 'Q1'])
        self.assertEqual(entries[1]['gates'], ['V1', 'V2', 'V3'])

    def test_ordered_requirements_keep_nested_content_but_not_next_paragraph(self):
        source = '''## 5. Architecture
1. `CHILD-1` First step.
   Continued obligation.

   | Nested | Requirement |
   | Keep | This |

Separate explanatory paragraph.
2. `CHILD-2` Second step.
'''
        entries = checker.definitions(source)
        self.assertEqual([entry['id'] for entry in entries], ['CHILD-1', 'CHILD-2'])
        self.assertIn('Continued obligation.', entries[0]['definition'])
        self.assertIn('| Keep | This |', entries[0]['definition'])
        self.assertNotIn('Separate explanatory', entries[0]['definition'])

    def test_duplicate_canonical_definition_refuses(self):
        with self.assertRaisesRegex(checker.InvalidPlan, 'duplicate source definition'):
            checker.definitions('## 3. Decisions\n| D1 | One |\n| D1 | Two |\n')

    def test_line_wrapping_does_not_change_preservation_hash(self):
        self.assertEqual(checker.normal_digest('Keep this\n  exact obligation.'),
                         checker.normal_digest('Keep  this exact obligation.'))
        self.assertNotEqual(checker.normal_digest('Keep this exact obligation.'),
                            checker.normal_digest('Drop this exact obligation.'))

    def test_duplicate_json_fields_refuse(self):
        with self.assertRaisesRegex(checker.InvalidPlan, 'duplicate JSON field'):
            checker.load_mapping('{"schemaVersion":1,"schemaVersion":2}')

    def test_frozen_legacy_names_match_the_reviewed_digest(self):
        self.assertEqual(len(checker.legacy_ids()), 361)
        self.assertEqual(checker.id_set_digest(checker.legacy_ids()),
                         checker.RETAINED_ID_SET_SHA256)


class CoverageMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = checker.PLAN.read_text(encoding='utf-8')
        cls.original = complete_map(cls.source)

    def setUp(self):
        self.mapping = copy.deepcopy(self.original)

    def reject(self, pattern, source=None):
        with self.assertRaisesRegex(checker.InvalidPlan, pattern):
            checker.validate(self.source if source is None else source, self.mapping)

    def test_complete_retained_plan_is_mappable_without_claiming_completion(self):
        result = checker.validate(self.source, self.mapping)
        self.assertGreaterEqual(result['definitions'], 361)
        self.assertEqual(result['retained'], 361)
        self.assertGreaterEqual(result['workItems'], 42)
        self.assertEqual(result['firstTracerTickets'], 3)

    def test_missing_item_refuses(self):
        self.mapping['items'] = [item for item in self.mapping['items'] if item['id'] != 'W01']
        self.reject('item coverage mismatch; missing: W01')

    def test_duplicate_item_refuses(self):
        self.mapping['items'].append(copy.deepcopy(self.mapping['items'][0]))
        self.reject('duplicate item id')

    def test_phantom_item_refuses(self):
        item = copy.deepcopy(self.mapping['items'][0]); item['id'] = 'W99'
        self.mapping['items'].append(item)
        self.reject('unknown: W99')

    def test_unknown_stage_or_disposition_refuses(self):
        self.mapping['items'][0]['stage'] = 'unplanned'
        self.reject('unknown stage')
        self.mapping['items'][0]['stage'] = 'T5'
        self.mapping['items'][0]['disposition'] = 'completed-everything'
        self.reject('unknown disposition')

    def test_stage_cycle_refuses(self):
        self.mapping['stages'][0]['dependsOn'] = ['T5']
        self.reject('stage dependency cycle')

    def test_definition_hash_change_refuses(self):
        self.mapping['items'][0]['definitionSha256'] = '0' * 64
        self.reject('definition changed')

    def test_dropped_verification_reference_refuses(self):
        item = next(item for item in self.mapping['items'] if item['gates'])
        item['gates'] = []
        self.reject('lost a referenced verification gate')

    def test_unknown_gate_refuses(self):
        self.mapping['items'][0]['gates'].append('V99')
        self.reject('unknown identifiers: V99')

    def test_unindexed_scope_obligation_change_refuses(self):
        changed = self.source.replace('## 2. Summary',
                                      'A newly changed scope obligation.\n\n## 2. Summary', 1)
        self.reject('protected source obligations changed: scope', changed)

    def test_removing_a_protected_span_refuses(self):
        self.mapping['protectedBlocks'] = [block for block in self.mapping['protectedBlocks']
                                           if block['id'] != 'architecture']
        self.reject('missing or changed protected source span: architecture')

    def test_simultaneous_source_and_map_drop_cannot_change_retained_pin(self):
        changed = '\n'.join(line for line in self.source.splitlines()
                            if not line.startswith('| W01 |'))
        self.mapping['items'] = [item for item in self.mapping['items'] if item['id'] != 'W01']
        self.mapping['retainedIds'].remove('W01')
        self.mapping['retainedIdSetSha256'] = checker.id_set_digest(self.mapping['retainedIds'])
        self.reject('retained legacy identifier set changed', changed)

    def test_new_definition_is_allowed_only_when_mapped_and_legacy_ids_stay(self):
        changed = self.source.replace('## 4. Current state',
                                      '| D20 | Additional decision | Why | Decided |\n\n'
                                      '## 4. Current state', 1)
        extended = complete_map(changed)
        self.assertEqual(extended['retainedIds'], self.mapping['retainedIds'])
        result = checker.validate(changed, extended)
        self.assertEqual(result['definitions'], len(self.mapping['items']) + 1)
        self.reject('missing: D20', changed)

    def test_first_tracer_cannot_close_full_work_items(self):
        self.mapping['firstTracer']['fullWorkItemsClosed'] = True
        self.reject('must not claim full work-item completion')

    def test_first_tracer_cannot_call_a_subset_a_full_verification(self):
        self.mapping['firstTracer']['verification'][0]['coverage'] = 'full'
        self.reject('only named verification subsets')

    def test_active_queue_cannot_expand_to_four_tickets(self):
        self.mapping['firstTracer']['tickets'].append({'id': 'extra', 'workItems': ['W15']})
        self.reject('exactly three tickets')

    def test_ticket_cannot_expand_beyond_the_declared_tracer_slice(self):
        self.mapping['firstTracer']['tickets'][0]['workItems'].append('W37')
        self.reject('unknown identifiers: W37')

    def test_cli_inventory_does_not_require_the_map_to_exist(self):
        out = io.StringIO()
        with redirect_stdout(out):
            result = checker.main(['--inventory', '--map', '/no-map-is-needed-here'])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(out.getvalue())['retainedIdSetSha256'],
                         checker.RETAINED_ID_SET_SHA256)

    def test_cli_failure_has_a_nonzero_exit_and_useful_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad-map.json'
            path.write_text('{bad-json')
            error = io.StringIO()
            with redirect_stderr(error):
                result = checker.main(['--map', str(path)])
            self.assertEqual(result, 1)
            self.assertIn('atomic-delivery-plan:', error.getvalue())

    def test_actual_delivery_map(self):
        if not checker.MAP.is_file():
            self.skipTest('root has not written the delivery map yet')
        result = checker.validate(self.source, checker.load_mapping(checker.MAP.read_text()))
        self.assertGreaterEqual(result['definitions'], 361)


if __name__ == '__main__':
    unittest.main()
