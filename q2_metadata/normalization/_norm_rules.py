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

from q2_metadata.normalization._norm_messages import WarningsCollection, ErrorsCollection
from q2_metadata.normalization._norm_check_rules import check_rule


class Rules(object):
    """Collect the rules of one current variable.

        remap must be a dict
            Apply the rule of remapping variables values: replace
            all instances of a given value by another one value.
                        remap:
                          str: str
        validation must be a dict
            Apply the rule of validating variables values: replace by the blank
            (or the missing) value every sample entry that for the current variable has
            in one or multiple other variable(s) a null or missing value for that sample.
                        validation:
                          force_to_blank_if:
                            is null:
                            - variable
        normalization must be a dict
            Apply the rules of normalizing the variables values, by replacing
            the values outside the range by a given replacement value.
                        normalization:
                            gated_value:
                                - Out of bounds
                            maximum:
                                - int
                                - float
                            minimum:
                                - int
                                - float
        missing must be a str
            Apply rule of checking the allowed missing values:
            replace not-expected values and numpy's nan (empty) by
            the passed missing value term.
                        missing:
                            - not applicable
                            - not collected
                            - not provided
                            - restricted access
        format must be a str
            Apply rule of checking that the passed column is in the correct format:
            [THIS COMMAND WOULD EITHER INFER THE DTYPE (as of now) OR USE THE
            RESULT OF AN INITIAL DTYPE GETTER FUNCTION (see _dtypes.py)]
                        format:
                          - bool
                          - float
                          - int
                          - str
        expected must be a list
            Apply rule of allowing only expected values:
            These do allow the missing and blanks.
                        expected:
                            - str
                            - list
        ontology must be a str
            Name of the ontology to lookup within for control vocabulary, e.g.
                        ontology: Gazetteer
        blank must be a str
            Apply the rules of checking the allowed blank values, by replacing
            the not-expected values and numpy's nan (empty) by the passed
            blank value term, e.g.
                        blank:
                            - not applicable
                            - not collected
                            - not provided
                            - restricted access

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
    variables_rules : dict
        Rules (values) parsed from the current variable's yml file.
    warnings : WarningsCollection instance
        Collection of warnings encountered during either the parsing
        of the variables rules, or during the application the rules.
    errors : ErrorsCollection instance
        Collection of errors encountered during either the parsing
        of the variables rules, or during the application the rules.

    Methods
    -------
    parse_rule : staticmethod
        Performs the parsing of the current variable's yml file and
        returns the rules (values) in `self.variables_rules`.
    _check_variable_rules
        Loops over each rule and check that they are well formatted
        and either raise a specific issue error or a fill the rules dict.
    normalize
        Perform the application of the variables' rules.

    Raises
    ------
    IOError : yaml.YAMLError
        If something went wrong with reading the .yml rule file.
    ExpectedError
        If wrong formatting of an "expected" rule.
    OntologyError
        If wrong formatting of an "ontology" rule.
    RemapError
        If wrong formatting of a "remap" rule.
    ValidationError
        If wrong formatting of a "validation" rule.
    NormalizationError,
         If wrong formatting of an "normalization" rule.
    BlankError
        If wrong formatting of a "blank" rule.
    MissingError
        If wrong formatting of a "missing" rule.
    FormatError
        If wrong formatting of a "format" rule.

    """
    def __init__(self, variable_rules_fp: str, variable: str):
        """Initialize the class instance for the set of rules associated
        with a single metadata variable. The instantiated class will be
        given a `variable` attribute corresponding to the variable name
        as string, as well as a `rules` attribute collecting the actual
        rules in a dictionary.

        Parameters
        ----------
        variable_rules_fp : str
            Path to one variable's rules yaml file.
        variable : str
            Name of the variable which rules are parsed and
            that is the yaml file name without the .yml extension.

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
                'missing': None
            },
            'format': None
        }
        self.variables_rules = self.parse_rule(variable_rules_fp)
        self.warnings = WarningsCollection()
        self.errors = ErrorsCollection()
        self._check_variable_rules(variable)

    @staticmethod
    def parse_rule(variable_rules_fp: str):
        """Read the yaml file of the current variable's rules.

        Parameters
        ----------
        variable_rules_fp : str
            Path to one variable's rules yaml file.

        Returns
        -------
        yaml_loaded : dict
            Parsed variable's rules.
        """
        with open(variable_rules_fp) as handle:
            try:
                yaml_loaded = yaml.load(handle, Loader=yaml.FullLoader)
                return yaml_loaded
            except yaml.YAMLError:
                raise IOError("Something is wrong with the .yml rule file.")

    def _check_variable_rules(self, variable):
        """This functions adds encountered issues
        to the warning/error class objects.
        """
        for rule, rule_value in self.variables_rules.items():
            check_rule(variable, self.rules, rule, rule_value)

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
    variables_rules_files : list
        Paths to the yaml rules files.
    warnings : WarningsCollection instance
        Collection of warnings encountered during either the parsing
        of the variables rules, or during the application the rules.
    errors : ErrorsCollection instance
        Collection of errors encountered during either the parsing
        of the variables rules, or during the application the rules.

    Methods
    -------
    _check_variables_rules_dir
        Performs checks on rules paths input. Either raise Exceptions,
        or return the list `variables_rules_files` containing the paths
        to the existing yml rules files.
    parse_variables_rules
        Parse the yml rules files, one variable at a time and returns the
        dict `variables_rules` that for each variable (keys) leads to an
        instance of the `Rules()` class. This class performs rule-formatting
        checks and fills a rules dict structure.

    Raises
    ------
    IOError
        If directory passed to --p-rules-dir does not exist.
    FileNotFoundError
        If directory passed to --p-rules-dir contains no .yml file.

    """

    def __init__(self, variables_rules_dir):
        """Initialize the class instance for the collection of the set
        of rules associated with all the metadata variables. The instantiated class will be
        given a `variable` attribute corresponding to the variable name
        as string, as well as a `rules` attribute collecting the actual
        rules in a dictionary.

        Parameters
        ----------
        variables_rules_dir
        """
        self.warnings = WarningsCollection()
        self.errors = ErrorsCollection()
        self.variables_rules_fps = self._check_variables_rules_dir(variables_rules_dir)

    def parse_variables_rules(self) -> dict:
        """Parse the variables yaml rues files one by one.

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
            variables_rules[variable] = Rules(variable_rules_fp, variable)
        return variables_rules

    @staticmethod
    def _check_variables_rules_dir(variables_rules_dir: str) -> list:
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
