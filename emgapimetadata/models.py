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

import mongoengine


class Annotation(mongoengine.Document):

    accession = mongoengine.StringField(
        required=True, max_length=20, unique_with=('description'))
    description = mongoengine.StringField(required=True, max_length=255)
    lineage = mongoengine.StringField(required=True, max_length=255)


class RunAnnotation(mongoengine.EmbeddedDocument):

    annotation = mongoengine.ReferenceField(Annotation)
    count = mongoengine.IntField(required=True)


class Run(mongoengine.Document):

    accession = mongoengine.StringField(
        required=True, max_length=20,
        unique_with=('pipeline_version'))
    pipeline_version = mongoengine.StringField(
        required=True, max_length=20,
        unique_with=('accession'))
    annotations = mongoengine.EmbeddedDocumentListField(
        RunAnnotation, required=False)