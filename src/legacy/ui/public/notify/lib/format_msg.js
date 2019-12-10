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

import _ from 'lodash';
import { i18n } from '@kbn/i18n';
import { formatESMsg } from './format_es_msg';
const has = _.has;

/**
 * Formats the error message from an error object, extended elasticsearch
 * object or simple string; prepends optional second parameter to the message
 * @param  {Error|String} err
 * @param  {String} source - Prefix for message indicating source (optional)
 * @returns {string}
 */
export function formatMsg(err, source) {
  let message = '';
  if (source) {
    message += source + ': ';
  }

  const esMsg = formatESMsg(err);

  if (typeof err === 'string') {
    message += err;
  } else if (esMsg) {
    message += esMsg;
  } else if (err instanceof Error) {
    message += formatMsg.describeError(err);
  } else if (has(err, 'status') && has(err, 'data')) {
    // is an Angular $http "error object"
    if (err.status === -1) {
      // status = -1 indicates that the request was failed to reach the server
      message += i18n.translate('common.ui.notify.toaster.unavailableServerErrorMessage', {
        defaultMessage:
          'An HTTP request has failed to connect. ' +
          'Please check if the NetMon-UI server is running and that your browser has a working connection, ' +
          'or contact your system administrator.',
      });
    } else {
      message += i18n.translate('common.ui.notify.toaster.errorStatusMessage', {
        defaultMessage: 'Error {errStatus} {errStatusText}: {errMessage}',
        values: {
          errStatus: err.status,
          errStatusText: err.statusText,
          errMessage: err.data.message,
        },
      });
    }
  }

  return message;
}

formatMsg.describeError = function(err) {
  if (!err) return undefined;
  if (err.shortMessage) return err.shortMessage;
  if (err.body && err.body.message) return err.body.message;
  if (err.message) return err.message;
  return '' + err;
};
