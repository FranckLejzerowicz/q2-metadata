# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import yaml


class Error(Exception):
    """Base class for exceptions encountered
    in the rules checking."""

    @classmethod
    def generic_message(cls, rule, variable, value):
        reformatted_value = '\t# %s' % yaml.dump(value).replace('\n', '\n\t# ')
        return 'Wrong formatting for "%s" rule; variable %s:\n' \
               '%s' % (rule, variable, reformatted_value)


class ExpectedError(Error):
    """Exception raised for errors in the
    formatting of the "expected values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'expected'
        self.variable = variable
        self.value = value
        self.message = self.get_message()

    def get_message(self):
        if not isinstance(self.value, list):
            return 'is not a list'
        str_items = [x for x in self.value if isinstance(x, str)]
        if len(str_items) != len(self.value):
            return 'not all items are strings'

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> %s' % (message, self.message)


class OntologyError(Error):
    """Exception raised for errors in the
    formatting of the "ontology values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'ontology'
        self.variable = variable
        self.value = value
        self.message = self.get_message()

    def get_message(self):
        ontologies = ['Gazetteer ontology']
        if not isinstance(self.value, str):
            return 'is not a string'
        if self.value not in ontologies:
            return 'none of %s' % ', '.join(ontologies)

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> %s' % (message, self.message)


class RemapError(Error):
    """Exception raised for errors in the
    formatting of the "remap values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'remap'
        self.variable = variable
        self.value = value
        self.message = self.get_message()

    def get_message(self):
        if not isinstance(self.value, dict):
            return 'is not a dictionary'
        str_values = [x for x, y in self.value.items() if isinstance(y, str)]
        if len(str_values) != len(self.value.keys()):
            return 'not all dictionary values are strings'

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> %s' % (message, self.message)


class ValidationError(Error):
    """Exception raised for errors in the
    formatting of the "validation values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'validation'
        self.variable = variable
        self.value = value
        self.message = self.get_message()

    def get_message(self):
        possible_validations = {
            'force_to_blank_if': {'is_null'}
        }
        if not isinstance(self.value, dict):
            return 'is not a dictionary'
        rule_value_set = set(self.value)
        accepted_set = rule_value_set & set(possible_validations)
        non_accepted_set = sorted(rule_value_set ^ accepted_set)
        if len(non_accepted_set):
            return 'inacceptable validations (%s)' % ', '.join(non_accepted_set)
        possible_validations_2 = possible_validations['force_to_blank_if']
        for rule_2, rule_value_2 in self.value['force_to_blank_if'].items():
            if not isinstance(rule_value_2, list):
                return 'variables under condition "%s" not in a list' % rule_2
            if rule_2 not in possible_validations_2:
                return 'inacceptable condition: %s' % rule_2

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> %s' % (message, self.message)


class NormalizationError(Error):
    """Exception raised for errors in the
    formatting of the "validation values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'normalization'
        self.variable = variable
        self.value = value
        self.message = self.get_message()

    def get_message(self):
        if not isinstance(self.value, dict):
            return 'is not a dictionary'
        possible_normalizations = {'maximum', 'mininum', 'gated_value'}
        rule_value_set = set(self.value)
        impossible = sorted(rule_value_set ^ (rule_value_set & possible_normalizations))
        if len(impossible):
            return 'impossible normalization terms (%s)' % ', '.join(impossible)

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> %s' % (message, self.message)


class BlankError(Error):
    """Exception raised for errors in the
    formatting of the "blank values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'format'
        self.variable = variable
        self.value = value

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> is not a string' % message


class MissingError(Error):
    """Exception raised for errors in the
    formatting of the "missing values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'missing'
        self.variable = variable
        self.value = value

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> is not a string' % message


class FormatError(Error):
    """Exception raised for errors in the
    formatting of the "format values" rules.
    """
    def __init__(self, variable, value):
        self.rule = 'format'
        self.variable = variable
        self.value = value

    def __str__(self):
        message = self.generic_message(self.rule, self.variable, self.value)
        return '%s -> is not a string' % message
