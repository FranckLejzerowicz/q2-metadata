# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2 as q2
from qiime2.plugin import Metadata
from .plugin_setup import plugin
from ._format import MetadataFormat, MetadataDirectoryFormat
import pandas as pd


@plugin.register_transformer
def _1(data: Metadata) -> MetadataFormat:
    ff = MetadataFormat()
    path = str(ff) + '/metadata.tsv'
    data.save(path)
    return ff


@plugin.register_transformer
def _2(ff: MetadataFormat) -> Metadata:
    path = str(ff) + '/metadata.tsv'
    return Metadata.load(path)


@plugin.register_transformer
def _3(data: pd.DataFrame) -> MetadataDirectoryFormat:
    ff = MetadataDirectoryFormat()
    path = str(ff) + '/metadata.tsv'
    q2.Metadata(data).save(path)
    return ff
