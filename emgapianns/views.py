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
import urllib

from django.db.models import Q
from mongoengine.queryset.visitor import Q as M_Q

from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response

from emgapi import serializers as emg_serializers
from emgapi import models as emg_models
from emgapi import filters as emg_filters

from . import serializers as m_serializers
from . import models as m_models
from . import pagination as m_page
from . import viewsets as m_viewsets
from . import mixins as m_mixins


logger = logging.getLogger(__name__)


class GoTermViewSet(m_viewsets.ReadOnlyModelViewSet):

    """
    Provides list of GO terms.
    """

    serializer_class = m_serializers.GoTermSerializer

    lookup_field = 'accession'
    lookup_value_regex = 'GO:[0-9]+'

    def get_queryset(self):
        return m_models.GoTerm.objects.all()

    def get_object(self):
        try:
            accession = self.kwargs[self.lookup_field]
            return m_models.GoTerm.objects.get(accession=accession)
        except KeyError:
            raise Http404(("Attribute error '%s'." % self.lookup_field))
        except m_models.GoTerm.DoesNotExist:
            raise Http404(('No %s matches the given query.' %
                           m_models.GoTerm.__class__.__name__))

    def get_serializer_class(self):
        return super(GoTermViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of GO terms
        Example:
        ---
        `/annotations/go-terms`
        """
        return super(GoTermViewSet, self) \
            .list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves GO term
        Example:
        ---
        `/annotations/go-terms/GO:009579`
        """
        return super(GoTermViewSet, self) \
            .retrieve(request, *args, **kwargs)


class InterproIdentifierViewSet(m_viewsets.ReadOnlyModelViewSet):

    """
    Provides list of InterPro identifiers.
    """

    serializer_class = m_serializers.InterproIdentifierSerializer

    lookup_field = 'accession'
    lookup_value_regex = 'IPR[0-9]+'

    def get_queryset(self):
        return m_models.InterproIdentifier.objects.all()

    def get_object(self):
        try:
            accession = self.kwargs[self.lookup_field]
            return m_models.InterproIdentifier.objects.get(accession=accession)
        except KeyError:
            raise Http404(("Attribute error '%s'." % self.lookup_field))
        except m_models.InterproIdentifier.DoesNotExist:
            raise Http404(('No %s matches the given query.' %
                           m_models.GoTerm.__class__.__name__))

    def get_serializer_class(self):
        return super(InterproIdentifierViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of InterPro identifier
        Example:
        ---
        `/annotations/interpro-identifier`
        """
        return super(InterproIdentifierViewSet, self) \
            .list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves InterPro identifier
        Example:
        ---
        `/annotations/interpro-identifier/IPR020405`
        """
        return super(InterproIdentifierViewSet, self) \
            .retrieve(request, *args, **kwargs)


class GoTermAnalysisRelationshipViewSet(m_viewsets.ListReadOnlyModelViewSet):

    serializer_class = emg_serializers.AnalysisSerializer

    filter_class = emg_filters.AnalysisJobFilter

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
        '@sample__metadata__var_val_ucv',
    )

    lookup_field = 'accession'

    def get_queryset(self):
        accession = self.kwargs[self.lookup_field]
        try:
            annotation = m_models.GoTerm.objects.get(accession=accession)
        except KeyError:
            raise Http404(("Attribute error '%s'." % self.lookup_field))
        except m_models.GoTerm.DoesNotExist:
            raise Http404(('No %s matches the given query.' %
                           m_models.GoTerm.__class__.__name__))
        logger.info("get accession %s" % annotation.accession)
        job_ids = m_models.AnalysisJobGoTerm.objects \
            .filter(
                M_Q(go_slim__go_term=annotation) |
                M_Q(go_terms__go_term=annotation)
            ) \
            .distinct('job_id')
        logger.info("Found %d analysis" % len(job_ids))
        return emg_models.AnalysisJob.objects \
            .filter(job_id__in=job_ids) \
            .available(self.request)

    def get_serializer_class(self):
        return emg_serializers.AnalysisSerializer

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of analysis results for the given GO term
        Example:
        ---
        `/annotations/go-terms/GO:009579/analyses`
        """
        return super(GoTermAnalysisRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class InterproIdentifierAnalysisRelationshipViewSet(  # NOQA
    m_viewsets.ListReadOnlyModelViewSet):

    serializer_class = emg_serializers.AnalysisSerializer

    filter_class = emg_filters.AnalysisJobFilter

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
        '@sample__metadata__var_val_ucv',
    )

    lookup_field = 'accession'

    def get_queryset(self):
        accession = self.kwargs[self.lookup_field]
        try:
            annotation = m_models.InterproIdentifier.objects \
                .get(accession=accession)
        except KeyError:
            raise Http404(("Attribute error '%s'." % self.lookup_field))
        except m_models.InterproIdentifier.DoesNotExist:
            raise Http404(('No %s matches the given query.' %
                           m_models.InterproIdentifier.__class__.__name__))
        logger.info("get identifier %s" % annotation.accession)
        job_ids = m_models.AnalysisJobInterproIdentifier.objects \
            .filter(interpro_identifiers__interpro_identifier=annotation) \
            .distinct('job_id')
        logger.info("Found %d analysis" % len(job_ids))
        return emg_models.AnalysisJob.objects \
            .filter(job_id__in=job_ids) \
            .available(self.request)

    def get_serializer_class(self):
        return emg_serializers.AnalysisSerializer

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of analysis results for the given InterPro identifier
        Example:
        ---
        `/annotations/interpro-identifier/IPR020405/analyses`
        """
        return super(InterproIdentifierAnalysisRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class AnalysisGoTermRelationshipViewSet(  # NOQA
    m_viewsets.ListReadOnlyModelViewSet):

    serializer_class = m_serializers.GoTermRetriveSerializer

    pagination_class = m_page.MaxSetPagination

    lookup_field = 'accession'

    def get_queryset(self):
        job = emg_models.AnalysisJob.objects \
            .filter(
                Q(pk=int(self.kwargs['accession'].lstrip('MGYA')))
            ) \
            .exclude(experiment_type__experiment_type='amplicon') \
            .first()

        analysis = None
        try:
            if job is not None:
                analysis = m_models.AnalysisJobGoTerm.objects \
                    .get(analysis_id=str(job.job_id))
        except m_models.AnalysisJobGoTerm.DoesNotExist:
            pass

        return getattr(analysis, 'go_terms', [])

    def list(self, request, *args, **kwargs):
        """
        Retrieves GO terms for the given accession
        Example:
        ---
        `/analyses/MGYA00102827/go-terms`
        """
        return super(AnalysisGoTermRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class AnalysisGoSlimRelationshipViewSet(  # NOQA
    m_viewsets.ListReadOnlyModelViewSet):

    serializer_class = m_serializers.GoTermRetriveSerializer

    pagination_class = m_page.MaxSetPagination

    lookup_field = 'accession'

    def get_queryset(self):
        job = emg_models.AnalysisJob.objects \
            .filter(
                Q(pk=int(self.kwargs['accession'].lstrip('MGYA')))
            ) \
            .exclude(experiment_type__experiment_type='amplicon') \
            .first()

        analysis = None
        try:
            if job is not None:
                analysis = m_models.AnalysisJobGoTerm.objects \
                    .get(analysis_id=str(job.job_id))
        except m_models.AnalysisJobGoTerm.DoesNotExist:
            pass

        return getattr(analysis, 'go_slim', [])

    def list(self, request, *args, **kwargs):
        """
        Retrieves GO slim for the given accession
        Example:
        ---
        `/analyses/MGYA00102827/go-slim`
        """
        return super(AnalysisGoSlimRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class AnalysisInterproIdentifierRelationshipViewSet(  # NOQA
    m_viewsets.ListReadOnlyModelViewSet):

    serializer_class = m_serializers.InterproIdentifierRetriveSerializer

    pagination_class = m_page.MaxSetPagination

    lookup_field = 'accession'

    def get_queryset(self):
        job = emg_models.AnalysisJob.objects \
            .filter(
                Q(pk=int(self.kwargs['accession'].lstrip('MGYA')))
            ) \
            .exclude(experiment_type__experiment_type='amplicon') \
            .first()

        analysis = None
        try:
            if job is not None:
                analysis = m_models.AnalysisJobInterproIdentifier.objects \
                    .get(analysis_id=str(job.job_id))
        except m_models.AnalysisJobInterproIdentifier.DoesNotExist:
            pass

        return getattr(analysis, 'interpro_identifiers', [])

    def list(self, request, *args, **kwargs):
        """
        Retrieves InterPro identifiers for the given accession
        Example:
        ---
        `/analyses/MGYA00102827/interpro-identifiers`
        """
        return super(AnalysisInterproIdentifierRelationshipViewSet, self) \
            .list(request, *args, **kwargs)


class OrganismViewSet(m_viewsets.ListReadOnlyModelViewSet):

    """
    Provides list of Organisms.
    """

    serializer_class = m_serializers.OrganismSerializer

    filter_backends = (
        filters.OrderingFilter,
    )

    ordering_fields = (
        'name',
        'prefix',
        'lineage',
    )

    lookup_field = 'lineage'
    lookup_value_regex = '.*'

    def get_queryset(self):
        return m_models.Organism.objects.all()

    def get_serializer_class(self):
        return super(OrganismViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of Organisms
        Example:
        ---
        `/annotations/organisms`
        """
        return super(OrganismViewSet, self) \
            .list(request, *args, **kwargs)


class OrganismTreeViewSet(m_viewsets.ListReadOnlyModelViewSet):

    """
    Provides list of Organisms.
    """

    serializer_class = m_serializers.OrganismSerializer

    filter_backends = (
        filters.OrderingFilter,
    )

    ordering_fields = (
        'name',
        'domain',
        'prefix',
        'lineage',
    )

    lookup_field = 'lineage'
    lookup_value_regex = '[^/]+'

    def get_queryset(self):
        lineage = urllib.parse.unquote(
            self.kwargs.get('lineage', None).strip())
        organism = m_models.Organism.objects \
            .filter(lineage=lineage) \
            .only('name').distinct('name')
        if len(organism) == 0:
            raise Http404(("Attribute error '%s'." % self.lookup_field))
        queryset = m_models.Organism.objects \
            .filter(M_Q(ancestors__in=organism) | M_Q(name__in=organism))
        return queryset

    def get_serializer_class(self):
        return super(OrganismTreeViewSet, self).get_serializer_class()

    def get_serializer_context(self):
        context = super(OrganismTreeViewSet, self).get_serializer_context()
        context['lineage'] = self.kwargs.get('lineage')
        return context

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of Organisms
        Example:
        ---
        `/annotations/organisms/Bacteria:Chlorobi/children`
        """
        return super(OrganismTreeViewSet, self) \
            .list(request, *args, **kwargs)


class AnalysisOrganismRelationshipViewSet(
    m_mixins.AnalysisJobTaxonomyViewSetMixin,
    m_viewsets.ListReadOnlyModelViewSet):
    """Retrieves 16SrRNA Taxonomic analysis for the given accession
    Example:
    ---
    `/analyses/MGYA00102827/taxonomy`
    ---
    """
    taxonomy_field = 'taxonomy'


class AnalysisOrganismSSURelationshipViewSet(  # NOQA
    m_mixins.AnalysisJobTaxonomyViewSetMixin,
    m_viewsets.ListReadOnlyModelViewSet):
    """Retrieves SSU Taxonomic analysis for the given accession
    Example: 
    ---
    `/analyses/MGYA00102827/taxonomy/ssu`
    ---
    """
    taxonomy_field = 'taxonomy_ssu'


class AnalysisOrganismLSURelationshipViewSet(  # NOQA
    m_mixins.AnalysisJobTaxonomyViewSetMixin,
    m_viewsets.ListReadOnlyModelViewSet):
    """Retrieves LSU Taxonomic analysis for the given accession
    Example: 
    ---
    `/analyses/MGYA00102827/taxonomy/lsu`
    ---
    """
    taxonomy_field = 'taxonomy_lsu'


class AnalysisOrganismITSOneDBRelationshipViewSet(  # NOQA
    m_mixins.AnalysisJobTaxonomyViewSetMixin,
    m_viewsets.ListReadOnlyModelViewSet):
    """Retrieves ITSoneDB Taxonomic analysis for the given accession
    Example:
    ---
    `/analyses/MGYA00102827/taxonomy/itsonedb`
    ---
    """
    taxonomy_field = 'taxonomy_itsonedb'


class AnalysisOrganismITSUniteRelationshipViewSet(  # NOQA
    m_mixins.AnalysisJobTaxonomyViewSetMixin,
    m_viewsets.ListReadOnlyModelViewSet):
    """Retrieves ITS UNITE Taxonomic analysis for the given accession
    Example: 
    ---
    `/analyses/MGYA00102827/taxonomy/itsonedb`
    ---    
    """
    taxonomy_field = 'taxonomy_itsunite'


class AnalysisTaxonomyOverview(APIView):
    """Get the counts for each taxonomic results for an analysis job.
    """

    def get(self, request, accession):
        """Get the AnalysisJob and then the AnalysisJobTaxonomy
        """        
        job = get_object_or_404(
            emg_models.AnalysisJob,
            Q(pk=int(accession.lstrip('MGYA')))
        )
        analysis = None
        try:
            analysis = m_models.AnalysisJobTaxonomy.objects \
                .get(analysis_id=str(job.job_id))
        except m_models.AnalysisJobTaxonomy.DoesNotExist:
            raise Http404

        return Response({
            'accession': analysis.accession,
            'pipeline_version': analysis.pipeline_version,
            'taxonomy_count': len(getattr(analysis, 'taxonomy', [])),
            'taxonomy_ssu_count': len(getattr(analysis, 'taxonomy_ssu', [])),
            'taxonomy_lsu_count': len(getattr(analysis, 'taxonomy_lsu', [])),
            'taxonomy_itsunite_count': len(getattr(analysis, 'taxonomy_itsunite', [])),
            'taxonomy_itsonedb_count': len(getattr(analysis, 'taxonomy_itsonedb', []))
        })


class OrganismAnalysisRelationshipViewSet(m_viewsets.ListReadOnlyModelViewSet):

    serializer_class = emg_serializers.AnalysisSerializer

    filter_class = emg_filters.AnalysisJobFilter

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    ordering_fields = (
        'job_id',
    )

    ordering = ('-job_id',)

    search_fields = (
        '@sample__metadata__var_val_ucv',
    )

    lookup_field = 'lineage'

    def get_queryset(self):
        lineage = urllib.parse.unquote(
            self.kwargs.get(self.lookup_field, None).strip())
        organism = m_models.Organism.objects.filter(lineage=lineage) \
            .only('id')
        if len(organism) == 0:
            raise Http404(("Attribute error '%s'." % self.lookup_field))
        job_ids = m_models.AnalysisJobTaxonomy.objects \
            .filter(
                M_Q(taxonomy__organism__in=organism) |
                M_Q(taxonomy_lsu__organism__in=organism) |
                M_Q(taxonomy_ssu__organism__in=organism)
            ).distinct('job_id')
        return emg_models.AnalysisJob.objects \
            .filter(job_id__in=job_ids) \
            .available(self.request)

    def get_serializer_class(self):
        return emg_serializers.AnalysisSerializer

    def list(self, request, *args, **kwargs):
        """
        Retrieves list of analysis results for the given Organism
        Example:
        ---
        `/annotations/organisms/Bacteria:Chlorobi:OPB56/analysis`
        """

        return super(OrganismAnalysisRelationshipViewSet, self) \
            .list(request, *args, **kwargs)
