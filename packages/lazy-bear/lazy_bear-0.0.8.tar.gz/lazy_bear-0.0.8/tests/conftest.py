"""Configuration for the pytest test suite."""

from os import environ

from lazy_bear import METADATA

environ[f"{METADATA.env_variable}"] = "test"
