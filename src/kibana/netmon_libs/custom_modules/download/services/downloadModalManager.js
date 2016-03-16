define(function (require) {
  var _ = require('lodash');
  var app = require('modules').get('app/discover');
  
  app.factory('DownloadModalManager', function ($q, $timeout, $http, Restangular) {
     return {
         initializeMultiCapture : function() {
             return {
                hasSelection: false,
                selectedRows: {},
                selectAllType: 'visible',
                allChecked: false,
                boxcount: 0
            };
        },
        getLodaingModalContent : function() {
            return {
                header: 'Downloading Selected Files',
                body: 'Depending on the size of the files, this may take a few minutes',
                closeButton: 'Cancel Download',
                isLoadingModal: true,
                headerClass: ''
            };
        },
        getDownloadSuccessModalContent : function () {
            return {
                header: 'Success',
                body: 'File download complete.',
                closeButton: 'Close',
                isLoadingModal: false,
                headerClass: 'alert alert-success'
            };
        }
    };
 });
});