/* This file is a duplicate of /www/probe/analyze/js/services/ElasticSearchFields.js
* TODO: figure out a way to share angular modules
*  between Kibana and NetMon
*/
define(function (require) {
    var _ = require('lodash');
    require('fieldmap');
    var app = require('modules').get('app/dashboard');
    app.factory('elasticSearchFields', function() {
          var DEFAULT_TYPE = 'networkData',
              NETWORK_DATA_FIELDS = getFieldMap(),
              FIELD_MAP = {
                // default is the "network_*" indices
                'networkData': NETWORK_DATA_FIELDS,
                // alarms is the "events_*" indices
                'alarms': _.extend({
                   'rulename': 'RuleName',
                   'ruleseverity': 'RuleSeverity'
                }, NETWORK_DATA_FIELDS),
                // rules is the "networkrules" index
                'alarmRules': {
                   'enabled': 'enabled',
                   'severity': 'severity',
                   'query': 'query',
                   'createddate': 'createdDate',
                   'lastmodifieddate': 'lastModifiedDate'
                }
              };

          var ElasticSearchFields = function() {
             this.type = DEFAULT_TYPE;
         };

          ElasticSearchFields.prototype.getType = function() {
             return this.type;
         };

          ElasticSearchFields.prototype.setType = function(type) {
             this.type = !!FIELD_MAP[type] ? type : DEFAULT_TYPE;
             return this;
         };

          ElasticSearchFields.prototype.getMap = function() {
             var type = this.getType();
             return !!FIELD_MAP[type] ? FIELD_MAP[type] : FIELD_MAP[DEFAULT_TYPE];
         };

          ElasticSearchFields.prototype.convertQuery = function(query) {
             query = typeof(query) !== 'string' ? query.toString() : query;

             var type = this.getType(),
                 fieldMap = this.getMap(type),
                 regexField = /([\w\d]+):/ig,
                 regexExists = /(_exists_:)\s*([\w\d]+)(?=\s|$)/ig,
                 regexMAC = /(DestMAC:|SrcMAC:)\s*\"([0-9a-f]{2}[:-]){5}([0-9a-f]{2}\")/i;

             function convertField(field) {
                return fieldMap[field.toLowerCase()];
             }

             query = query.replace(regexField, function(str, p1, p2) {
                var field = convertField(p1);
                return (field === undefined) ? str : field + ':';

             });
             
             query = query.replace(regexExists, function(str, p1, p2) {
                var field = convertField(p2);
                return field === undefined ? str : p1 + field;
             });

             query = query.replace(regexMAC, function(str, p1, p2) {
                var field = str.replace(p1, '').toLowerCase().trim();
                return p1 + field;
             });
             
             return query;
         };

          return new ElasticSearchFields();
       });
   });
