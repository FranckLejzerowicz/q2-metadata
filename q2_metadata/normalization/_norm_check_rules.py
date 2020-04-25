# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_metadata.normalization._norm_errors import (
    RuleError, ExpectedError, OntologyError, RemapError,
    ValidationError, NormalizationError,
    BlankError, MissingError, FormatError
)


def check_rule(variable: str, rules: dict, rule: str, rule_value):
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
    rules : dict
        Rules in the hard-coded data structure that has
        common default values for all variables and
        that is checked and updated here.
    rule : str
        Current rule name. Could be one of "expected", "ontology",
        "remap", "validation", "normalization", "blank", "missing",
        "format".
    rule_value : str, list or dict
        Parsed rule value for the current rule.

    Raises
    ------
    RuleError
        If the rule is not recognized.
    ExpectedError
        If the "expected" rule if not properly formatted.
    OntologyError
        If the "ontology" rule if not properly formatted.
    RemapError
        If the "remap" rule if not properly formatted.
    ValidationError
        If the "validation" rule if not properly formatted.
    NormalizationError
        If the "normalization" rule if not properly formatted.
    BlankError
        If the "blank" rule if not properly formatted.
    MissingError
        If the "missing" rule if not properly formatted.
    FormatError
        If the "format" rule if not properly formatted.
    """

    rule_type_map = {
        'expected': (check_expected, ExpectedError, 'lookups', ),
        'ontology': (check_ontology, OntologyError, 'lookups'),
        'remap': (check_remap, RemapError, 'edits'),
        'validation': (check_validation, ValidationError, 'edits'),
        'normalization': (check_normalization, NormalizationError, 'edits'),
        'blank': (check_blank_missing, BlankError, 'allowed'),
        'missing': (check_blank_missing, MissingError, 'allowed'),
        'format': (check_format, FormatError, 'allowed')
    }

    if rule not in rule_type_map:
        raise RuleError(rule, variable, rule_value)

    rule_method, rule_error, rule_type = rule_type_map[rule]
    if rule_method(rule_value):
        rules[rule_type][rule] = rule_value
    else:
        raise rule_error(variable, rule_value)


def check_expected(rule_value):
    """Check that the user-defined value for the
    rule "expected" is a list of strings.

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "expected".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    # check if the rule value is indeed a list (it must be the case).
    if isinstance(rule_value, list):
        # checks that all the items in the expected value list are strings.
        str_items = [x for x in rule_value if isinstance(x, str)]
        if len(str_items) == len(rule_value):
            return True
    return False


def check_ontology(rule_value):
    """Check that the user-defined value for the
    rule "ontology" is a string that is matching one
    of one the currently supported ontologies.

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "ontology".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    return isinstance(rule_value, str) and rule_value in {'Gazetteer ontology'}


def check_remap(rule_value):
    """Check that the user-defined value for the
    rule "remap" is a dictionary and all keys and
    values instances should be strings, integers
    or floats.

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "remap".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    if isinstance(rule_value, dict):
        str_values = [
            x for x, y in rule_value.items() if
                isinstance(x, (str, int, float)) and
                isinstance(y, (str, int, float))
        ]
        if len(str_values) == len(rule_value.keys()):
            return True
    return False


def check_validation(rule_value):
    """Check that the user-defined value for the rule
    "validation" is a nested dictionary that has for first
    key "force_to_blank_if" and for nested key "is null",
    and for nested value a list.

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "validation".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    # accepted structure for the "validation" rule
    possible_validations = {
        'force_to_blank_if': {'is null'}
    }
    # check the first level is a dict
    if isinstance(rule_value, dict):
        # get the current keys
        rule_value_set = set(rule_value)
        # get the accepted keys from the current keys
        accepted_set = rule_value_set & set(possible_validations)
        # if there is not more keys than the accepted ones
        if not len(rule_value_set ^ accepted_set):
            # get the possible conditions
            possible_validations_2 = possible_validations['force_to_blank_if']
            # for each of the condition/replacements for the accepted keys
            for rule_2, rule_value_2 in rule_value['force_to_blank_if'].items():
                # check that the content of replacements are lists
                if isinstance(rule_value_2, list):
                    # get the accepted conditions from the current conditions
                    if rule_2 in possible_validations_2:
                        return True
    return False


def check_normalization(rule_value):
    """Check that the user-defined value for the rule
    "normalization" is a dictionary which keys are no
    other than "minimum", "maximum" or "gated_value",
    and which values are numeric.

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "normalization".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    allowed = {'maximum', 'minimum', 'gated_value'}
    rule_value_set = set(rule_value)
    if isinstance(rule_value, dict) and rule_value_set.issubset(allowed):
        is_int_or_float = map(lambda x: isinstance(x, (int, float)), rule_value.values())
        if len(rule_value) == sum(is_int_or_float):
            return True
    return False


def check_format(rule_value):
    """Check that the user-defined value for
    rule "format" is a string that is one of
    "bool", "float", "int" or "str".

    Parameters
    ----------
    rule_value
        Parsed rule value for rule "format".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    allowed_values = {'bool', 'float', 'int', 'str'}
    return isinstance(rule_value, str) and rule_value.lower() in allowed_values


def check_blank_missing(rule_value):
    """Check that the user-defined value for either of the
    rule "blank" ot "missing" is correctly formatted.

    blank must be a str
        Apply the rules of checking the allowed blank values, by replacing
        the not-expected values and numpy's nan (empty) by the passed
        blank value term, e.g.
                    blank:
                        - not applicable
                        - not collected
                        - not provided
                        - restricted access

    missing must be a str
        Apply rule of checking the allowed missing values:
        replace not-expected values and numpy's nan (empty) by
        the passed missing value term.
                    missing:
                        - not applicable
                        - not collected
                        - not provided
                        - restricted access

    Parameters
    ----------
    rule_value
        Parsed rule value for either of
        the rules "blank" or "missing".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    allowed_values = {'not applicable', 'not collected',
                      'not provided', 'restricted access'}
    if isinstance(rule_value, str) and rule_value.lower() in allowed_values:
        return True
    return False
