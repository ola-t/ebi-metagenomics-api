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

from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework import filters

from . import models as emg_models
from . import serializers as emg_serializers
from . import filters as emg_filters
from . import mixins as emg_mixins


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
    )


class BiomeStudyRelationshipViewSet(mixins.ListModelMixin,
                                    BaseStudyRelationshipViewSet):

    lookup_field = 'lineage'

    def get_queryset(self):
        lineage = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Biome, lineage=lineage)
        studies = emg_models.Sample.objects \
            .available(self.request) \
            .filter(
                biome__lft__gte=obj.lft, biome__rgt__lte=obj.rgt,
                biome__depth__gte=obj.depth) \
            .values('study_id')
        queryset = emg_models.Study.objects \
            .available(self.request) \
            .filter(study_id__in=studies)
        if 'samples' in self.request.GET.get('include', '').split(','):
            _qs = emg_models.Sample.objects \
                .available(self.request) \
                .select_related('biome')
            queryset = queryset.prefetch_related(
                Prefetch('samples', queryset=_qs))
        return queryset

    def list(self, request, lineage, *args, **kwargs):
        """
        Retrieves list of studies for the given biome
        Example:
        ---
        `/biomes/root:Environmental:Aquatic/studies` retrieve linked
        studies

        `/biomes/root:Environmental:Aquatic/studies?include=samples` with
        studies
        """
        return super(BiomeStudyRelationshipViewSet, self) \
            .list(request, lineage, *args, **kwargs)


class PublicationStudyRelationshipViewSet(mixins.ListModelMixin,
                                          BaseStudyRelationshipViewSet):

    """
    Publications endpoint provides access to the publications linked to
    metagenomic studies. Related studies can be filtered by many of attributes
    or searched by: name, abstract, centre name, author, etc.
    """

    lookup_field = 'pubmed_id'
    lookup_value_regex = '[0-9\.]+'

    def get_queryset(self):
        pubmed_id = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Publication, pubmed_id=pubmed_id)
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

    def list(self, request, pubmed_id, *args, **kwargs):
        """
        Retrieves list of studies for the given Pubmed ID
        Example:
        ---
        `/publications/{pubmed}/studies` retrieve linked
        studies

        `/publications/{pubmed}/studies?include=samples` with
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
        `/studies/SRP001634/samples` retrieve linked samples

        `/studies/SRP001634/samples?include=runs` with runs

        Filter by:
        ---
        `/studies/ERP009004/samples?biome=root%3AEnvironmental%3AAquatic`
        filtered by biome

        `/studies/ERP009004/samples?geo_loc_name=Alberta` filtered by
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
        `/pipeline/3.0/samples` retrieve linked samples

        `/pipeline/3.0/samples?include=runs` with runs

        Filter by:
        ---
        `/pipeline/3.0/samples?biome=root%3AEnvironmental%3AAquatic`
        filtered by biome

        `/pipeline/3.0/samples?geo_loc_name=Alberta` filtered by
        localtion
        """
        return super(PipelineSampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class ExperimentSampleRelationshipViewSet(mixins.ListModelMixin,
                                          BaseSampleRelationshipViewSet):

    """
    Experiment types endpoint provides access to the metagenomic studies
    filteres by various type of experiments. Studies or samples can be
    filtered by many attributes including metadata.
    """

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
        `/experiments/metagenomic/samples` retrieve linked samples

        `/experiments/metagenomic/samples?include=runs` with runs

        Filter by:
        ---
        `/experiments/metagenomic/samples?biome=root%3AEnvironmental
        %3AAquatic` filtered by biome

        `/experiments/metagenomic/samples?geo_loc_name=Alberta`
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
        queryset = emg_models.Sample.objects \
            .available(self.request) \
            .filter(
                biome__lft__gte=obj.lft, biome__rgt__lte=obj.rgt,
                biome__depth__gte=obj.depth) \
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
        `/biomes/root:Environmental:Aquatic/samples` retrieve linked
        samples

        `/biomes/root:Environmental:Aquatic/samples?include=runs` with
        runs

        Filter by:
        ---
        `/biomes/root:Environmental:Aquatic/samples?geo_loc_name=Alberta`
        filtered by localtion

        """
        return super(BiomeSampleRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class PublicationSampleRelationshipViewSet(mixins.ListModelMixin,
                                           BaseSampleRelationshipViewSet):

    lookup_field = 'pubmed_id'
    lookup_value_regex = '[0-9\.]+'

    def get_queryset(self):
        pubmed_id = self.kwargs[self.lookup_field]
        obj = get_object_or_404(emg_models.Publication, pubmed_id=pubmed_id)
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

    def list(self, request, pubmed_id, *args, **kwargs):
        """
        Retrieves list of studies for the given Pubmed ID
        Example:
        ---
        `/publications/{pubmed}/samples` retrieve linked
        samples

        `/publications/{pubmed}/samples?include=runs` with
        runs
        """
        return super(PublicationSampleRelationshipViewSet, self) \
            .list(request, pubmed_id, *args, **kwargs)


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
        `/samples/ERS1015417/runs`

        Filter by:
        ---
        `/samples/ERS1015417/runs?experiment_type=metagenomics`
        """
        return super(SampleRunRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class BiomeTreeViewSet(mixins.ListModelMixin,
                       viewsets.GenericViewSet):

    serializer_class = emg_serializers.BiomeSerializer
    queryset = emg_models.Biome.objects.filter(depth=1)

    filter_class = emg_filters.BiomeFilter

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'lineage',
    )
    ordering = ('biome_id',)

    lookup_field = 'lineage'
    lookup_value_regex = '[a-zA-Z0-9\:\-\s\(\)\<\>]+'

    def get_queryset(self):
        lineage = self.kwargs.get('lineage', None).strip()
        if lineage:
            l = get_object_or_404(emg_models.Biome, lineage=lineage)
            queryset = emg_models.Biome.objects \
                .filter(lft__gt=l.lft, rgt__lt=l.rgt,
                        depth__gt=l.depth)
        else:
            queryset = super(BiomeTreeViewSet, self).get_queryset()
        return queryset

    def get_serializer_class(self):
        return super(BiomeTreeViewSet, self).get_serializer_class()

    def get_serializer_context(self):
        context = super(BiomeTreeViewSet, self).get_serializer_context()
        context['lineage'] = self.kwargs.get('lineage')
        return context

    def list(self, request, lineage, *args, **kwargs):
        """
        Retrieves children for the given Biome node.
        Example:
        ---
        `/biomes/root:Environmental:Aquatic/children`
        list all children
        """

        return super(BiomeTreeViewSet, self) \
            .list(request, lineage, *args, **kwargs)


class PipelineToolsRelationshipViewSet(emg_mixins.MultipleFieldLookupMixin,
                                       mixins.ListModelMixin,
                                       viewsets.GenericViewSet):

    """
    Pipeline tools endpoint provides detail about the pipeline tools were used
    to analyse the data in each steps.
    """

    serializer_class = emg_serializers.PipelineToolSerializer

    lookup_field = 'release_version'
    lookup_value_regex = '[a-zA-Z0-9.]+'

    def get_queryset(self):
        release_version = self.kwargs[self.lookup_field]
        obj = get_object_or_404(
            emg_models.Pipeline, release_version=release_version)
        queryset = emg_models.PipelineTool.objects.filter(pipelines=obj)
        return queryset

    def list(self, request, release_version, *args, **kwargs):
        """
        Retrieves list of pipeline tools for the given pipeline version
        Example:
        ---
        `/pipeline/{release_version}/tools`
        """
        return super(PipelineToolsRelationshipViewSet, self) \
            .list(request, release_version, *args, **kwargs)


class RunsMetadataView(emg_mixins.MultipleFieldLookupMixin,
                       generics.ListAPIView):

    serializer_class = emg_serializers.AnalysisJobAnnSerializer

    lookup_fields = ('accession', 'release_version')

    def get_queryset(self):
        return emg_models.AnalysisJobAnn.objects.all() \
            .select_related('job', 'var') \
            .order_by('var')

    def list(self, request, accession, release_version, *args, **kwargs):
        """
        Retrieves metadatafor the given analysis job
        Example:
        ---
        `/runs/ERR1385375/3.0/metadata` retrieve metadata
        """

        queryset = emg_models.AnalysisJobAnn.objects.filter(
            job__accession=accession,
            job__pipeline__release_version=release_version) \
            .select_related('job', 'var') \
            .order_by('var')
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class SampleMetadataRelationshipViewSet(mixins.ListModelMixin,
                                        viewsets.GenericViewSet):

    serializer_class = emg_serializers.SampleAnnSerializer

    lookup_field = 'accession'

    def get_queryset(self):
        accession = self.kwargs[self.lookup_field]
        return emg_models.SampleAnn.objects.filter(
            sample__accession=accession) \
            .select_related('sample', 'var') \
            .order_by('var')

    def list(self, request, accession, *args, **kwargs):
        """
        Retrieves metadatafor the given analysis job
        Example:
        ---
        `/runs/ERR1385375/3.0/metadata` retrieve metadata
        """

        return super(SampleMetadataRelationshipViewSet, self) \
            .list(request, accession, *args, **kwargs)
