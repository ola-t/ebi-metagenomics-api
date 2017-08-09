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

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins

from rest_framework import filters

from . import models as emg_models
from . import serializers as emg_serializers
from . import filters as emg_filters


class BaseStudyRelationshipViewSet(viewsets.GenericViewSet):

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


class BiomeStudyRelationshipViewSet(mixins.ListModelMixin,
                                    BaseStudyRelationshipViewSet):

    lookup_field = 'lineage'

    def get_queryset(self):
        lineage = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Biome, lineage=lineage)
        studies = emg_models.Sample.objects \
            .available(self.request) \
            .filter(biome__lft__gte=obj.lft-1, biome__rgt__lte=obj.rgt+1) \
            .values('study_id')
        queryset = emg_models.Study.objects \
            .available(self.request) \
            .filter(biome_id__in=studies)
        if 'samples' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Sample.objects \
                .available(self.request) \
                .select_related('biome')
            queryset = queryset.prefetch_related(
                Prefetch('samples', queryset=_qs))
        return queryset

    def list(self, request, lineage, *args, **kwargs):
        """
        Retrieves list of studies for the given pipeline version
        Example:
        ---
        `/api/biomes/root:Environmental:Aquatic/studies` retrieve linked
        studies

        `/api/biomes/root:Environmental:Aquatic/studies?include=samples` with
        studies
        """
        return super(BiomeStudyRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class PublicationStudyRelationshipViewSet(mixins.ListModelMixin,
                                          BaseStudyRelationshipViewSet):

    lookup_field = 'pub_id'

    def get_queryset(self):
        pub_id = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Publication, pub_id=pub_id)
        queryset = emg_models.Study.objects \
            .available(self.request) \
            .filter(publications=obj)
        if 'samples' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Sample.objects \
                .available(self.request) \
                .select_related('biome')
            queryset = queryset.prefetch_related(
                Prefetch('samples', queryset=_qs))
        return queryset

    def list(self, request, pub_id, *args, **kwargs):
        """
        Retrieves list of studies for the given pipeline version
        Example:
        ---
        `/api/publications/338/studies` retrieve linked
        studies

        `/api/publications/338/studies?include=samples` with
        samples
        """
        return super(PublicationStudyRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class BaseSampleRelationshipViewSet(viewsets.GenericViewSet):

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


class StudySampleRelationshipViewSet(mixins.ListModelMixin,
                                     BaseSampleRelationshipViewSet):

    lookup_field = 'accession'

    def get_queryset(self):
        study = get_object_or_404(
            emg_models.Study, accession=self.kwargs[self.lookup_field])
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .filter(study_id=study.pk) \
            .prefetch_related('biome', 'study')
        if 'runs' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects \
                .available(self.request) \
                .select_related(
                    'analysis_status', 'experiment_type'
                )
            queryset = queryset.prefetch_related(
                Prefetch('runs', queryset=_qs))
        return queryset

    def list(self, request, accession, *args, **kwargs):
        """
        Retrieves list of samples for the given study accession
        Example:
        ---
        `/api/studies/SRP001634/samples` retrieve linked samples

        `/api/studies/SRP001634/samples?include=runs` with runs

        Filter by:
        ---
        `/api/studies/ERP009004/samples?biome=root%3AEnvironmental%3AAquatic`
        filtered by biome

        `/api/studies/ERP009004/samples?geo_loc_name=Alberta` filtered by
        localtion
        """
        return super(StudySampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class PipelineSampleRelationshipViewSet(mixins.ListModelMixin,
                                        BaseSampleRelationshipViewSet):

    lookup_field = 'release_version'

    def get_queryset(self):
        pipeline = get_object_or_404(
            emg_models.Pipeline,
            release_version=self.kwargs[self.lookup_field])
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .filter(analysis__pipeline=pipeline) \
            .prefetch_related('biome', 'study')
        if 'runs' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects \
                .available(self.request) \
                .select_related(
                    'analysis_status', 'experiment_type'
                )
            queryset = queryset.prefetch_related(
                Prefetch('runs', queryset=_qs))
        return queryset

    def list(self, request, release_version, *args, **kwargs):
        """
        Retrieves list of samples for the given pipeline version
        Example:
        ---
        `/api/pipeline/3.0/samples` retrieve linked samples

        `/api/pipeline/3.0/samples?include=runs` with runs

        Filter by:
        ---
        `/api/pipeline/3.0/samples?biome=root%3AEnvironmental%3AAquatic`
        filtered by biome

        `/api/pipeline/3.0/samples?geo_loc_name=Alberta` filtered by
        localtion
        """
        return super(PipelineSampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class ExperimentSampleRelationshipViewSet(mixins.ListModelMixin,
                                          BaseSampleRelationshipViewSet):

    lookup_field = 'experiment_type'

    def get_queryset(self):
        experiment_type = get_object_or_404(
            emg_models.ExperimentType,
            experiment_type=self.kwargs[self.lookup_field])
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .filter(runs__experiment_type=experiment_type) \
            .prefetch_related('biome', 'study')
        if 'runs' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects \
                .available(self.request) \
                .select_related(
                    'analysis_status', 'experiment_type'
                )
            queryset = queryset.prefetch_related(
                Prefetch('runs', queryset=_qs))
        return queryset

    def list(self, request, experiment_type, *args, **kwargs):
        """
        Retrieves list of samples for the given experiment type
        Example:
        ---
        `/api/experiments/metagenomic/samples` retrieve linked samples

        `/api/experiments/metagenomic/samples?include=runs` with runs

        Filter by:
        ---
        `/api/experiments/metagenomic/samples?biome=root%3AEnvironmental
        %3AAquatic` filtered by biome

        `/api/experiments/metagenomic/samples?geo_loc_name=Alberta`
        filtered by localtion
        """
        return super(ExperimentSampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class BiomeSampleRelationshipViewSet(mixins.ListModelMixin,
                                     BaseSampleRelationshipViewSet):

    lookup_field = 'lineage'

    def get_queryset(self):
        lineage = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Biome, lineage=lineage)
        biomes = emg_models.Biome.objects.values('biome_id') \
            .filter(lft__gte=obj.lft, rgt__lte=obj.rgt,
                    depth__gte=obj.depth)
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .filter(biome_id__in=biomes) \
            .prefetch_related('biome', 'study')
        if 'runs' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects \
                .available(self.request) \
                .select_related(
                    'analysis_status', 'experiment_type'
                )
            queryset = queryset.prefetch_related(
                Prefetch('runs', queryset=_qs))
        return queryset

    def list(self, request, lineage, *args, **kwargs):
        """
        Retrieves list of samples for the given biome
        Example:
        ---
        `/api/biomes/root:Environmental:Aquatic/samples` retrieve linked
        samples

        `/api/biomes/root:Environmental:Aquatic/samples?include=runs` with
        runs

        Filter by:
        ---
        `/api/biomes/root:Environmental:Aquatic/samples?geo_loc_name=Alberta`
        filtered by localtion

        """
        return super(BiomeSampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class PublicationSampleRelationshipViewSet(mixins.ListModelMixin,
                                           BaseSampleRelationshipViewSet):

    lookup_field = 'pub_id'

    def get_queryset(self):
        pub_id = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Publication, pub_id=pub_id)
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .filter(study__publications=obj)
        if 'runs' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Run.objects \
                .available(self.request) \
                .select_related(
                    'analysis_status', 'experiment_type'
                )
            queryset = queryset.prefetch_related(
                Prefetch('runs', queryset=_qs))
        return queryset

    def list(self, request, pub_id, *args, **kwargs):
        """
        Retrieves list of studies for the given pipeline version
        Example:
        ---
        `/api/publications/338/samples` retrieve linked
        studies

        `/api/publications/338/samples?include=runs` with
        samples
        """
        return super(PublicationSampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class SampleRunRelationshipViewSet(mixins.ListModelMixin,
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
        sample = get_object_or_404(
            emg_models.Sample, accession=self.kwargs[self.lookup_field])
        queryset = emg_models.Run.objects \
            .available(self.request) \
            .filter(sample_id=sample.pk) \
            .select_related(
                'sample',
                'analysis_status',
                'experiment_type'
            ).distinct()
        return queryset

    def get_serializer_class(self):
        return emg_serializers.RunSerializer

    def list(self, request, accession, *args, **kwargs):
        """
        Retrieves list of runs for the given sample accession
        Example:
        ---
        `/api/samples/ERS1015417/runs`

        Filter by:
        ---
        `/api/samples/ERS1015417/runs?experiment_type=metagenomics`
        """
        return super(SampleRunRelationshipViewSet, self) \
            .list(request, *args, **kwargs)