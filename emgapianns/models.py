#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2019 EMBL - European Bioinformatics Institute
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

import mongoengine


# Annotations model

class BaseAnnotation(mongoengine.DynamicDocument):

    accession = mongoengine.StringField(primary_key=True, required=True)
    description = mongoengine.StringField(required=True)

    meta = {
        'abstract': True,
    }


class GoTerm(BaseAnnotation):

    lineage = mongoengine.StringField(required=True)


class InterproIdentifier(BaseAnnotation):
    pass


class KeggModule(BaseAnnotation):
    """KEGG MODULE.
    KEGG MODULE is a collection of manually defined functional units, called KEGG modules and identified 
    by the M numbers, used for annotation and biological interpretation of sequenced genomes. 
    There are three types of KEGG modules:

    pathway modules – representing tight functional units in KEGG metabolic pathway maps, 
                      such as M00002 (Glycolysis, core module involving three-carbon compounds)
    structural complexes – often forming molecular machineries, such as M00144 (NADH:quinone oxidoreductase, prokaryotes)
    functional sets – other types of functional units, especially those that can be used to infer 
                      phenotypes, such as M00363 (EHEC pathogenicity signature, Shiga toxin)

    For more information: https://www.genome.jp/kegg/module.html  
    """
    name = mongoengine.StringField(required=True)


class PfamEntry(BaseAnnotation):
    """PfamEntry entry
    For more information: https://pfam.xfam.org/
    """
    pass


class KeggOrtholog(BaseAnnotation):
    """KEGG Ortholog (KO)
    """
    pass


class GenomeProperty(BaseAnnotation):
    """Genome property
    """
    pass


class BaseAnalysisJobAnnotation(mongoengine.EmbeddedDocument):

    count = mongoengine.IntField(required=True)

    meta = {
        'abstract': True,
    }


class AnalysisJobGoTermAnnotation(BaseAnalysisJobAnnotation):

    go_term = mongoengine.ReferenceField(GoTerm, required=True)

    @property
    def accession(self):
        return self.go_term.accession

    @property
    def description(self):
        return self.go_term.description

    @property
    def lineage(self):
        return self.go_term.lineage


class AnalysisJobInterproIdentifierAnnotation(BaseAnalysisJobAnnotation):

    interpro_identifier = mongoengine.ReferenceField(InterproIdentifier,
                                                     required=True)

    @property
    def accession(self):
        return self.interpro_identifier.accession

    @property
    def description(self):
        return self.interpro_identifier.description

    @property
    def lineage(self):
        return self.interpro_identifier.lineage


class AnalysisJobKeggModuleAnnotation(mongoengine.EmbeddedDocument):
    """KEGG modules on a given Analysis Job.
    """
    module = mongoengine.ReferenceField(KeggModule, required=True)
    completeness = mongoengine.FloatField(default=0.0)
    matching_kos = mongoengine.ListField(mongoengine.StringField(), default=list)
    missing_kos = mongoengine.ListField(mongoengine.StringField(), default=list)

    @property
    def accession(self):
        return self.module.accession

    @property
    def description(self):
        return self.module.description

    @property
    def name(self):
        return self.module.name


class AnalysisJobPfamAnnotation(BaseAnalysisJobAnnotation):
    """PFam on a given Analysis Job.
    """
    pfam_entry = mongoengine.ReferenceField(PfamEntry, required=True)

    @property
    def accession(self):
        return self.pfam_entry.accession

    @property
    def description(self):
        return self.pfam_entry.description


class AnalysisJobGenomePropAnnotation(BaseAnalysisJobAnnotation):
    """GenomeProperty on a given Analysis Job.
    """
    genome_property = mongoengine.ReferenceField(GenomeProperty, required=True)

    @property
    def accession(self):
        return self.genome_property.accession

    @property
    def description(self):
        return self.genome_property.description


class AnalysisJobKeggOrthologAnnotation(BaseAnalysisJobAnnotation):
    """KEGG KO on a given Analysis Job.
    """
    ko = mongoengine.ReferenceField(KeggOrtholog, required=True)

    @property
    def accession(self):
        return self.ko.accession

    @property
    def description(self):
        return self.ko.description


class BaseAnalysisJob(mongoengine.Document):

    analysis_id = mongoengine.StringField(primary_key=True, required=True)
    accession = mongoengine.StringField(required=True)
    pipeline_version = mongoengine.StringField(required=True)
    job_id = mongoengine.IntField(required=True)

    meta = {
        'abstract': True,
    }


class AnalysisJobGoTerm(BaseAnalysisJob):

    go_terms = mongoengine.EmbeddedDocumentListField(
        AnalysisJobGoTermAnnotation, required=False)

    go_slim = mongoengine.EmbeddedDocumentListField(
        AnalysisJobGoTermAnnotation, required=False)


class AnalysisJobInterproIdentifier(BaseAnalysisJob):

    interpro_identifiers = mongoengine.EmbeddedDocumentListField(
        AnalysisJobInterproIdentifierAnnotation, required=False)


class AnalysisJobKeggModule(BaseAnalysisJob):
    """KEGG module annotations.
    """
    kegg_modules = mongoengine.EmbeddedDocumentListField(
        AnalysisJobKeggModuleAnnotation, required=False)


class AnalysisJobPfam(BaseAnalysisJob):
    """Pfam entries for an analysis
    """
    pfam_entries = mongoengine.SortedListField(
        mongoengine.EmbeddedDocumentField(AnalysisJobPfamAnnotation),
        required=False, ordering='count', reverse=True)


class AnalysisJobKeggOrtholog(BaseAnalysisJob):
    """KeggOrtholog entries for an analysis
    """
    ko_entries = mongoengine.SortedListField(
        mongoengine.EmbeddedDocumentField(AnalysisJobKeggOrthologAnnotation),
        required=False, ordering='count', reverse=True)


class AnalysisJobGenomeProperty(BaseAnalysisJob):
    """Genome properties for an analysis
    """
    genome_properties = mongoengine.SortedListField(
        mongoengine.EmbeddedDocumentField(AnalysisJobGenomePropAnnotation),
        required=False, ordering='count', reverse=True)


class Organism(mongoengine.Document):
    """Taxonomic model
    """
    id = mongoengine.StringField(primary_key=True)
    lineage = mongoengine.StringField(required=True)
    ancestors = mongoengine.ListField(mongoengine.StringField(), default=list)
    hierarchy = mongoengine.DictField()
    domain = mongoengine.StringField()
    name = mongoengine.StringField()
    parent = mongoengine.StringField()
    rank = mongoengine.StringField()
    pipeline_version = mongoengine.StringField(required=True)

    meta = {
        'ordering': ['lineage']
    }


class AnalysisJobOrganism(mongoengine.EmbeddedDocument):

    count = mongoengine.IntField(required=True)
    organism = mongoengine.ReferenceField(Organism)

    @property
    def lineage(self):
        return self.organism.lineage

    @property
    def ancestors(self):
        return self.organism.ancestors

    @property
    def hierarchy(self):
        return self.organism.hierarchy

    @property
    def domain(self):
        return self.organism.domain

    @property
    def name(self):
        return self.organism.name

    @property
    def parent(self):
        return self.organism.parent

    @property
    def rank(self):
        return self.organism.rank

    @property
    def pipeline_version(self):
        return self.organism.pipeline_version


class AnalysisJobTaxonomy(mongoengine.Document):

    analysis_id = mongoengine.StringField(primary_key=True)
    accession = mongoengine.StringField(required=True)
    pipeline_version = mongoengine.StringField(required=True)
    job_id = mongoengine.IntField(required=True)

    taxonomy = mongoengine.EmbeddedDocumentListField(
        AnalysisJobOrganism, required=False)
    taxonomy_lsu = mongoengine.EmbeddedDocumentListField(
        AnalysisJobOrganism, required=False)
    taxonomy_ssu = mongoengine.EmbeddedDocumentListField(
            AnalysisJobOrganism, required=False)
    taxonomy_itsonedb = mongoengine.EmbeddedDocumentListField(
            AnalysisJobOrganism, required=False)
    taxonomy_itsunite = mongoengine.EmbeddedDocumentListField(
            AnalysisJobOrganism, required=False)
