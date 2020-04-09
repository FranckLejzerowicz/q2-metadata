# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2 as q2
import pandas as pd
import pkg_resources

from q2_metadata.normalization._norm_utils import get_intersection, get_variables_rules_dir
from q2_metadata.normalization._norm_messages import WarningsCollection, ErrorsCollection
from q2_metadata.normalization._norm_rules import RulesCollection

RULES = pkg_resources.resource_filename("q2_metadata", "")


def normalize(metadata: q2.Metadata, rules_dir: q2.plugin.Str) -> pd.DataFrame:
    """
    Parameters
    ----------
    metadata : q2.Metadata
        The sample metadata.
    rules_dir : q2.plugin.Str
        The path to the yaml rules folder.

    Returns
    -------
    metadata_curated : pd.DataFrame
        Curated metadata table.
    """

    # TEMPORARY FUNCTION TO PASS THE DEFAULT FOLDER CONTAINING OUR 8 RULES
    # (A REAL USER SHOULD PASS ANOTHER FOLDER LOCATION TO '--p-rules-dir')
    variables_rules_dir = get_variables_rules_dir(rules_dir, RULES)

    # initialize the collection objects as well as for warning and errors
    rules = RulesCollection()
    warnings = WarningsCollection()
    errors = ErrorsCollection()

    # Collect rules from yaml files folder by instantiating a class
    variables_rules_files = rules.check_variables_rules_dir(variables_rules_dir)

    # parse all the variables' yaml rules files
    rules.parse_variables_rules(list(variables_rules_files))

    # Get metadata as pandas data frame
    md = metadata.to_dataframe()

    # get metadata variables that have rules
    focus = get_intersection(rules.variables_rules.keys(), md.columns.tolist())

    # checks correct rules format and put rules in data structure
    rules.check_variables_rules(focus)

    # apply rules one variable at a time
    # for variable in focus:
    #     md[variable] = rules.normalize(variable, md[variable])

    # only during dev so that the function return something :)
    return md
