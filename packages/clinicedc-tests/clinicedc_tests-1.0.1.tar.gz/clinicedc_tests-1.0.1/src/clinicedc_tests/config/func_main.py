from __future__ import annotations

import os
import sys

import django
from django.test.runner import DiscoverRunner


def func_main(django_settings_module: str, *project_tests: str):
    """Directly set DJANGO_SETTINGS_MODULE instead of
    using settings.configure.
    """
    os.environ["DJANGO_SETTINGS_MODULE"] = django_settings_module
    django.setup()
    tags = [t.split("=")[1] for t in sys.argv if t.startswith("--tag")]
    failfast = any([True for t in sys.argv if t.startswith("--failfast")])
    keepdb = any([True for t in sys.argv if t.startswith("--keepdb")])
    opts = dict(failfast=failfast, tags=tags, keepdb=keepdb)
    failures = DiscoverRunner(**opts).run_tests(list(project_tests))
    sys.exit(failures)
