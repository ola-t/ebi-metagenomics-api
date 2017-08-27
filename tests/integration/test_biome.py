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


# import pytest
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from model_mommy import mommy

from emgapi import models as emg_models


class TestBiomeAPI(APITestCase):

    def setUp(self):
        self.data = {}
        self.data['study'] = mommy.make(
            'emgapi.Study',
            pk=1,
            accession="SPR0001",
            is_public=1,
        )

        self.data['_biomes'] = [
            {'lineage': 'root', 'depth': 1, 'lft': 1, 'rgt': 50},
            {'lineage': 'root:foo', 'depth': 2, 'lft': 2, 'rgt': 25},
            {'lineage': 'root:foo2', 'depth': 2, 'lft': 26, 'rgt': 49},
            {'lineage': 'root:foo:bar', 'depth': 3, 'lft': 3, 'rgt': 24},
            {'lineage': 'root:foo2:bar2', 'depth': 3, 'lft': 26, 'rgt': 48},
        ]
        for b in self.data['_biomes']:
            mommy.make(
                'emgapi.Biome',
                depth=b['depth'],
                biome_name=b['lineage'].split(':')[-1],
                lineage=b['lineage'],
                lft=b['lft'],
                rgt=b['rgt'],
                pk=(self.data['_biomes'].index(b)+1)
            )

        self.data['samples'] = []
        for pk in range(2, len(self.data['_biomes'])+1):
            self.data['samples'].append(
                mommy.make(
                    'emgapi.Sample',
                    pk=pk,
                    biome=emg_models.Biome.objects.get(pk=pk),
                    accession="ERS{:0>3}".format(pk),
                    is_public=1,
                    study=self.data['study']
                )
            )

    def test_biomes_list(self):
        url = reverse('emgapi:biomes-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()

        assert len(rsp['data']) == 2
        biomes = rsp['data']
        for b in biomes:
            assert b['type'] == 'biomes'
            assert b['id'] in ('root:foo', 'root:foo2')

    def test_samples(self):
        url = reverse('emgapi:biomes-children-list', args=['root:foo'])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()

        # Data
        assert len(rsp['data']) == 1

        biomes = rsp['data']
        for b in biomes:
            assert b['type'] == 'biomes'
            assert b['id'] in ('root:foo:bar',)

        response = self.client.get(
            biomes[0]['relationships']['samples']['links']['related'])
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()
        assert len(rsp['data']) == 1
        for s in rsp['data']:
            assert s['type'] == 'samples'
            assert s['id'] in ('ERS004',)

    def test_study(self):
        url = reverse('emgapi:studies-detail', args=['SPR0001'])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        rsp = response.json()

        # Data
        biomes = rsp['data']['relationships']['biomes']['data']
        assert len(biomes) == 4
        _expected_biomes = (
            'root:foo', 'root:foo2', 'root:foo:bar', 'root:foo2:bar2')
        for b in biomes:
            assert b['type'] == 'biomes'
            assert b['id'] in _expected_biomes
