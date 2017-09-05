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

import logging

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins
from rest_framework.response import Response

from rest_framework_mongoengine import viewsets as m_viewset

from emgapi import serializers as emg_serializers
from emgapi import models as emg_models
from emgapi import filters as emg_filters
from emgapi import mixins as emg_mixins

from . import serializers as m_serializers
from . import models as m_models

logger = logging.getLogger(__name__)


class GoTermViewSet(m_viewset.ReadOnlyModelViewSet):

    serializer_class = m_serializers.GoTermSerializer

    lookup_field = 'accession'
    lookup_value_regex = '[a-zA-Z0-9\:]+'

    def get_queryset(self):
        return m_models.GoTerm.objects.all()

    def get_object(self):
        accession = self.kwargs.get('accession', None)
        return m_models.GoTerm.objects(accession=accession).first()

    def get_serializer_class(self):
        return super(GoTermViewSet, self).get_serializer_class()


class InterProTermViewSet(m_viewset.ReadOnlyModelViewSet):

    serializer_class = m_serializers.InterProTermSerializer

    lookup_field = 'accession'
    lookup_value_regex = '[a-zA-Z0-9\:]+'

    def get_queryset(self):
        return m_models.InterProTerm.objects.all()

    def get_object(self):
        accession = self.kwargs.get('accession', None)
        return m_models.InterProTerm.objects(accession=accession).first()

    def get_serializer_class(self):
        return super(InterProTermViewSet, self).get_serializer_class()


class GoTermRunRelationshipViewSet(mixins.ListModelMixin,
                                   m_viewset.GenericViewSet):

    serializer_class = emg_serializers.AnalysisSerializer

    # filter_class = emg_filters.RunFilter

    filter_backends = (
        # DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'accession',
    )

    ordering = ('-accession',)

    search_fields = (
        'instrument_platform',
        'instrument_model',
        '@sample__metadata__var_val_ucv',
    )

    lookup_field = 'accession'

    def get_queryset(self):
        annotation = get_object_or_404(
            m_models.GoTerm.objects,
            accession=self.kwargs[self.lookup_field])
        run_ids = m_models.AnalysisJobGoTerm.objects \
            .filter(go_terms__go_term=annotation.pk) \
            .only('accession', 'pipeline_version')
        run_ids2 = m_models.AnalysisJobGoSlimTerm.objects \
            .filter(go_slim__go_term=annotation.pk) \
            .only('accession', 'pipeline_version')
        run_ids = [str(r.accession) for r in run_ids]
        run_ids.extend([str(r.accession) for r in run_ids2])
        queryset = emg_models.AnalysisJob.objects \
            .filter(accession__in=run_ids) \
            .available(self.request) \
            .select_related(
                'sample',
                'analysis_status',
                'experiment_type'
            )
        return queryset

    def get_serializer_class(self):
        return emg_serializers.AnalysisSerializer

    def list(self, request, accession, *args, **kwargs):
        """
        Retrieves list of runs for the given sample accession
        Example:
        ---
        `/annotations/GO:0001/runs`
        """
        return super(GoTermRunRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class InterProTermRunRelationshipViewSet(mixins.ListModelMixin,
                                         m_viewset.GenericViewSet):

    serializer_class = emg_serializers.RunSerializer

    filter_class = emg_filters.RunFilter

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'accession',
    )

    ordering = ('-accession',)

    search_fields = (
        'instrument_platform',
        'instrument_model',
        '@sample__metadata__var_val_ucv',
    )

    lookup_field = 'accession'

    def get_queryset(self):
        annotation = get_object_or_404(
            m_models.InterProTerm.objects,
            accession=self.kwargs[self.lookup_field])
        run_ids = m_models.AnalysisJobInterProTerm.objects \
            .filter(go_terms__go_term=annotation.pk) \
            .only('accession')
        run_ids = [str(r.accession) for r in run_ids]
        queryset = emg_models.Run.objects \
            .filter(accession__in=run_ids) \
            .available(self.request) \
            .select_related(
                'sample',
                'analysis_status',
                'experiment_type'
            )
        return queryset

    def get_serializer_class(self):
        return emg_serializers.RunSerializer

    def list(self, request, accession, *args, **kwargs):
        """
        Retrieves list of runs for the given sample accession
        Example:
        ---
        `/annotations/GO0001/runs`
        """
        return super(InterProTermRunRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class AnalysisGoTermRelViewSet(emg_mixins.MultipleFieldLookupMixin,
                               mixins.ListModelMixin,
                               m_viewset.GenericViewSet):

    serializer_class = m_serializers.GoTermRetriveSerializer

    lookup_fields = ('accession', 'release_version')

    def get_queryset(self):
        return emg_models.AnalysisJob.objects \
            .available(self.request) \
            .select_related(
                'sample',
                'pipeline',
                'analysis_status',
            )

    def list(self, request, accession, release_version, *args, **kwargs):
        """
        Retrieves run for the given accession and pipeline version
        Example:
        ---
        `/runs/ERR1385375/3.0/annotations`
        """

        analysis = m_models.AnalysisJobGoTerm.objects.filter(
            accession=accession, pipeline_version=release_version).first()

        ann_ids = []
        if analysis is not None:
            ann_ids = [a.go_term.pk for a in analysis.go_terms]
            ann_counts = {
                a.go_term.pk: a.count for a in analysis.go_terms
            }

        queryset = m_models.GoTerm.objects.filter(pk__in=ann_ids)

        page = self.paginate_queryset(queryset)
        for p in page:
            p.count = ann_counts[p.pk]
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class AnalysisGoSlimRelViewSet(emg_mixins.MultipleFieldLookupMixin,
                               mixins.ListModelMixin,
                               m_viewset.GenericViewSet):

    serializer_class = m_serializers.GoTermRetriveSerializer

    lookup_fields = ('accession', 'release_version')

    def get_queryset(self):
        return emg_models.AnalysisJob.objects \
            .available(self.request) \
            .select_related(
                'sample',
                'pipeline',
                'analysis_status',
            )

    def list(self, request, accession, release_version, *args, **kwargs):
        """
        Retrieves run for the given accession and pipeline version
        Example:
        ---
        `/runs/ERR1385375/3.0/annotations`
        """

        analysis = m_models.AnalysisJobGoSlimTerm.objects.filter(
            accession=accession, pipeline_version=release_version).first()

        ann_ids = []
        if analysis is not None:
            ann_ids = [a.go_term.pk for a in analysis.goslim]
            ann_counts = {
                a.go_term.pk: a.count for a in analysis.goslim
            }

        queryset = m_models.GoTerm.objects.filter(pk__in=ann_ids)

        page = self.paginate_queryset(queryset)
        for p in page:
            p.count = ann_counts[p.pk]
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class AnalysisInterProTermRelViewSet(emg_mixins.MultipleFieldLookupMixin,
                                     mixins.ListModelMixin,
                                     m_viewset.GenericViewSet):

    serializer_class = m_serializers.InterProTermRetriveSerializer

    lookup_fields = ('accession', 'release_version')

    def get_queryset(self):
        return emg_models.AnalysisJob.objects \
            .available(self.request) \
            .select_related(
                'sample',
                'pipeline',
                'analysis_status',
            )

    def list(self, request, accession, release_version, *args, **kwargs):
        """
        Retrieves run for the given accession and pipeline version
        Example:
        ---
        `/runs/ERR1385375/3.0/annotations`
        """

        analysis = m_models.AnalysisJobInterProTerm.objects.filter(
            accession=accession, pipeline_version=release_version).first()

        ann_ids = []
        if analysis is not None:
            ann_ids = [a.go_term.pk for a in analysis.go_terms]
            ann_counts = {
                a.go_term.pk: a.count for a in analysis.go_terms
            }

        queryset = m_models.InterProTerm.objects.filter(pk__in=ann_ids)

        page = self.paginate_queryset(queryset)
        for p in page:
            p.count = ann_counts[p.pk]
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)