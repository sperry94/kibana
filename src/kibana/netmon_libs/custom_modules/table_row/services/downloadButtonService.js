define(function (require) {
   
  var app = require('modules').get('app/discover');
  
  app.factory('DownloadButtonService', function ($q, $timeout, $http, ejsResource, Restangular) {
     return {
         getButtonType : function(row, fieldName) {
             if ((fieldName === 'Captured') && (row._source.Captured === true)){
                 return 'pcap';
             } else if ((fieldName === 'Attach') && 
             (row._source.Attach === true) &&
             (row._source.Captured === true)){
                 return 'file';
             } else {
                 return null;
             }
         }
     };
 });
});