#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sonic_yang_mgmt` package."""

import pytest
import os

from sonic_yang_mgmt import sonic_yang_mgmt

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    os.system('python sonic_yang_mgmt/tests/yang-model-tests/yangModelTesting.py -f sonic_yang_mgmt/tests/yang-model-tests/yangTest.json -y sonic_yang_mgmt/yang-models/')
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
