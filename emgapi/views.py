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

from django.conf import settings
from django.db.models import Prefetch
# from django.db.models import Count
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response

from rest_framework import filters
from rest_framework.decorators import detail_route, list_route
# from rest_framework import authentication
from rest_framework import permissions

from . import models as emg_models
from . import serializers as emg_serializers
from . import filters as emg_filters
from . import permissions as emg_perms

logger = logging.getLogger(__name__)


class MultipleFieldLookupMixin(object):

    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field
    filtering.
    Source: http://www.django-rest-framework.org/api-guide/generic-views/
    """

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs[field]:
                filter[field] = self.kwargs[field]
        return get_object_or_404(queryset, **filter)


class MyDataViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = emg_serializers.StudySerializer
    permission_classes = (
        permissions.IsAuthenticated,
        emg_perms.IsSelf,
    )

    def get_queryset(self):
        queryset = emg_models.Study.objects \
            .mydata(self.request) \
            .select_related('biome')
        return queryset

    def get_serializer_class(self):
        return super(MyDataViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieve studies owned by the logged in user
        Example:
        ---
        `/api/mydata` retrieve own studies
        """
        queryset = emg_models.Study.objects \
            .mydata(self.request) \
            .select_related('biome')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BiomeViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    serializer_class = emg_serializers.BiomeSerializer
    queryset = emg_models.Biome.objects.all()

    filter_backends = (
        filters.OrderingFilter,
    )

    ordering_fields = (
        'lineage',
    )
    ordering = ('lineage',)

    lookup_field = 'lineage'
    lookup_value_regex = '[a-zA-Z0-9\:\-\s\(\)\<\>]+'

    def get_queryset(self):
        if self.action == 'list':
            lineage = self.kwargs.get('lineage', None)
            if lineage is not None and len(lineage) > 0:
                l = get_object_or_404(emg_models.Biome, lineage=lineage)
                queryset = emg_models.Biome.objects \
                    .filter(lft__gte=l.lft-1, rgt__lte=l.rgt+1,
                            depth=l.depth+1)
            else:
                queryset = emg_models.Biome.objects.filter(depth=1)
        else:
            queryset = super(BiomeViewSet, self).get_queryset()
        return queryset

    def get_serializer_class(self):
        return super(BiomeViewSet, self).get_serializer_class()

    def get_serializer_context(self):
        context = super(BiomeViewSet, self).get_serializer_context()
        context['lineage'] = self.kwargs.get('lineage')
        return context

    def list(self, request, lineage, *args, **kwargs):
        """
        Retrieves children for the given Biome node.
        Example:
        ---
        `/api/biomes/root:Environmental:Aquatic`
        list all children
        """

        return super(BiomeViewSet, self) \
            .list(request, lineage, *args, **kwargs)


class StudyViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    serializer_class = emg_serializers.StudySerializer

    filter_class = emg_filters.StudyFilter

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'accession',
        'last_update',
        'samples_count',
        'runs_count',
    )

    ordering = ('-last_update',)

    search_fields = (
        '@study_name',
        '@study_abstract',
        'centre_name',
        'author_name',
        'author_email',
        'project_id',
    )

    lookup_field = 'accession'
    lookup_value_regex = '[a-zA-Z0-9]+'

    def get_queryset(self):
        queryset = emg_models.Study.objects \
            .available(self.request)
        if 'samples' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Sample.objects \
                .available(self.request) \
                .select_related('biome')
            queryset = queryset.prefetch_related(
                Prefetch('samples', queryset=_qs))
        if 'publications' in self.request.GET.get('include', '').split(','):
            queryset = queryset.prefetch_related(
                Prefetch(
                    'publications',
                    queryset=emg_models.Publication.objects.all()))
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return emg_serializers.RetrieveStudySerializer
        return super(StudyViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of studies
        Example:
        ---
        `/api/studies`

        `/api/studies?fields[studies]=accession,samples_count,biomes`
        retrieve only selected fileds

        `/api/studies?include=publications` with publications

        Filter by:
        ---
        `/api/studies?biome=root:Environmental:Terrestrial:Soil`

        `/api/studies?centre_name=BioProject`

        Search for:
        ---
        name, abstract, author and centre name etc.

        `/api/studies?search=microbial%20fuel%20cells`
        """

        return super(StudyViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves study for the given accession
        Example:
        ---
        `/api/studies/ERP009004` retrieve study SRP001634

        `/api/studies/ERP009004?include=samples`
        with samples
        """
        return super(StudyViewSet, self).retrieve(request, *args, **kwargs)

    @list_route(
        methods=['get', ],
        serializer_class=emg_serializers.StudySerializer
    )
    def recent(self, request):
        """
        Retrieve 20 latest studies
        Example:
        ---
        `/api/studies/recent` retrieve recent studies
        """
        limit = settings.EMG_DEFAULT_LIMIT
        queryset = emg_models.Study.objects \
            .recent(self.request)[:limit]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(
        methods=['get', ],
        url_name='publications-list',
        serializer_class=emg_serializers.PublicationSerializer
    )
    def publications(self, request, accession=None):
        """
        Retrieves list of publications for the given study accession
        Example:
        ---
        `/api/studies/SRP000183/publications` retrieve linked publications
        """

        obj = self.get_object()
        queryset = obj.publications.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(
        methods=['get', ],
        url_name='biomes-list',
        serializer_class=emg_serializers.BiomeSerializer
    )
    def biomes(self, request, accession=None):
        """
        Retrieves list of biomes for the given study accession
        Example:
        ---
        `/api/studies/ERP009004/biomes` retrieve linked samples
        """

        obj = self.get_object()
        biomes = obj.samples.values('biome_id').distinct()
        queryset = emg_models.Biome.objects \
            .filter(pk__in=biomes)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class SampleViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = emg_serializers.SampleSerializer

    filter_class = emg_filters.SampleFilter

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'accession',
        'last_update',
        'runs_count',
    )

    ordering = ('-last_update',)

    search_fields = (
        '@sample_name',
        '@sample_desc',
        'sample_alias',
        'species',
        'environment_feature',
        'environment_biome',
        'environment_feature',
        'environment_material',
        '@metadata__var_val_ucv',
    )

    lookup_field = 'accession'
    lookup_value_regex = '[a-zA-Z0-9_]+'

    def get_queryset(self):
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .prefetch_related('biome', 'study')
        if 'runs' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects \
                .available(self.request) \
                .select_related(
                    'analysis_status', 'experiment_type'
                )
            queryset = queryset.prefetch_related(
                Prefetch('runs', queryset=_qs))
        if 'study' in self.request.GET.get('include', '').split(','):
            queryset = queryset.select_related('study__biome')
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return emg_serializers.RetrieveSampleSerializer
        return super(SampleViewSet, self).get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves sample for the given accession
        Example:
        ---
        `/api/samples/ERS1015417`

        `/api/samples/ERS1015417?include=metadata` with metadata

        """
        return super(SampleViewSet, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of samples
        Example:
        ---
        `/api/samples` retrieves list of samples

        `/api/samples?fields[samples]=accession,runs_count,biome`
        retrieve only selected fileds

        `/api/samples?include=metadata,runs,study`
        with related metadata, runs and studies

        `/api/samples?ordering=accession` ordered by accession

        Filter by:
        ---
        `/api/samples?experiment_type=metagenomics`

        `/api/samples?species=sapiens`

        `/api/samples?biome=root:Environmental:Aquatic:Marine`

        Search for:
        ---
        name, descriptions, metadata, species, environment feature and material

        `/api/samples?search=continuous%20culture`

        """
        return super(SampleViewSet, self).list(request, *args, **kwargs)

    @detail_route(
        methods=['get', ],
        url_name='metadata-list',
        serializer_class=emg_serializers.SampleAnnSerializer
    )
    def metadata(self, request, accession=None):
        """
        Retrieves list of samples for the given study accession
        Example:
        ---
        `/api/samples/ERS1015417/metadata` retrieve metadata
        """

        obj = self.get_object()
        queryset = obj.metadata.all() \
            .select_related('sample', 'var') \
            .order_by('var')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


# class SampleAnnAPIView(MultipleFieldLookupMixin, generics.RetrieveAPIView):
#
#     serializer_class = emg_serializers.SampleAnnSerializer
#
#     lookup_fields = ('var__var_name', 'var_val_ucv')
#
#     def get_queryset(self):
#         return emg_models.SampleAnn.objects.all()
#
#     def get(self, request, name, value, *args, **kwargs):
#         """
#         Retrieves sample annotation for the given sample accession and value
#         Example:
#         ---
#         `/api/metadata/name/value`
#         """
#         sa = emg_models.SampleAnn.objects.get(
#             var__var_name=name,
#             var_val_ucv=value
#         )
#         serializer = self.get_serializer(sa)
#         return Response(data=serializer.data)


class SampleAnnsViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    serializer_class = emg_serializers.SampleAnnSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'sample',
        'var',
    )

    ordering = (
        'sample',
        'var',
    )

    search_fields = (
        'var__var_name',
        'var_val_ucv',
    )

    def get_queryset(self):
        queryset = emg_models.SampleAnn.objects.all()
        return queryset

    def get_serializer_class(self):
        return super(SampleAnnsViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of annotaitons
        Example:
        ---
        `/api/metadata` retrieves list of samples
        """
        return super(SampleAnnsViewSet, self).list(request, *args, **kwargs)


class RunAPIView(MultipleFieldLookupMixin, generics.RetrieveAPIView):

    serializer_class = emg_serializers.RetrieveRunSerializer

    lookup_fields = ('accession', 'release_version')

    def get_queryset(self):
        return emg_models.AnalysisJob.objects \
            .available(self.request) \
            .select_related(
                'sample',
                'pipeline',
                'analysis_status',
            )

    def get(self, request, accession, release_version, *args, **kwargs):
        """
        Retrieves run for the given accession and pipeline version
        Example:
        ---
        `/api/runs/ERR1385375/pipelines/3.0`
        """
        run = get_object_or_404(
            emg_models.AnalysisJob, accession=accession,
            pipeline__release_version=release_version)
        serializer = self.get_serializer(run)
        return Response(data=serializer.data)


class RunViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):

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
        queryset = emg_models.Run.objects
        if self.action == 'retrieve':
            queryset = queryset \
                .filter(accession=self.kwargs['accession']) \
                .distinct()
        else:
            queryset = queryset.available(self.request) \
                .prefetch_related(
                    'sample',
                    'analysis_status',
                    'experiment_type'
                )
        return queryset

    def get_serializer_class(self):
        return super(RunViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of runs
        Example:
        ---
        `/api/runs`

        `/api/runs?fields[runs]=accession,experiment_type` retrieve only
        selected fileds

        Filter by:
        ---
        `/api/runs?experiment_type=metagenomics`

        `/api/runs?biome=root:Environmental:Aquatic:Marine`
        """
        return super(RunViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves run for the given accession
        Example:
        ---
        `/api/runs/ERR1385375`
        """
        return super(RunViewSet, self).retrieve(request, *args, **kwargs)


class PipelineViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    serializer_class = emg_serializers.PipelineSerializer
    queryset = emg_models.Pipeline.objects.all()

    filter_backends = (
        filters.OrderingFilter,
    )

    ordering_fields = (
        'release_version',
    )

    ordering = ('release_version',)

    # search_fields = ()

    lookup_field = 'release_version'
    lookup_value_regex = '[a-zA-Z0-9.]+'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return emg_serializers.PipelineSerializer
        return super(PipelineViewSet, self).get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves pipeline for the given version
        Example:
        ---
        `/api/pipelines/3.0`

        `/api/pipelines/3.0?include=tools` with tools
        """
        return super(PipelineViewSet, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of pipeline versions
        Example:
        ---
        `/api/pipeline`

        `/api/pipeline?include=tools` with tools
        """
        return super(PipelineViewSet, self).list(request, *args, **kwargs)

    @detail_route(
        methods=['get', ],
        url_name='tools-list',
        serializer_class=emg_serializers.PipelineToolSerializer
    )
    def tools(self, request, release_version=None):
        """
        Retrieves list of tools for the given pipeline version
        Example:
        ---
        `/api/pipeline/tools`
        """
        obj = self.get_object()
        queryset = obj.tools.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class PipelineToolAPIView(MultipleFieldLookupMixin, generics.RetrieveAPIView):

    serializer_class = emg_serializers.PipelineToolSerializer
    queryset = emg_models.PipelineTool.objects.all()

    lookup_fields = ('tool_name', 'version')

    def get(self, request, tool_name, version, *args, **kwargs):
        """
        Retrieves pipeline tool details for the given pipeline version
        Example:
        ---
        `/api/tools/interproscan/5.19-58.0`
        """
        run = get_object_or_404(
            emg_models.PipelineTool,
            tool_name__iexact=tool_name, version=version)
        serializer = self.get_serializer(run)
        return Response(data=serializer.data)


class PipelineToolViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = emg_serializers.PipelineToolSerializer
    queryset = emg_models.PipelineTool.objects.all()

    # lookup_field = 'tool_name'
    # lookup_value_regex = '[0-9a-zA-Z\-\.]+'

    def get_serializer_class(self):
        return super(PipelineToolViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of pipeline tools
        Example:
        ---
        `/api/tools` retrieves list of pipeline tools
        """
        return super(PipelineToolViewSet, self).list(request, *args, **kwargs)


class ExperimentTypeViewSet(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):

    serializer_class = emg_serializers.ExperimentTypeSerializer
    queryset = emg_models.ExperimentType.objects.all()

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'experiment_type',
    )

    ordering = ('experiment_type',)

    lookup_field = 'experiment_type'
    lookup_value_regex = '[a-zA-Z]+'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return emg_serializers.ExperimentTypeSerializer
        return super(ExperimentTypeViewSet, self).get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves experiment type for the given id
        """
        return super(ExperimentTypeViewSet, self) \
            .retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of experiment types
        """
        return super(ExperimentTypeViewSet, self) \
            .list(request, *args, **kwargs)


class PublicationViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = emg_serializers.PublicationSerializer

    filter_class = emg_filters.PublicationFilter

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'pub_id',
        'studies_count',
    )

    ordering = ('pub_id',)

    search_fields = (
        '@pub_title',
        '@pub_abstract',
        'pub_type',
        'authors',
        'doi',
        'isbn',
    )

    lookup_field = 'pub_id'
    lookup_value_regex = '[a-zA-Z0-9,]+'

    def get_queryset(self):
        queryset = emg_models.Publication.objects.all()
        if 'studies' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects.select_related('biome')
            queryset = queryset.prefetch_related(
                Prefetch('studies', queryset=_qs))
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return emg_serializers.RetrievePublicationSerializer
        return super(PublicationViewSet, self).get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves publication for the given id
        Example:
        ---
        `/api/publications/338`

        `/api/publications/338?include=studies` with studies
        """
        return super(PublicationViewSet, self) \
            .retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of publications
        Example:
        ---
        `/api/publications` retrieves list of publications

        `/api/publications?include=studies` with studies

        `/api/publications?ordering=pub_id` ordered by id

        Search for:
        ---
        title, abstract, authors, etc.

        `/api/publications?search=text`
        """
        return super(PublicationViewSet, self).list(request, *args, **kwargs)
