"""
Helper functions for loading environment settings.
"""
import os
import sys
import json
import re
from lazy import lazy
from path import path


class Env(object):
    """
    Load information about the execution environment.
    """

    def __init__():
        # Root of the git repository (edx-platform)
        REPO_ROOT = path(__file__).dirname().dirname().dirname()

        # Service variant (lms, cms, etc.) configured with an environment variable
        # We use this to determine which envs.json file to load.
        SERVICE_VARIANT = os.environ.get('SERVICE_VARIANT', None)
        # If service variant not configured in env, then pass the correct
        # environment for lms / cms
        if not SERVICE_VARIANT:  # this will intentionally catch "";
            # ignore command line environments, e.g.  "paver var=val"
            clean_args = [x for x in sys.argv[1:] if x.find('=')<0]
            # consider only words remaining (parse out separators)
            p = re.compile(r'\W+')
            clean_args = p.split(' '.join(clean_args))
            # if lms or cms is among command line words, use it's env
            SERVICE_VARIANT = 'lms' if 'lms' in clean_args \
                        else 'cms' if ('cms' in clean_args) or ('studio' in clean_args) \
                        else SERVICE_VARIANT

    @lazy
    def env_tokens(self):
        """
        Return a dict of environment settings.
        If we couldn't find the JSON file, issue a warning and return an empty dict.
        """

        # Find the env JSON file
        env_path = "env.json"
        if self.SERVICE_VARIANT is not None:
            env_path = self.REPO_ROOT.dirname() / "{service}.env.json".format(service=self.SERVICE_VARIANT)

        # If the file does not exist, issue a warning and return an empty dict
        if not os.path.isfile(env_path):
            print "Warning: could not find environment JSON file at '{path}'".format(path=env_path)
            return dict()

        # Otherwise, load the file as JSON and return the resulting dict
        try:
            with open(env_path) as env_file:
                return json.load(env_file)

        except ValueError:
            print "Error: Could not parse JSON in {path}".format(path=env_path)
            sys.exit(1)

    @lazy
    def feature_flags(self):
        """
        Return a dictionary of feature flags configured by the environment.
        """
        return self.env_tokens.get('FEATURES', dict())
