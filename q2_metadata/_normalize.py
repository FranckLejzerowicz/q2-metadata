# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2 as q2
import pandas as pd
import pkg_resources

from q2_metadata.normalization._norm_utils import get_intersection
from q2_metadata.normalization._norm_rules import RulesCollection

RULES = pkg_resources.resource_filename("q2_metadata", "")


def normalize(metadata: q2.Metadata, rules_dir: q2.plugin.Str) -> q2.Metadata:
    """
    Parameters
    ----------
    metadata : q2.Metadata
        The sample metadata.
    rules_dir : q2.plugin.Str
        The path to the yaml rules folder.

    Returns
    -------
    metadata_curated : q2.Metadata
        Curated metadata table.
    """
    variables_rules_dir = str(rules_dir)
    if not variables_rules_dir:
        variables_rules_dir = RULES

    # Collect rules from yaml files folder
    rules = RulesCollection(variables_rules_dir)
    # Get metadata as pandas data frame
    md = metadata.to_dataframe()
    focus = get_intersection(rules.get_variables_names(), md.columns.tolist())
    # for variable in focus:
    #     md[variable] = rules.normalize(variable, md[variable])

    # only during dev so that the function return something :)
    md_out = pd.DataFrame()
    return q2.Metadata(md_out)