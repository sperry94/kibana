define(function (require) {
   
    var app = require('modules').get('app/dashboard');
    require('plugins/dashboard/components/modal/validators');
    require('plugins/dashboard/components/modal/kbnIndexService');
    require('plugins/dashboard/components/modal/ElasticSearchFields');
    
    var moment = require('moment');
    var angular = require('angular');
    var _ = require('lodash');
    
    app.controller('SaveRuleController', function ($scope, $modalInstance, $http, query, formValidators, Restangular, ejsResource, kbnIndex, elasticSearchFields) {
        $scope.init = function(query){
           $scope.ejs = ejsResource('https://' + window.location.hostname);
           $scope.elasticSearchFields = elasticSearchFields;
           $scope.validators = formValidators;
           
           $scope.savableRule = {
              state: 'unsaved'
           };

           if (query.query_string.query && query.query_string.query !== '*') {
              $scope.savableRule.queryObj = query;
              $scope.savableRule.query = query.query_string.query;
           }
        };
        
        $scope.init(query);
        
         $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
         };

         $scope.openConfirmSaveRuleModal = function(rule, form) {
            var from = moment().subtract('days', 1).toDate(),
                to = moment().toDate();

            $scope.savableRule.state = 'unconfirmed';
            $scope.savableRule.loading = true;
            console.log('form', form);
            form.$setPristine();

            kbnIndex.indices(from, to, '[network_]YYYY_MM_DD', 'day')
               .then(
                  function(indices) {
                     $scope.ejs.Request()
                        .indices(indices)
                        .facet(
                           $scope.ejs.QueryFacet('rules')
                           .query(
                              $scope.ejs.FilteredQuery(
                                 $scope.ejs.QueryStringQuery($scope.elasticSearchFields.convertQuery(rule.query)),
                                 $scope.ejs.RangeFilter('TimeUpdated')
                                    .from(from)
                                    .to(to)
                              )
                           )
                        )
                        .doSearch()
                        .then(
                           function(result) {
                              $scope.savableRule.loading = false;

                              if (result && result.facets && result.facets.rules && result.facets.rules.count !== undefined) {
                                 $scope.savableRule.numMatches = result.facets.rules.count;
                              } else {
                                 $scope.savableRule.state = 'error';
                                 $scope.savableRule.error = 'There was a problem executing your search.';
                              }
                           },
                           function() {
                              $scope.savableRule.loading = false;
                              $scope.savableRule.state = 'error';
                              $scope.savableRule.error = 'There was a problem executing your search.';
                           }
                        );
                  },
                  function() {
                     $scope.savableRule.loading = false;
                     $scope.savableRule.state = 'error';
                     $scope.savableRule.error = 'There was a problem executing your search.';
                  }
               );
         };

        $scope.saveRule = function(rule) {
            rule.query = $scope.elasticSearchFields.convertQuery(rule.query);

            var query = $scope.ejs.QueryStringQuery(rule.query);

            rule.loading = true;
           Restangular
              .all('rules/')
              .post({
                 name: rule.name,
                 enabled: true,
                 severity: rule.severity,
                 query: angular.fromJson(query.toString())
              })
              .then(
                 function(data) {
                   if (!data.error){
                     $scope.savableRule = angular.copy(data);
                     $scope.savableRule.state = 'saved';
                     $scope.savableRule.loading = false;
                   } else{
                     $scope.savableRule = {
                           loading: false,
                           state: 'error',
                           error: data.message
                     };
                   }
                 },
                function() {
                   $scope.savableRule = {
                      loading: false,
                      state: 'error',
                      error: 'There was a problem saving your rule.'
                   };
              });
           };
      });
  });
