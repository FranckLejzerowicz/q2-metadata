# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import yaml
import pandas as pd


class RuleFormatError(object):

    def __init__(self):
        self.rule_format_error = []

    def collect(self, variable, rule, rule_value, rule_type, error):
        reformatted_value = '\t# %s' % yaml.dump(rule_value).replace('\n', '\n\t# ')
        message = 'Wrong formatting for "%s" rule:\n%s' % (rule, reformatted_value)
        error_list = [
            variable,
            rule,
            rule_value,
            rule_type,
            message,
            error
        ]
        self.rule_format_error.append(error_list)

    def as_dataframe(self):
        rule_format_error_pd = pd.DataFrame(
            self.rule_format_error,
            columns=[
                'variable',
                'rule',
                'rule_value',
                'rule_type',
                'message',
                'error'
            ]
        )
        return rule_format_error_pd
