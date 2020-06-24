# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""This module contain the main classes for the metadata normalization
plugin in QIIME2.

Glossary:
    variable        :   Name of a metadata variable supposed to occur in
                        the metadata table header.
    variable_rules  :   Set of rules associated with a variable and described
                        in the per-variable .yml files.
    rules           :   collection of all the rules that will apply on all
                        variables. The rules are parsed, checked and collected
                        into this structured object before being applied.
    rule            :   One rule that is one of "expected", "ontology",
                        "remap", "validation", "normalization", "blank",
                        "missing" or "format". Each of these rules has a
                        `rule_value` in a specific format, which is checked
                        using static methods in class RulesCollection().

Rules formatting (.yml files):
    remap           :   Map the variables values by replacing all instances
                        of a given value by another one value.
        Example:
            ```
            remap:
              US: USA
            ```
    validation      :   Validate the variables values by replacing by the
                        missing value every sample entry that for the current
                        variable has in one or multiple other variable(s) a
                        null or missing value for that sample.
        Example:
            ```
            validation:
              force_to_blank_if:
                is null:
                - variable
            ```
    normalization   :   Normalize the variables values by replacing the values
                        outside the a range by a given replacement value.
        Example:
            ```
            normalization:
                gated_value: nan
                maximum: 100
                minimum: 10
            ```
    missing         :   Check that missing values are one of the terms reserved
                        for this instance.
        Example:
            ```
            missing:
                - not applicable
                - not collected
                - not provided
                - restricted access
            ```
    format          :   Check that the passed column is in the correct format.
        Example:
            ```
            format:
              - bool
              - float
              - int
              - str
            ```

    expected        :   Check that the variable values are one of the passed
                        expected values (or the missing and blanks).
        Example:
            ```
            expected:
                - "Yes"
                - "No"
            ```
    ontology        :   Name of the ontology to look up for control vocabulary.
        Example:
            ```
            ontology: Gazetteer
            ```
    blank           :   Check that blank values are one of the terms reserved
                        for this instance.
        Example:
            ```
            missing:
                - not applicable
                - not collected
                - not provided
                - restricted access
            ```
"""

import pkg_resources
from glob import glob
import pandas as pd
from os.path import basename, isdir, splitext

from q2_metadata.normalization._norm_utils import read_yaml_file
from q2_metadata.normalization._norm_errors import RuleFormatError

FORMAT = pkg_resources.resource_filename("q2_metadata", "")


class Rules(object):
    """Collect the rules of one current variable.

    Parameters
    ----------
    variable_rules_fp : str
        Path to one variable's rules yaml file.

    Attributes
    ----------
    rules: dict
        Checked rules in a hard-coded data structure that
        has common default values for all variables and
        that is then updated based on the parsed rules.

    Methods
    -------
    parse_rule : staticmethod
        Performs the parsing of the current variable's yml file and
        returns the rules (values) in `self.variables_rules`.
    normalize
        Perform the application of the variables' rules.

    Raises
    ------
    IOError : yaml.YAMLError
        If something went wrong with reading the .yml rule file.
    """
    def __init__(self, variable_rules_fp: str):
        """Initialize the class instance for the set of rules associated
        with a single metadata variable. The instantiated class will be
        given a `variable` attribute corresponding to the variable name
        as string, as well as a `rules` attribute collecting the actual
        rules in a dictionary.

        Parameters
        ----------
        variable_rules_fp : str
            Path to one variable's rules yaml file.
        """
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
                'missing': None,
                'format': None
            }

        }
        self.parsed_rules = self.parse_rule(variable_rules_fp)

    @staticmethod
    def parse_rule(variable_rules_fp: str):
        """Read the yaml file of the current variable's rules.

        Parameters
        ----------
        variable_rules_fp : str
            Path to one variable's rules yaml file.

        Returns
        -------
        parsed_rules : dict
            Parsed variable's rules.
        """
        return read_yaml_file(variable_rules_fp)

    def normalize(self, variable: str, input_column: pd.Series) -> pd.Series:
        """Apply the rules of the metadata table.

        Dispatch the metadata column to be curated to
        the functions that will be applied to properly process
        the current variable according to the current set of
        rules for it.

        Parameters
        ----------
        variable : str
            Name of the variable which rules are parsed and
            that is the yaml file name without the .yml extension.
        input_column : pd.Series
            Metadata column to be curated (that may already got
            through this function).

        Returns
        -------
        output_column : pd.Series
            Curated (or being curated) metadata column.
        """
        pass


class RulesCollection(object):
    """Collect all the rules for all the variables.

    Attributes
    ----------
    variables_rules : dict
        for each variable (keys) leads to an
        instance of the `Rules()` class (values).
    rules_format_error : list
        rules_allowed_fp = '%s/normalization/assets/rules_allowed.yml' % FORMAT
    self.rules_allowed = read_yaml_file(rules_allowed_fp)


    Methods
    -------
    check_variables_rules_dir
        Performs checks on rules paths input. Either raise Exceptions,
        or return the list `variables_rules_files` containing the paths
        to the existing yml rules files.
    parse_variables_rules
        Parse the yml rules files, one variable at a time and returns the
        dict `variables_rules` that for each variable (keys) leads to an
        instance of the `Rules()` class. This class performs rule-formatting
        checks and fills a rules dict structure.
    check_variables_rules
        Loops over each variable and its rules and check that these are
        well formatted. Fills `rules` attribute with well formatted rules,
        or collect the encountered formatiing issues in `rules_format_error`.

    Raises
    ------
    IOError
        If directory to process does not exist.
    FileNotFoundError
        If directory to process contains no .yml file.
    """

    def __init__(self) -> None:
        """Initialize the class instance for the collection of the set
        of rules associated with all the metadata variables.
        The instantiated class will be given a `variable` attribute
        corresponding to the variable name as string, as well as a
        `rules` attribute collecting the actual rules in a dictionary.
        """
        self.variables_rules = {}
        self.rules_format_error = RuleFormatError()
        rules_allowed_fp = '%s/normalization/assets/rules_allowed.yml' % FORMAT
        self.rules_allowed = read_yaml_file(rules_allowed_fp)

    @staticmethod
    def check_variables_rules_dir(variables_rules_dir: str) -> list:
        """Checks paths validity for the rules files.

        Checks that the yaml rules directory exists
        and that it contains yml files. If yes, returns
        the files in a list.

        Parameters
        ----------
        variables_rules_dir : str
            Path to the folder containing the variables rules in yaml.

        Returns
        -------
        variables_rules_files : list
            Paths to the yaml rules files.
        """
        if not isdir(variables_rules_dir):
            raise IOError("Input directory %s does not exist" % variables_rules_dir)
        variables_rules_files = glob('%s/*.yml' % variables_rules_dir)
        if not variables_rules_files:
            raise IOError("Input directory %s empty" % variables_rules_dir)
        return variables_rules_files

    def parse_variables_rules(self, variables_rules_files: list) -> None:
        """Initialize rules structure for each variable.

        Parse the variables yaml rules files one by one.
        At this point, the attribute `variables_rules` will
        have for each variable (keys), an instance of the
        Rules() class (values), initiated with an empty default data
        structure `rules` and the yet unchecked `parsed_rules`.

        Parameters
        ----------
        variables_rules_files : list
            Paths to the yaml rules files.
        """
        for variable_rules_fp in variables_rules_files:
            # get the file name (should correspond to a variable name)
            variable = splitext(basename(variable_rules_fp))[0]
            # instantiate Rules() class to get variable's yaml rules
            self.variables_rules[variable] = Rules(variable_rules_fp)

    def check_variables_rules(self, focus: list) -> None:
        """Collect the properly-formatted rules.

        This method fills the rules attribute with the correctly
        formatted rules for the current variable, or raise user-
        defined exception.

        Parameters
        ----------
        focus : list
            Metadata variables that have rules.
        """
        for variable in focus:
            variable_rules = self.variables_rules[variable]
            for rule, rule_value in variable_rules.parsed_rules.items():
                self.check_rule(variable, rule, rule_value)

    def check_rule(self, variable: str, rule: str, rule_value) -> None:
        """For each rule in the current variable's rules set,
        perform checks that the rule values to be used for the rules
        to apply are properly formatted. The properly formatted rules
        are collected in the `Rules.rules` dictionary structure that
        is the same of all variables, otherwise, a user-defined error
        specific to each rule is raised.

        Parameters
        ----------
        variable : str
            Name of the metadata variable for which there is rules.
        rule : str
            Current rule name. Could be one of "expected", "ontology",
            "remap", "validation", "normalization", "blank", "missing",
            "format".
        rule_value : str, list or dict
            Parsed rule value for the current rule.

        Returns
        -------
        rule_format_error : list
            Issues encountered when checking the rules.
        """

        rule_type_map = {
            'normalization': (self.check_normalization, 'edits'),
            'validation': (self.check_validation, 'edits'),
            'remap': (self.check_remap, 'edits'),
            'expected': (self.check_expected, 'lookups'),
            'ontology': (self.check_allowed, 'lookups'),
            'blank': (self.check_allowed, 'allowed'),
            'missing': (self.check_allowed, 'allowed'),
            'format': (self.check_allowed, 'allowed')
        }
        if rule in rule_type_map:
            rule_method, rule_type = rule_type_map[rule]
            error = rule_method(rule_value, self.rules_allowed[rule])
            if not len(error):
                self.variables_rules[
                    variable].rules[rule_type][rule] = rule_value
            else:
                self.rules_format_error.collect(
                    variable, rule, rule_value, rule_type, error)
        else:
            self.rules_format_error.collect(
                variable, rule, rule_value, '', 'rule not recognized')

    @staticmethod
    def check_expected(rule_value, allowed) -> list:
        """Check that the user-defined value for the
        rule "expected" is a list of strings.

        Parameters
        ----------
        rule_value
            Parsed value for the rule "expected".
        allowed
            No reference allowed values for this rule.

        Returns
        -------
        list
            empty if successful, error message otherwise.
        """
        if isinstance(rule_value, list):
            wrong = [x for x in rule_value if not isinstance(x, str)]
            if len(wrong):
                return ['not a string', wrong]
            else:
                return []
        else:
            return ['not a list']

    @staticmethod
    def check_remap(rule_value, allowed) -> list:
        """Check that the user-defined value for the
        rule "remap" is a dictionary and all keys and
        values instances should be strings, integers
        or floats.

        Parameters
        ----------
        rule_value
            Parsed value for the rule "remap".
        allowed
            No reference allowed values for this rule.

        Returns
        -------
        list
            empty if successful, error message otherwise.
        """
        if isinstance(rule_value, dict):
            wrong = [
                "%s: %s" % (str(x), str(y)) for x, y in rule_value.items() if
                not isinstance(x, (str, int, float)) or
                not isinstance(y, (str, int, float))
            ]
            if len(wrong):
                return ['not str, int or float', wrong]
            else:
                return []
        else:
            return ['not a dictionary']

    @staticmethod
    def check_validation(rule_value, allowed) -> list:
        """Check that the user-defined value for the rule
        "validation" is a nested dictionary that has for first
        key "force_to_blank_if" and for nested key "is null",
        and for nested value a list.

        Parameters
        ----------
        rule_value
            Parsed rule value for the rule "validation".
        allowed
            Reference value from the rule's assets,
            here, a data structure for the data validation,
            i.e. two-level nested dict,
            e.g.
                allowed_level1:
                  allowed_level2:
                    - variable1
                    - ...

        Returns
        -------
        list
            empty if successful, error message otherwise.
        """

        if isinstance(rule_value, dict):
            if set(rule_value).issubset(allowed):
                for allowed_key, nested_dict in rule_value.items():
                    if isinstance(nested_dict, dict):
                        for nested_rule, variables in nested_dict.items():
                            if nested_rule not in allowed[allowed_key]:
                                return ['not allowed', nested_rule]
                            if not isinstance(variables, list):
                                return ['not a list', variables]
                    else:
                        return ['not a nested dictionary']
            else:
                not_allowed = '", "'.join(set(rule_value).difference(allowed))
                return ['not allowed', not_allowed]
        else:
            return ['not a dictionary']
        return []

    @staticmethod
    def check_normalization(rule_value, allowed) -> list:
        """Check that the user-defined value for the rule
        "normalization" is a dictionary which keys are no
        other than "minimum", "maximum" or "gated_value",
        and which values are numeric.

        Parameters
        ----------
        rule_value
            Parsed rule value for the rule "normalization".
        allowed
            Reference value from the rule's assets,
            here ["maximum", "minimum", "gated_value"].

        Returns
        -------
        list
            empty if successful, error message otherwise.
        """
        # the rule must be a dict
        if isinstance(rule_value, dict):
            # the keys must be either of "maximum", "minimum", "gated_value"
            if set(rule_value).issubset(allowed):
                not_numeric = [x for x, y in rule_value.items()
                               if not isinstance(y, (int, float))]
                if len(not_numeric):
                    return ['not numeric', not_numeric]
                else:
                    return []
            else:
                not_allowed = '", "'.join(set(rule_value).difference(allowed))
                return ['not allowed', not_allowed]
        else:
            return ['not a dictionary']

    @staticmethod
    def check_allowed(rule_value, allowed) -> list:
        """Check that the user-defined value is amongst the
        texts allowed for the rule. This is for rules "ontology",
        "format", "blank" and "missing".

        Parameters
        ----------
        rule_value
            Parsed value for rule.
        allowed
            Reference value from the rule's assets, here:
            - list ['Gazetteer ontology'] for rule "ontology"
            - list ["bool", "float", "int" or "str"] for rule "format"
            - list ["not applicable", "not collected",  "not provided" or
                    "restricted access"] for rules "blank" or "missing".

        Returns
        -------
        list
            empty if successful, error message otherwise.
        """

        if isinstance(rule_value, str):
            if rule_value not in allowed:
                return ['not allowed', rule_value]
            else:
                return []
        else:
            return ['not a string']
