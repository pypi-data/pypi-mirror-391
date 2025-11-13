# -*- coding: utf-8 -*-
"""
Provides a connector to the Nakala research repository.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501


from .models import (
    PROD_URL, TEST_URL,
    Uploadable, Collection, Data, File,
    _exception,  # TODO remove
    )
from .edit import upload, create_nakala_metadata
from .read import getDatabase, update_presets, ITEM_EID, FILE_EID


__version__ = '0.11.0'
__all__ = [
        'getDatabase', 'update_presets',
        'upload', 'create_nakala_metadata',
        'Uploadable', 'Collection', 'Data', 'File',
        'PROD_URL', 'TEST_URL',
        '__version__',  '__copyright__', '__license__',
        '_exception',  # TODO remove
    ]
__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
