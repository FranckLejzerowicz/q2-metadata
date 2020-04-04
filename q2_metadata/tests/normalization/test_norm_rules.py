# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import glob
import unittest
import pkg_resources
from q2_metadata.normalization._norm_rules import RulesCollection, Rules
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


ROOT = pkg_resources.resource_filename('q2_metadata', 'tests/normalization/rules')


class RulesCollectionInputTests(unittest.TestCase):

    def setUp(self):

        # directory containing the rules files that are either:
        #  - correctly formatted    "_0.yml" version
        #  - incorrectly formatted  "_1.yml" and "_2.yml" versions
        self.raisers_dir = '%s/rules_errors/raisers' % ROOT

        # in this directory the rule are names as if the variables names
        # were the error type name (for convenience in unittesting here).
        self.blank_rad = '%s/BlankError/BlankError' % self.raisers_dir
        self.expected_rad = '%s/ExpectedError/ExpectedError' % self.raisers_dir
        self.format_rad = '%s/FormatError/FormatError' % self.raisers_dir
        self.missing_rad = '%s/MissingError/MissingError' % self.raisers_dir
        self.normalization_rad = '%s/NormalizationError/NormalizationError' % self.raisers_dir
        self.ontology_rad = '%s/OntologyError/OntologyError' % self.raisers_dir
        self.remap_rad = '%s/RemapError/RemapError' % self.raisers_dir
        self.validation_rad = '%s/ValidationError/ValidationError' % self.raisers_dir
        # --> for each there are 3 files, e.g. for `self.blank_rad`:
        #  (1) '%s_0.yml' % self.blank_rad    --> will NOT raise error
        #  (2) '%s_1.yml' % self.blank_rad    --> will raise error
        #  (3) '%s_2.yml' % self.blank_rad    --> will raise error

    def test_blank_formatting(self):

        # testing instance
        rule_structure_key = 'allowed'
        cur_rule = 'blank'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.blank_rad))

        # no error raised
        rules_collection.check_variables_rules(['BlankError_0'])
        rule = rules_collection.variables_rules['BlankError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule], 'Not applicable')

        # error raised 1
        with self.assertRaises(BlankError):
            rules_collection.check_variables_rules(['BlankError_1'])

        # error raised 2
        with self.assertRaises(BlankError):
            rules_collection.check_variables_rules(['BlankError_2'])

    def test_expected_formatting(self):
        # testing instance
        rule_structure_key = 'lookups'
        cur_rule = 'expected'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.expected_rad))

        # no error raised
        rules_collection.check_variables_rules(['ExpectedError_0'])
        rule = rules_collection.variables_rules['ExpectedError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule], ['A', 'B'])

        # error raised 1
        with self.assertRaises(ExpectedError):
            rules_collection.check_variables_rules(['ExpectedError_1'])

        # error raised 2
        with self.assertRaises(ExpectedError):
            rules_collection.check_variables_rules(['ExpectedError_2'])

    def test_format_formatting(self):

        # testing instance
        rule_structure_key = 'format'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.format_rad))

        # no error raised
        rules_collection.check_variables_rules(['FormatError_0'])
        rule = rules_collection.variables_rules['FormatError_0'].rules
        self.assertEqual(rule[rule_structure_key], 'int')

        # error raised 1
        with self.assertRaises(FormatError):
            rules_collection.check_variables_rules(['FormatError_1'])

        # error raised 2
        with self.assertRaises(FormatError):
            rules_collection.check_variables_rules(['FormatError_2'])

    def test_missing_formatting(self):
        # testing instance
        rule_structure_key = 'allowed'
        cur_rule = 'missing'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.missing_rad))

        # no error raised
        rules_collection.check_variables_rules(['MissingError_0'])
        rule = rules_collection.variables_rules['MissingError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule], 'Not provided')

        # error raised 1
        with self.assertRaises(MissingError):
            rules_collection.check_variables_rules(['MissingError_1'])

        # error raised 2
        with self.assertRaises(MissingError):
            rules_collection.check_variables_rules(['MissingError_2'])

    def test_normalization_formatting(self):
        # testing instance
        rule_structure_key = 'edits'
        cur_rule = 'normalization'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.normalization_rad))

        # no error raised
        rules_collection.check_variables_rules(['NormalizationError_0'])
        rule = rules_collection.variables_rules['NormalizationError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule],
                         {'gated_value': 'Out of bounds',
                          'maximum': 120, 'minimum': 0})

        # error raised 1
        with self.assertRaises(NormalizationError):
            rules_collection.check_variables_rules(['NormalizationError_1'])

        # error raised 2
        with self.assertRaises(NormalizationError):
            rules_collection.check_variables_rules(['NormalizationError_2'])

    def test_ontology_formatting(self):
        # testing instance
        rule_structure_key = 'lookups'
        cur_rule = 'ontology'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.ontology_rad))

        # no error raised
        rules_collection.check_variables_rules(['OntologyError_0'])
        rule = rules_collection.variables_rules['OntologyError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule], 'Gazetteer ontology')

        # error raised 1
        with self.assertRaises(OntologyError):
            rules_collection.check_variables_rules(['OntologyError_1'])

        # error raised 2
        with self.assertRaises(OntologyError):
            rules_collection.check_variables_rules(['OntologyError_2'])

    def test_remap_formatting(self):
        # testing instance
        rule_structure_key = 'edits'
        cur_rule = 'remap'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.remap_rad))

        # no error raised
        rules_collection.check_variables_rules(['RemapError_0'])
        rule = rules_collection.variables_rules['RemapError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule], {'USA': 'US'})

        # error raised 1
        with self.assertRaises(RemapError):
            rules_collection.check_variables_rules(['RemapError_1'])

        # error raised 2
        with self.assertRaises(RemapError):
            rules_collection.check_variables_rules(['RemapError_2'])

    def test_validation_formatting(self):
        # testing instance
        rule_structure_key = 'edits'
        cur_rule = 'validation'
        rules_collection = RulesCollection()
        rules_collection.parse_variables_rules(glob.glob('%s*yml' % self.validation_rad))

        # no error raised
        rules_collection.check_variables_rules(['ValidationError_0'])
        rule = rules_collection.variables_rules['ValidationError_0'].rules
        self.assertEqual(rule[rule_structure_key][cur_rule],
                         {'force_to_blank_if': {'is null': ['host_taxid']}})

        # error raised 1
        with self.assertRaises(ValidationError):
            rules_collection.check_variables_rules(['ValidationError_1'])

        # error raised 2
        with self.assertRaises(ValidationError):
            rules_collection.check_variables_rules(['ValidationError_2'])

        # extra error raised 3
        with self.assertRaises(ValidationError):
            rules_collection.check_variables_rules(['ValidationError_3'])


class RulesCollectionClassTests(unittest.TestCase):

    def setUp(self):

        self.rules_template = {
            'edits': {
                'remap': {},
                'normalization': {},
                'validation': {}
            },
            'lookups': {
                'ontology': None,
                'expected': []
            },
            'allowed': {
                'blank': None,
                'missing': None
            },
            'format': None
        }

        # testing instance
        self.rules_collection = RulesCollection()

        # error yaml files directories
        self.no_dir = '%s/rules_collection_errors/none' % ROOT
        self.empty = '%s/rules_collection_errors/empty' % ROOT
        self.no_yml = '%s/rules_collection_errors/no_yml' % ROOT

        # ok yaml files directory
        self.ok_dir = '%s/rules_collection_errors/ok' % ROOT
        self.files = ['%s/%s.yml' % (self.ok_dir, x) for x in ['A', 'B']]
        self.rules = {
            'A': self.rules_template.copy(),
            'B': self.rules_template.copy(),
        }

    def test_check_variables_rules_dir(self):

        with self.assertRaises(IOError) as ex:
            self.rules_collection._check_variables_rules_dir(self.no_dir)
        self.assertEqual("Input directory %s does not exist" % self.no_dir, str(ex.exception))

        with self.assertRaises(IOError) as ex:
            self.rules_collection._check_variables_rules_dir(self.empty)
        self.assertEqual("Input directory %s empty" % self.empty, str(ex.exception))

        with self.assertRaises(IOError) as ex:
            self.rules_collection._check_variables_rules_dir(self.no_yml)
        self.assertEqual("Input directory %s empty" % self.no_yml, str(ex.exception))

        content = self.rules_collection._check_variables_rules_dir(self.ok_dir)
        self.assertEqual(sorted(content), self.files)

    def test_parse_variables_rules(self):

        self.rules_collection.parse_variables_rules(self.files)
        for variable, variable_rules in self.rules_collection.variables_rules.items():
            self.assertEqual(variable_rules.parsed_rules, {'format': 'str'})


class RulesClassTests(unittest.TestCase):

    def setUp(self):

        self.rules_dir = '%s/rules_errors' % ROOT
        self.not_yml = '%s/not_yml' % self.rules_dir
        # these two well-formatted, dummy rules contain the following info
        self.simple_ok = '%s/ok/simple.yml' % self.rules_dir
        self.all_ok = '%s/ok/all_ok.yml' % self.rules_dir
        self.rules = {
            'edits': {
                'remap': {},
                'normalization': {},
                'validation': {}
            },
            'lookups': {
                'ontology': None,
                'expected': []
            },
            'allowed': {
                'blank': None,
                'missing': None
            },
            'format': None
        }
        self.default_rules = {
            'edits': {
                'remap': {'USA': 'US'},
                'normalization': {
                    'gated_value': 'Out of bounds',
                    'maximum': 120,
                    'minimum': 0
                },
                'validation': {
                     'force_to_blank_if': {'is null': ['host_taxid']}
                }
            },
            'lookups': {
                'ontology': 'Gazetteer ontology',
                'expected': [
                    'I do not have this condition',
                    'Self-diagnosed',
                    'Diagnosed by a medical professional (doctor, physician assistant)',
                    'Diagnosed by an alternative medicine practitioner'
                ]
            },
            'allowed': {
                'blank': 'Not applicable',
                'missing': 'Not provided'
            },
            'format': 'str'
        }

    def test_rules_instantiation(self):

        rules = Rules(self.all_ok)
        self.assertEqual(rules.parsed_rules, self.default_rules)

    def test_parse_rule(self):

        with self.assertRaises(IOError) as ex:
            Rules.parse_rule('%s/A.yml.gz' % self.not_yml)
        self.assertEqual("Something is wrong with the .yml rule file.", str(ex.exception))

        with self.assertRaises(IOError) as ex:
            Rules.parse_rule('%s/B.yml' % self.not_yml)
        self.assertEqual("Something is wrong with the .yml rule file.", str(ex.exception))

        test_yaml_parsed = Rules.parse_rule(self.simple_ok)
        self.assertEqual(test_yaml_parsed, {'format': 'str'})


if __name__ == '__main__':
    unittest.main()
