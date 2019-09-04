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

from rest_framework_json_api import serializers
# from rest_framework_json_api import relations

from rest_framework_mongoengine import serializers as m_serializers

# from emgapi import models as emg_models
from emgapi import fields as emg_fields

from . import models as m_models


class GoTermSerializer(m_serializers.DocumentSerializer,
                       serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:goterms-detail',
        lookup_field='accession',
    )

    def get_analysis(self, obj):
        return None

    class Meta:
        model = m_models.GoTerm
        fields = '__all__'


class InterproIdentifierSerializer(m_serializers.DocumentSerializer,
                                   serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:interproidentifier-detail',
        lookup_field='accession',
    )

    def get_analysis(self, obj):
        return None

    class Meta:
        model = m_models.InterproIdentifier
        fields = '__all__'


class KeggModuleSerializer(m_serializers.DocumentSerializer,
                            serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:keggmodule-detail',
        lookup_field='accession',
    )

    class Meta:
        model = m_models.KeggModule
        fields = '__all__'


class PfamSerializer(m_serializers.DocumentSerializer,
                            serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:pfam-detail',
        lookup_field='accession',
    )

    class Meta:
        model = m_models.PfamEntry
        fields = '__all__'



class GoTermRetriveSerializer(m_serializers.DynamicDocumentSerializer,
                              serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:goterms-detail',
        lookup_field='accession',
    )

    # analyses = relations.SerializerMethodResourceRelatedField(
    #     source='get_analyses',
    #     model=emg_models.AnalysisJob,
    #     many=True,
    #     read_only=True,
    #     related_link_view_name='emgapi_v1:goterms-analyses-list',
    #     related_link_url_kwarg='accession',
    #     related_link_lookup_field='accession'
    # )

    def get_analyses(self, obj):
        return None

    count = serializers.IntegerField(required=False)

    class Meta:
        model = m_models.GoTerm
        fields = '__all__'


class InterproIdentifierRetriveSerializer(  # NOQA
    m_serializers.DynamicDocumentSerializer,
    serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:interproidentifier-detail',
        lookup_field='accession',
    )

    # analyses = relations.SerializerMethodResourceRelatedField(
    #     source='get_analyses',
    #     model=emg_models.AnalysisJob,
    #     many=True,
    #     read_only=True,
    #     related_link_view_name='emgapi_v1:interproidentifier-analyses-list',
    #     related_link_url_kwarg='accession',
    #     related_link_lookup_field='accession'
    # )

    def get_analyses(self, obj):
        return None

    count = serializers.IntegerField(required=False)

    class Meta:
        model = m_models.InterproIdentifier
        fields = '__all__'


class KeggModuleRetrieveSerializer(
    m_serializers.DynamicDocumentSerializer,
    serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:keggmodule-detail',
        lookup_field='accession',
    )

    completeness = serializers.FloatField(required=True)
    matching_kos = serializers.ListField(required=True)
    missing_kos = serializers.ListField(required=True)

    class Meta:
        model = m_models.KeggModule
        fields = '__all__'


class PfamRetrieveSerializer(
    m_serializers.DynamicDocumentSerializer,
    serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='emgapi_v1:pfam-detail',
        lookup_field='accession',
    )

    count = serializers.IntegerField(required=True)

    class Meta:
        model = m_models.PfamEntry
        fields = '__all__'

class OrganismSerializer(m_serializers.DynamicDocumentSerializer,
                         serializers.HyperlinkedModelSerializer):

    url = emg_fields.OrganismHyperlinkedIdentityField(
        view_name='emgapi_v1:organisms-children-list',
        lookup_field='lineage',
    )

    # attributes
    # children = relations.SerializerMethodResourceRelatedField(
    #     source='get_children',
    #     model=m_models.Organism,
    #     many=True,
    #     read_only=True,
    #     related_link_view_name='emgapi_v1:organisms-children-list',
    #     related_link_url_kwarg='lineage',
    #     related_link_lookup_field='lineage',
    # )
    #
    # def get_children(self, obj):
    #     return None

    # analyses = relations.SerializerMethodResourceRelatedField(
    #     source='get_analyses',
    #     model=emg_models.AnalysisJob,
    #     many=True,
    #     read_only=True,
    #     related_link_view_name='emgapi_v1:organisms-analyses-list',
    #     related_link_url_kwarg='lineage',
    #     related_link_lookup_field='lineage'
    # )

    def get_analyses(self, obj):
        return None

    class Meta:
        model = m_models.Organism
        exclude = (
            'id',
            'ancestors',
        )


class OrganismRetriveSerializer(OrganismSerializer):

    count = serializers.IntegerField(required=False)

    class Meta:
        model = m_models.Organism
        exclude = (
            'id',
            'ancestors',
        )
