"""
Settings for bok choy tests
"""

import os
from path import path


########################## Prod-like settings ###################################
# These should be as close as possible to the settings we use in production.
# As in prod, we read in environment and auth variables from JSON files.
# Unlike in prod, we use the JSON files stored in this repo.
# This is a convenience for ensuring (a) that we can consistently find the files
# and (b) that the files are the same in Jenkins as in local dev.
os.environ['SERVICE_VARIANT'] = 'bok_choy'
os.environ['CONFIG_ROOT'] = path(__file__).abspath().dirname()  #pylint: disable=E1120

from .aws import *  # pylint: disable=W0401, W0614
from xmodule.x_module import prefer_xmodules


######################### Testing overrides ####################################

# Needed for the reset database management command
INSTALLED_APPS += ('django_extensions',)

# Redirect to the test_root folder within the repo
TEST_ROOT = CONFIG_ROOT.dirname().dirname() / "test_root"  #pylint: disable=E1120
GITHUB_REPO_ROOT = (TEST_ROOT / "data").abspath()
LOG_DIR = (TEST_ROOT / "log").abspath()

# Configure Mongo modulestore to use the test folder within the repo
for store in ["default", "direct"]:
    MODULESTORE[store]['OPTIONS']['fs_root'] = (TEST_ROOT / "data").abspath()  #pylint: disable=E1120

# Enable django-pipeline and staticfiles
STATIC_ROOT = (TEST_ROOT / "staticfiles").abspath()
PIPELINE = True

# Silence noisy logs
import logging
LOG_OVERRIDES = [
    ('track.middleware', logging.CRITICAL),
    ('edx.discussion', logging.CRITICAL),
]
for log_name, log_level in LOG_OVERRIDES:
    logging.getLogger(log_name).setLevel(log_level)

# Use the auto_auth workflow for creating users and logging them in
FEATURES['AUTOMATIC_AUTH_FOR_TESTING'] = True

# Enable XBlocks
XBLOCK_SELECT_FUNCTION = prefer_xmodules

# Unfortunately, we need to use debug mode to serve staticfiles
DEBUG = True
