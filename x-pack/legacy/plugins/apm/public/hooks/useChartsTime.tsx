/*
 * Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
 * or more contributor license agreements. Licensed under the Elastic License;
 * you may not use this file except in compliance with the Elastic License.
 */

import { useContext } from 'react';
import { ChartsTimeContext } from '../context/ChartsTimeContext';

export function useChartsTime() {
  const context = useContext(ChartsTimeContext);

  if (!context) {
    throw new Error('Missing ChartsTime context provider');
  }

  return context;
}
