"""
Project constants.
"""

import os

# retain the trailing slash, otherwise 'api' will be stripped off by
# urllib.parse.urljoin
BASE_URL = 'https://ds20kdbi.cloud.cnaf.infn.it/preprod/api/'

# vTile repair testing
TABLE_VTILE = 'vtile'

# local database table cache
TABLE_CACHE_DIR_ROOT = os.path.expanduser('~/.ds20kdb_table_cache')
