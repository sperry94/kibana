/* This file is a duplicate of /www/probe/analyze/js/services/ElasticSearchFields.js
* TODO: figure out a way to share angular modules
*  between Kibana and NetMon
*/
define(function (require) {
    var _ = require('lodash');
    var app = require('modules').get('app/dashboard');
    app.factory('elasticSearchFields', function($http) {
          var fieldMap = {};
          var FIELDMAP_ROUTE = "/api/metadata/fieldmap";

          var ElasticSearchFields = function() {
         };

         ElasticSearchFields.prototype.fetchMapping = function() {
            return $http.get(FIELDMAP_ROUTE).then(
               function success(response) {
                  fieldMap = response.data;
                  return response.status;
            }, function error(response) {
                  return response.status;
            });
         }


          ElasticSearchFields.prototype.convertQuery = function(query) {
             query = typeof(query) !== 'string' ? query.toString() : query;

             var regexField = /([\w\d]+):/ig;
             var regexExists = /(_exists_:)\s*([\w\d]+)(?=\s|$)/ig;
             var regexMAC = /(DestMAC:|SrcMAC:)\s*\"([0-9a-f]{2}[:-]){5}([0-9a-f]{2}\")/i;

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

   /*
   class ElasticSearchFields {
   private FIELD_MAP: any;
   private http;

   constructor($state) {
      this.http = new HTTP($state);
      this.FIELD_MAP = {};
   }

   public fetchMapping(): Promise<boolean> {
      return this.http.fetch(FIELDMAP_ROUTE).then(response => {
         return response.json().then(json => {
            if (response.status === 200) {
               this.FIELD_MAP = json;
            }
            return response.status;
         })
      });
   }

   public convertQuery(query) {
      query = typeof query !== "string" ? query.toString() : query;

      const regexField = /([\w\d]+):/ig;
      const regexExists = /(_exists_:)\s*([\w\d]+)(?=\s|$)/ig;
      const regexMAC = /(DestMAC:|SrcMAC:)\s*\"([0-9a-f]{2}[:-]){5}([0-9a-f]{2}\")/i;

      let convertField = (field) => {
         return this.FIELD_MAP[field.toLowerCase()];
      }

      query = query.replace(regexField, function(str, p1, p2) {
         const field = convertField(p1);
         return (field === undefined) ? str : field + ':';

      });

      query = query.replace(regexExists, function(str, p1, p2) {
         const field = convertField(p2);
         return field === undefined ? str : p1 + field;
      });

      query = query.replace(regexMAC, function(str, p1, p2) {
         const field = str.replace(p1, '').toLowerCase().trim();
         return p1 + field;
      });

      return query;
   }
}
*/
