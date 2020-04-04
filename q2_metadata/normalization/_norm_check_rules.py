# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_metadata.normalization._norm_errors import (
    ExpectedError, OntologyError, RemapError,
    ValidationError, NormalizationError,
    BlankError, MissingError, FormatError
)


def check_rule(variable: str, rules: dict, rule: str, rule_value):
    """For each rule in the current variable's rules set,
    perform checks that the rule values to be used for the rules
    to apply are properly formatted.
        - If properly formatted: full the rules dict
        for the variable's Rules() class instance.
        - If not properly formatted: raise a specific error and
        collect the encountered error in the ErrorsCollection()
        instance for this variable's Rules() class instance.

    Parameters
    ----------
    variable : str
        Name of the variable which rules are parsed and
        that is the yaml file name without the .yml extension.
    rules : dict
        Rules in the hard-coded data structure that has
        common default values for all variables and
        that is checked and updated here.
    rule : str
        Current rule name. Could be one of these:
        - expected: accepted, controlled vocabulary from AGP.
        - ontology: accepted, controlled vocabulary from a third-party resource.
        - remap: the replacements to perform ( "A" -> "B" )
        - validation: the
        - normalization:
        - blank:
        - missing:
        - format:
    rule_value : str, list or dict
        Parsed rule value for the current rule.

    """
    if rule == 'expected':
        if check_expected(rule_value):
            rules['lookups'][rule] = rule_value
        else:
            raise ExpectedError(variable, rule_value)

    elif rule == 'ontology':
        if check_ontology(rule_value):
            rules['lookups'][rule] = rule_value
        else:
            raise OntologyError(variable, rule_value)

    elif rule == 'remap':
        if check_remap(rule_value):
            rules['edits'][rule] = rule_value
        else:
            raise RemapError(variable, rule_value)

    elif rule == 'validation':
        if check_validation(rule_value):
            rules['edits'][rule] = rule_value
        else:
            raise ValidationError(variable, rule_value)

    elif rule == 'normalization':
        if check_normalization(rule_value):
            rules['edits'][rule] = rule_value
        else:
            raise NormalizationError(variable, rule_value)

    elif rule == 'blank':
        if check_str(rule_value):
            rules['allowed'][rule] = rule_value
        else:
            raise BlankError(variable, rule_value)

    elif rule == 'missing':
        if check_str(rule_value):
            rules['allowed'][rule] = rule_value
        else:
            raise MissingError(variable, rule_value)

    elif rule == 'format':
        if check_str(rule_value):
            rules['format'] = rule_value
        else:
            raise FormatError(variable, rule_value)


def check_expected(rule_value):
    """Check that the user-defined value for the
    rule "expected" is correctly formatted.

    expected must be a list
        Apply rule of allowing only expected values:
        These do allow the missing and blanks.
                    expected:
                        - str
                        - list

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
    rule "ontology" is correctly formatted.

    ontology must be a str
        Name of the ontology to lookup within for control vocabulary, e.g.
                    ontology: Gazetteer

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "ontology".

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    if isinstance(rule_value, str):
        if rule_value in ['Gazetteer ontology']:
            return True
    return False


def check_remap(rule_value):
    """Check that the user-defined value for the
    rule "remap" is correctly formatted.

    remap must be a dict
        Apply the rule of remapping variables values: replace
        all instances of a given value by another one value.
                    remap:
                      str: str

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
        str_values = [x for x, y in rule_value.items() if isinstance(y, str)]
        if len(str_values) == len(rule_value.keys()):
            return True
    return False


def check_validation(rule_value):
    """Check that the user-defined value for the
    rule "validation" is correctly formatted.

    validation must be a dict
        Apply the rule of validating variables values: replace by the blank
        (or the missing) value every sample entry that for the current variable has
        in one or multiple other variable(s) a null or missing value for that sample.
                    validation:
                      force_to_blank_if:
                        is null:
                        - variable

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
    """Check that the user-defined value for the
    rule "normalization" is correctly formatted.

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

    Parameters
    ----------
    rule_value
        Parsed rule value for the rule "normalization".

    Returns
    -------
    bool
        True if successful, False otherwise.

    """
    if isinstance(rule_value, dict):
        possible_normalizations = {'maximum', 'mininum', 'gated_value'}
        rule_value_set = set(rule_value)
        if not len(rule_value_set ^ (rule_value_set & possible_normalizations)):
            return True
    return False


def check_str(rule_value):
    """Check that the user-defined value for either of the
    rules "blank", "missing" and "format" is correctly formatted.

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
        Apply rule of checking that the passed column in the correct format:
        [THIS COMMAND WOULD EITHER INFER THE DTYPE (as of now) OR USE THE
        RESULT OF AN INITIAL DTYPE GETTER FUNCTION (see _dtypes.py)]
                    format:
                      - bool
                      - float
                      - int
                      - str

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
    rule_value
        Parsed rule value for either of the
        rules "blank", "missing" or "format".

    Returns
    -------
    bool
        True if successful, False otherwise.

    """
    if isinstance(rule_value, str):
        return True
    return False