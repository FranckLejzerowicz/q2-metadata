# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import numpy as np

from q2_metadata.normalization._norm_rules import RulesCollection


class RulesFormatChecks(unittest.TestCase):

    def setUp(self):

        self.rules_collection = RulesCollection()

        self.rule_not_recognized = ('not_a_rule', '0', 'rule not recognized')
        self.values_expected = {
            'not a list': ['val', 1],
            'not a string': [['val', 1, '1']],
            'ok': [['val', '1'], ['1', '2']]
        }
        self.values_ontology = {
            'not a string': [['Gazetteer_ontology', 'Gazetteer'], 1, {}],
            'not allowed': ['Gazetteer_ontology', 'Gazetteer'],
            'ok': ['Gazetteer ontology']
        }

        self.values_remap = {
            'not a dictionary': [['val'], 'val', 1],
            'not str, int or float': [{('a',1): 1}, {'a': {}}, {'a': []}],
            'ok': [{1: 2}, {'a': 'b'}, {'Yes': 1}]
        }

        self.values_normalization = {
            'not a dictionary': ['1', 1, []],
            'not allowed': [
                {'a': 1},
                {'maximum': 1, 'a': 1},
                {'maximum': 1, 'minimum': 1, 'a': 1},
                {'maximum': 1, 'minimum': 1, 'gated_value': 1, 'a': 1}
            ],
            'not numeric': [
                {'minimum': 'a'},
                {'maximum': 1, 'minimum': 'a'},
                {'maximum': 1, 'minimum': 1, 'gated_value': {}}
            ],
            'ok': [
                {'maximum': 1},
                {'maximum': 1, 'minimum': 1},
                {'maximum': 1, 'minimum': 1, 'gated_value': 1}
            ]
        }

        self.values_validation = {
            'not a dictionary': [
                ('1', None), (1, None), ([], None)
            ],
            'not a nested dictionary': [
                ({'force_to_blank_if': []}, None),
            ],
            'not a list': [
                ({'force_to_blank_if': {'is null': 'a'}}, 0),
                ({'force_to_blank_if': {'is null': {}}}, 1)
            ],
            'not allowed': [
                ({'force_to_blank_if': {'not a condition': []}}, 'not a condition'),
                ({'force_to_blank_if': 0, 'other': 0}, 'other'),
                ({'not_accepted': 0}, 'not_accepted'),
            ],
            'ok': [
                ({'force_to_blank_if': {'is null': []}}, '')
            ]
        }

        self.rules_allowed = {
            'blank': [
                'not applicable',
                'not collected',
                'not provided',
                'restricted access'
            ],
            'missing': [
                'not applicable',
                'not collected',
                'not provided',
                'restricted access'
            ],
            'format': [
                'bool',
                'float',
                'int',
                'str'
            ]
        }

        self.values_str = {
            'blank': {
                'not a string': [0, {}, np.nan],
                'not allowed': ['float64', 'int32', 'anything else'],
                'ok': ['restricted access']
            },
            'missing': {
                'not a string': [0, {}, np.nan],
                'not allowed': ['float64', 'int32', 'anything else'],
                'ok': ['restricted access']
            },
            'format': {
                'not a string': [0, {}, np.nan],
                'not allowed': ['float64', 'int32', 'anything else'],
                'ok': ['str', 'int']
            }
        }

    # to test in ""check_rule()""
    # to test in ""check_rule()""
    # to test in ""check_rule()""
    # def get_message(self, cur, val):
    #     reformatted_val = '\t# %s' % yaml.dump(val).replace('\n', '\n\t# ')
    #     message = 'Wrong formatting for "%s" rule:\n%s' % (cur, reformatted_val)
    #     return message
    #
    # def test_rule_error(self):
        # self.rules_collection.check_rule()
    #     test_rule, test_value, test_message = self.rule_not_recognized
    #     message = '%s -> %s' % (self.get_message(test_rule, test_value), test_message)
    #     with self.assertRaises(RuleError) as ex:
    #         check_rule({}, test_rule, test_value)
    #     self.assertEqual(message, str(ex.exception))

    def test_expected_error(self):
        error_types = ['not a list', 'not a string', 'ok']
        for error_type in error_types:
            for eq in self.values_expected[error_type]:
                error_test = self.rules_collection.check_expected(eq, None)
                if error_type == 'ok':
                    self.assertEqual([], error_test)
                elif error_type == 'not a string':
                    self.assertEqual([error_type, [1]], error_test)
                else:
                    self.assertEqual([error_type], error_test)

    def test_ontology_error(self):
        error_types = ['not a string', 'not allowed', 'ok']
        for error_type in error_types:
            for eq in self.values_ontology[error_type]:
                error_test = self.rules_collection.check_allowed(
                    eq, ['Gazetteer ontology'])
                if error_type == 'ok':
                    self.assertEqual([], error_test)
                elif error_type == 'not allowed':
                    self.assertEqual([error_type, eq], error_test)
                else:
                    self.assertEqual([error_type], error_test)

    def test_remap_error(self):
        error_types = ['not a dictionary', 'not str, int or float', 'ok']
        for error_type in error_types:
            for eq in self.values_remap[error_type]:
                error_test = self.rules_collection.check_remap(
                    eq, None)
                if error_type == 'ok':
                    self.assertEqual([], error_test)
                elif error_type == 'not str, int or float':
                    self.assertEqual(
                        [error_type,
                         ['%s: %s' % (
                             list(eq.keys())[0], list(eq.values())[0]
                         )]], error_test
                    )
                else:
                    self.assertEqual([error_type], error_test)

    def test_validation_error(self):
        error_types = [
            'not a dictionary',
            'not a nested dictionary',
            'not a list',
            'not allowed',
            'ok'
        ]
        for error_type in error_types:
            for (eq, txt) in self.values_validation[error_type]:
                error_test = self.rules_collection.check_validation(
                    eq, {'force_to_blank_if': ['is null']})
                if error_type == 'ok':
                    self.assertEqual([], error_test)
                elif error_type == 'not a dictionary':
                    self.assertEqual([error_type], error_test)
                elif error_type == 'not a nested dictionary':
                    self.assertEqual([error_type], error_test)
                elif error_type == 'not a list':
                    if txt:
                        self.assertEqual([error_type, {}], error_test)
                    else:
                        self.assertEqual([error_type, 'a'], error_test)
                elif error_type == 'not allowed':
                    self.assertEqual([error_type, txt], error_test)

    def test_normalization_error(self):
        error_types = ['not a dictionary', 'not allowed', 'not numeric', 'ok']
        for error_type in error_types:
            for eq in self.values_normalization[error_type]:
                error_test = self.rules_collection.check_normalization(
                    eq, ['maximum', 'minimum', 'gated_value'])
                if error_type == 'ok':
                    self.assertEqual([], error_test)
                elif error_type == 'not numeric':
                    if 'gated_value' in eq:
                        self.assertEqual([error_type, ['gated_value']], error_test)
                    else:
                        self.assertEqual([error_type, ['minimum']], error_test)
                elif error_type == 'not allowed':
                    self.assertEqual([error_type, 'a'], error_test)
                else:
                    self.assertEqual([error_type], error_test)

    def test_allowed_error(self):
        for rule, rule_allowed in self.rules_allowed.items():
            error_types = ['not a string', 'not allowed', 'ok']
            for error_type in error_types:
                for eq in self.values_str[rule][error_type]:
                    error_test = self.rules_collection.check_allowed(
                        eq, rule_allowed)
                    if error_type == 'ok':
                        self.assertEqual([], error_test)
                    elif error_type == 'not allowed':
                        self.assertEqual([error_type, eq], error_test)
                    else:
                        self.assertEqual([error_type], error_test)


if __name__ == '__main__':
    unittest.main()
