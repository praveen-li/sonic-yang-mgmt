#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sonic_yang_mgmt` package."""

import pytest
import os

from sonic_yang_mgmt import sonic_yang_mgmt
import sonic_yang_mgmt/tests/yang-model-tests/yangModelTesting

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    os.cmd('python yangModelTesting.py -f yangTest.json -y ../../yang-models/')
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
