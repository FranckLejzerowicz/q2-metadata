# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_metadata.normalization._norm_check_rules import (
    check_expected,
    check_ontology,
    check_remap,
    check_validation,
    check_normalization,
    check_str
)
import unittest


class RuleFormatCheck(unittest.TestCase):

    def setUp(self):
        self.values_expected = {
            0: [['val', 1, '1'], 'val', 1],
            1: [['val'], ['1', '2']]
        }
        self.values_ontology = {
            0: [['Gazetteer_ontology', 'Gazetteer'], 'Gazetteer_ontology', 'Gazetteer', 1, {}],
            1: ['Gazetteer ontology']
        }
        self.values_remap = {
            0: [['val'], 'val', 1, {'a': 1}, {'a': {}}, {'a': []}],
            1: [{1: 'a'}, {'a': 'b'}]
        }
        self.values_validation = {
            0: [
                '1', 1, [], {'not_accepted': 0},
                {'force_to_blank_if': 0, 'other': 0},
                {'force_to_blank_if': {'is null': 0}},  # nested "0" should be list
                {'force_to_blank_if': {'is null': 'a'}}, # nested "a" should be list
                {'force_to_blank_if': {'is null': {}}}, # nested "{}" should be list
                {'force_to_blank_if': {'no a condition': []}},
            ],
            1: [
                {'force_to_blank_if': {'is null': []}}
            ]
        }
        self.values_normalization = {
            0: [
                '1', 1, [],
                {'a': 1},
                {'maximum': 1, 'a': 1},
                {'maximum': 1, 'mininum': 1, 'a': 1},
                {'maximum': 1, 'mininum': 1, 'gated_value': 1, 'a': 1}
            ],
            1: [
                {'maximum': 1},
                {'maximum': 1, 'mininum': 1},
                {'maximum': 1, 'mininum': 1, 'gated_value': 1}
            ]
        }
        self.values_str = {
            0: [['a'], {'a': 1}, ('a',)],
            1: ['a', '1']
        }

    def test_check_expected(self):
        # not equal
        for eq in self.values_expected[0]:
            self.assertFalse(check_expected(eq))
        # equal
        for eq in self.values_expected[1]:
            self.assertTrue(check_expected(eq))

    def test_check_ontology(self):
        # not equal
        for eq in self.values_ontology[0]:
            self.assertFalse(check_ontology(eq))
        # equal
        for eq in self.values_ontology[1]:
            self.assertTrue(check_ontology(eq))

    def test_check_remap(self):
        # not equal
        for eq in self.values_remap[0]:
            self.assertFalse(check_remap(eq))
        # equal
        for eq in self.values_remap[1]:
            self.assertTrue(check_remap(eq))

    def test_check_validation(self):
        # not equal
        for eq in self.values_validation[0]:
            self.assertFalse(check_validation(eq))
        # equal
        for eq in self.values_validation[1]:
            self.assertTrue(check_validation(eq))

    def test_check_normalization(self):
        # not equal
        for eq in self.values_normalization[0]:
            self.assertFalse(check_normalization(eq))
        # equal
        for eq in self.values_normalization[1]:
            self.assertTrue(check_normalization(eq))

    def test_check_str(self):
        # not equal
        for eq in self.values_str[0]:
            self.assertFalse(check_str(eq))
        # equal
        for eq in self.values_str[1]:
            self.assertTrue(check_str(eq))


if __name__ == '__main__':
    unittest.main()
