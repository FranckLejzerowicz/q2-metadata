# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import yaml
import unittest

from q2_metadata.normalization._norm_check_rules import check_rule
from q2_metadata.normalization._norm_errors import (
    ExpectedError,
    OntologyError,
    RemapError,
    ValidationError,
    NormalizationError,
    BlankError,
    MissingError,
    FormatError
)


class UserDefinedExceptions(unittest.TestCase):

    def setUp(self):
        self.values_expected = {
            'is not a list': ['val', 1],
            'not all items are strings': [['val', 1, '1']]
        }
        self.values_ontology = {
            'is not a string': [['Gazetteer_ontology', 'Gazetteer'], 1, {}],
            'none of Gazetteer ontology': ['Gazetteer_ontology', 'Gazetteer']
        }
        self.values_remap = {
            'is not a dictionary': [['val'], 'val', 1],
            'not all dictionary values are strings': [{'a': 1}, {'a': {}}, {'a': []}]
        }

        self.values_validation = {
            'is not a dictionary': [
                ('1', None), (1, None), ([], None)
            ],
            'inacceptable validations': [
                ({'force_to_blank_if': 0, 'other': 0}, 'other'),
                ({'not_accepted': 0}, 'not_accepted'),
                ({'not_accepted': 0, 'not_accepted2': 0}, 'not_accepted, not_accepted2'),
            ],
            'variables not in a list for condition': [
                ({'force_to_blank_if': {'is null': 0}}, 'is null'),
                ({'force_to_blank_if': {'is null': 'a'}}, 'is null'),
                ({'force_to_blank_if': {'is null': {}}}, 'is null')
            ],
            'inacceptable condition': [
                ({'force_to_blank_if': {'not a condition': []}}, 'not a condition')
            ]
        }
        self.values_normalization = {
            'is not a dictionary': ['1', 1, []],
            'impossible normalization terms': [
                {'a': 1},
                {'maximum': 1, 'a': 1},
                {'maximum': 1, 'mininum': 1, 'a': 1},
                {'maximum': 1, 'mininum': 1, 'gated_value': 1, 'a': 1}
            ]
        }
        self.values_blank = []
        self.values_missing = []
        self.values_format = []

    def get_message(self, cur, val):
        reformatted_val = '\t# %s' % yaml.dump(val).replace('\n', '\n\t# ')
        message = 'Wrong formatting for "%s" rule; variable test:\n' \
                  '%s' % (cur, reformatted_val)
        return message

    def test_expected_error(self):
        error_types = ['is not a list', 'not all items are strings']
        for error_type in error_types:
            for eq in self.values_expected[error_type]:
                message = '%s -> %s' % (self.get_message('expected', eq), error_type)
                with self.assertRaises(ExpectedError) as ex:
                    check_rule('test', {}, 'expected', eq)
                self.assertEqual(message, str(ex.exception))

    def test_ontology_error(self):
        error_types = ['is not a string', 'none of Gazetteer ontology']
        for error_type in error_types:
            for eq in self.values_ontology[error_type]:
                message = '%s -> %s' % (self.get_message('ontology', eq), error_type)
                with self.assertRaises(OntologyError) as ex:
                    check_rule('test', {}, 'ontology', eq)
                self.assertEqual(message, str(ex.exception))

    def test_remap_error(self):
        error_types = ['is not a dictionary', 'not all dictionary values are strings']
        for error_type in error_types:
            for eq in self.values_remap[error_type]:
                message = '%s -> %s' % (self.get_message('remap', eq), error_type)
                with self.assertRaises(RemapError) as ex:
                    check_rule('test', {}, 'remap', eq)
                self.assertEqual(message, str(ex.exception))

    def test_validation_error(self):
        error_types = [
            'is not a dictionary',
            'inacceptable validations',
            'variables not in a list for condition',
            'inacceptable condition'
        ]
        for error_type in error_types:
            for (eq, txt) in self.values_validation[error_type]:
                message = '%s -> %s' % (self.get_message('validation', eq), error_type)
                if txt:
                    message = '%s: %s' % (message, txt)
                with self.assertRaises(ValidationError) as ex:
                    check_rule('test', {}, 'validation', eq)
                self.assertEqual(message, str(ex.exception))

    def test_normalization_error(self):
        error_types = ['is not a dictionary', 'impossible normalization terms']
        for error_type in error_types:
            for eq in self.values_normalization[error_type]:
                message = '%s -> %s' % (self.get_message('normalization', eq), error_type)
                if error_type == 'impossible normalization terms':
                    message = '%s: a' % message
                with self.assertRaises(NormalizationError) as ex:
                    check_rule('test', {}, 'normalization', eq)
                self.assertEqual(message, str(ex.exception))

    def test_missing_error(self):
        for eq in self.values_missing:
            message = '%s -> is not a string' % self.get_message('missing', eq)
            with self.assertRaises(MissingError) as ex:
                check_rule('test', {}, 'missing', eq)
            self.assertEqual(message, str(ex.exception))

    def test_blank_error(self):
        for eq in self.values_blank:
            message = '%s -> is not a string' % self.get_message('blank', eq)
            with self.assertRaises(BlankError) as ex:
                check_rule('test', {}, 'blank', eq)
            self.assertEqual(message, str(ex.exception))

    def test_format_error(self):
        for eq in self.values_format:
            message = '%s -> is not a string' % self.get_message('format', eq)
            with self.assertRaises(FormatError) as ex:
                check_rule('test', {}, 'format', eq)
            self.assertEqual(message, str(ex.exception))


if __name__ == '__main__':
    unittest.main()
