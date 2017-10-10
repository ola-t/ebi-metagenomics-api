#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import os

from django.core.urlresolvers import reverse
from django.core.management import call_command

from rest_framework import status

# import fixtures
from test_utils.emg_fixtures import *  # noqa


@pytest.mark.usefixtures('mongodb')
@pytest.mark.django_db
class TestCLI(object):

    def test_goslim(self, client, run):
        call_command('import_summary', 'ABC01234',
                     os.path.dirname(os.path.abspath(__file__)),
                     suffix='.go_slim')

        url = reverse("emgapi:goterms-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()
        assert len(rsp['data']) == 3

        expected = ['GO:0030246', 'GO:0046906', 'GO:0043167']
        ids = [a['id'] for a in rsp['data']]
        assert ids == expected

    def test_go(self, client, run):
        call_command('import_summary', 'ABC01234',
                     os.path.dirname(os.path.abspath(__file__)),
                     suffix='.go')

        url = reverse("emgapi:goterms-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()
        assert len(rsp['data']) == 6

        expected = ['GO:0030170', 'GO:0019842', 'GO:0030246',
                    'GO:0046906', 'GO:0043167', 'GO:0005515']
        ids = [a['id'] for a in rsp['data']]
        print(ids)
        assert ids == expected

    def test_ipr(self, client, run):
        call_command('import_summary', 'ABC01234',
                     os.path.dirname(os.path.abspath(__file__)),
                     suffix='.ipr')

        url = reverse("emgapi:interproidentifier-list")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()
        assert len(rsp['data']) == 6

        expected = ['IPR009739', 'IPR021425', 'IPR021710',
                    'IPR033771', 'IPR024561', 'IPR013698']
        ids = [a['id'] for a in rsp['data']]
        assert ids == expected

    def test_qc(self, client, run):
        call_command('import_qc', 'ABC01234',
                     os.path.dirname(os.path.abspath(__file__)))

        url = reverse("emgapi:runs-pipelines-metadata-list",
                      args=["ABC01234", "1.0"])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()
        assert len(rsp['data']) == 5

        expected = [
            'Submitted nucleotide sequences/12345',
            'Nucleotide sequences after format-specific filtering/12345',
            'Predicted CDS/12345',
            'Predicted CDS with InterProScan match/12345',
            'Total InterProScan matches/12345678'
        ]
        ids = [a['id'] for a in rsp['data']]
        assert ids == expected
