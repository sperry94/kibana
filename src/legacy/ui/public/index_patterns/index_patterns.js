/*
 * THIS FILE HAS BEEN MODIFIED FROM THE ORIGINAL SOURCE
 * This comment only applies to modifications applied after the e633644c43a0a0271e0b6c32c382ce1db6b413c3 commit
 *
 * Copyright 2019 LogRhythm, Inc
 * Licensed under the LogRhythm Global End User License Agreement,
 * which can be found through this page: https://logrhythm.com/about/logrhythm-terms-and-conditions/
 */

/*
 * Licensed to Elasticsearch B.V. under one or more contributor
 * license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright
 * ownership. Elasticsearch B.V. licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { IndexPatternMissingIndices } from '../errors';
import { IndexPatternProvider } from './_index_pattern';
import { IndexPatternsPatternCacheProvider } from './_pattern_cache';
import { IndexPatternsGetProvider } from './_get';
import { FieldsFetcherProvider } from './fields_fetcher_provider';
import { fieldFormats } from '../registry/field_formats';
import { uiModules } from '../modules';
const module = uiModules.get('kibana/index_patterns');

export function IndexPatternsProvider(Private, config) {
  const self = this;

  const IndexPattern = Private(IndexPatternProvider);
  const patternCache = Private(IndexPatternsPatternCacheProvider);
  const getProvider = Private(IndexPatternsGetProvider);


  self.get = function (id) {
    if (!id) return self.make();

    const cache = patternCache.get(id);
    return cache || patternCache.set(id, self.make(id));
  };

  self.getDefault = async () => {
    const defaultIndexPatternId = config.get('defaultIndex');
    if (defaultIndexPatternId) {
      return await self.get(defaultIndexPatternId);
    }

    return null;
  };

  self.make = function (id) {
    return (new IndexPattern(id)).init(true);
  };

  self.delete = function (pattern) {
    self.getIds.clearCache();
    return pattern.destroy();
  };

  self.errors = {
    MissingIndices: IndexPatternMissingIndices
  };

  self.cache = patternCache;
  self.getIds = getProvider('id');
  self.getTitles = getProvider('attributes.title');
  self.getFields = getProvider.multiple;
  self.fieldsFetcher = Private(FieldsFetcherProvider);
  self.fieldFormats = fieldFormats;
  self.IndexPattern = IndexPattern;
}

module.service('indexPatterns', Private => Private(IndexPatternsProvider));
