# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import yaml
from glob import glob
import pandas as pd
from os.path import basename, isdir, splitext

from q2_metadata.normalization._norm_messages import warningsCollection, errorsCollection


class Rules(object):
    """Collect the rules of one current variable rules.

    Parameters
    ----------
    variable_rules_fp : str
        Path to one variable's rules yaml file.

    Attributes
    ----------
    variable : str
        Name of the variable which rules are parsed and
        that is the yaml file name without the .yml extension.

    remap : dict
        Apply the rules of remapping variables values, by replacing
        all instances of a given value by another one value.
                    'remap:
                      str: str'
    validation : dict
        Apply the rules of validating variables values, by replacing by the blank
        (or the missing) value every instance which in one or many other columns
        have a null or missing value.
                    'validation:
                      force_to_blank_if:
                        is null:
                        - variable'
    normalization : dict
        Apply the rules of normalizing the variables values, by replacing
        the values outside the range by a given replacement value.
                    'normalization:
                        gated_value:
                            - Out of bounds
                        maximum:
                            - int
                            - float
                        minimum:
                            - int
                            - float'
    missing : str
        Apply the rules of checking the allowed missing values, by replacing
        the not-expected values and numpy's nan (empty) by the passed
        missing value term.
                    'missing:
                        - not applicable
                        - not collected
                        - not provided
                        - restricted access'
    format : str
        Apply the rules of checking that the passed column in the correct format.
        [THIS COMMAND WOULD EITHER INFER THE DTYPE (as of now) OR USE THE
        RESULT OF AN INITIAL DTYPE GETTER FUNCTION (see _dtypes.py)]
                    'format:
                      - bool
                      - float
                      - int
                      - str'
    expected : list
        Apply the rules of allowing only expected values.
        These do allow the missing and blanks.
                    'expected:
                        - str
                        - list'
    ontology : str
        Name of the ontology to lookup within for control vocabulary, e.g.
                    'ontology: Gazetteer'
    blank : str
        Apply the rules of checking the allowed blank values, by replacing
        the not-expected values and numpy's nan (empty) by the passed
        blank value term, e.g.
                    'blank:
                        - not applicable
                        - not collected
                        - not provided
                        - restricted access'

    Raises
    ------
    ValueError
        # If the remote argument is not of ``bool`` or ``str`` type.
        # If none of the samples in the ordination matrix are in the metadata.
        # If the data is one-dimensional.
    KeyError
        # If there's samples in the ordination matrix but not in the metadata.
    """
    def __init__(self, variable_rules_fp: str):
        """
        Initialize the class instance for one set of rules beloning
        to one single metadata variable with it possible attribute, as
        a rate of one attribute per possible rule, plus the current
        variable name.

        Parameters
        ----------
        variable_rules_fp : str
            Path to one variable's rules yaml file.
        """
        self.variable = basename(variable_rules_fp).split('.yml')[0]
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
        self._process_rule(variable_rules_fp)

    def _process_rule(self, variable_rules_fp: str):
        """Read the yaml file of the current variable's rules.

        Parameters
        ----------
        variable_rules_fp : str
            Path to one variable's rules yaml file.

        Returns
        -------

        """
        with open(variable_rules_fp) as handle:
            variable_rules = yaml.load(handle, Loader=yaml.FullLoader)
            self._check_variable_rules(variable_rules)

    def _check_variable_rules(self, variable_rules: dict):
        """This functions adds encountered issues
        to the warning/error class objects.

        Parameters
        ----------
        variable_rules : dict

        """
        for rule, rule_value in variable_rules.items():
            if rule == 'expected':
                if isinstance(rule_value, list):
                    str_items = [x for x in rule_value if isinstance(x, str)]
                    if len(str_items) == len(rule_value):
                        self.rules['allowed'][rule] = rule_value
                    else:
                        errorsCollection(self.variable, rule, rule_value)

            elif rule == 'ontology':
                if isinstance(rule_value, str):
                    if rule_value in ['Gazetteer']:
                        self.rules['lookups'][rule] = rule_value

            elif rule == 'remap':
                if isinstance(rule, dict):
                    str_values = [x for x,y in rule_value.items() if isinstance(y, str)]
                    if len(str_values) == len(rule_value.keys()):
                        self.rules['edits'][rule] = rule_value
                    else:
                        errorsCollection(self.variable, rule, rule_value)

            elif rule == 'validation':
                possible_validations = {
                    'force_to_blank_if': {'is_null'}
                }
                if isinstance(rule_value, dict):
                    rule_value_set = set(rule_value)
                    if len(rule_value_set ^ (rule_value_set & set(possible_validations))):
                        errorsCollection(self.variable, rule, rule_value)
                        # raise and stop ? or keep checking?
                    else:
                        for rule_2, rule_value_2 in rule_value['force_to_blank_if'].items():
                            if isinstance(rule_value_2, list):
                                possible_validations_2 = possible_validations['force_to_blank_if']
                                if len(set(rule_2) ^ (set(rule_2) & possible_validations_2)):
                                    errorsCollection(self.variable, rule, rule_value)
                                else:
                                    self.rules['edits'][rule] = rule_value
                            else:
                                errorsCollection(self.variable, rule, rule_value)
                else:
                    errorsCollection(self.variable, rule, rule_value)

            elif rule == 'normalization':
                if isinstance(rule_value, dict):
                    possible_normalizations = {'maximum', 'mininum', 'gated_value'}
                    rule_value_set = set(rule_value)
                    if len(rule_value_set ^ (rule_value_set & possible_normalizations)):
                        errorsCollection(self.variable, rule, rule_value)
                    else:
                        self.rules['edits'][rule] = rule_value

            elif rule == 'blank':
                if isinstance(rule_value, str):
                    self.rules['allowed'][rule] = rule_value

            elif rule == 'missing':
                if isinstance(rule_value, str):
                    self.rules['allowed'][rule] = rule_value

            elif rule == 'format':
                if isinstance(rule_value, str):
                    self.rules['format'][rule] = rule_value

    # methods to apply the rules onto
    def normalize(self, variable: str, input_column: pd.Series) -> pd.Series:
        """
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

    Parameters
    ----------
    variables_rules_dir : str
        Path to the folder containing the variables rules in yaml.

    Attributes
    ----------
    variables_names : list
        Variables that have associated rules (and for now
        that are all the the rules from AGP until we refine the scope
        and decide whether to bother users with failed rules parsing
        checks for rules that are irrelevant to this user, i.e. shall
        we only parse rules in the focus?)
    warnings : warningsCollection instance
        Collection of warnings encountered during either the parsing
        of the variables rules, or during the application the rules.
    errors : errorsCollection instance
        Collection of errors encountered during either the parsing
        of the variables rules, or during the application the rules.
    """

    def __init__(self, variables_rules_dir):
        self.variables_rules_fps = self._check_variables_rules_dir(variables_rules_dir)

        # initialize the collection objects for warning and errors
        self.warnings = warningsCollection()
        self.errors = errorsCollection()

        # parse all the variables' yaml rules files
        self.variables_rules = self.parse_variables_rules()

    def get_variables_names(self):
        return sorted(self.variables_rules.keys())

    def parse_variables_rules(self) -> dict:
        """
        Parse the variables yaml rues files one by one.

        Returns
        -------
        variables_rules : dict
            Rules (values) for each metadata variable (keys).
        """
        variables_rules = {}
        for variable_rules_fp in self.variables_rules_fps:
            variable = splitext(basename(variable_rules_fp))[0]
            # make an instance of the class Rules() to get the rules
            # of the current variable and check the yaml format
            variables_rules[variable] = Rules(variable_rules_fp)
        return variables_rules

    def _check_variables_rules_dir(self, variables_rules_dir: str) -> list:
        """Checks that the yaml rules directory exists
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
