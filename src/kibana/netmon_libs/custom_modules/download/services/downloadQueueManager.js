define(function (require) {
  var _ = require('lodash');
  var angular = require('angular');
  require('plugins/dashboard/components/modal/modal');
  require('angular-bootstrap');
  var app = require('modules').get('netmon/download', ['ui.bootstrap']);
  
  app.factory('DownloadQueueManager', function ($q, $timeout, $http, Restangular) {
     var downloadQueue = {};
     var bulkChecked = {};
     var manager = {};
     var pageDirectory = {};
     var currentPage = {};
     
     manager.addToDownloadQueue = function (tableID, sessionID) {
         if (!downloadQueue[tableID]){
             downloadQueue[tableID] = [];
         }
         downloadQueue[tableID].push(sessionID);
     };
     
     manager.removeFromDownloadQueue = function(tableID, sessionID) {
         _.remove(downloadQueue[tableID], function(id){
             return (id === sessionID);
         });
     };
     
     manager.clearDownloadQueue = function(tableID) {
         downloadQueue[tableID] = [];
     };
     
     manager.getDownloadQueueByID = function (tableID) {
         return downloadQueue[tableID];
     };
     
     manager.getDownloadQueue = function () {
         return downloadQueue;
     };
    
     manager.setPageDirectory = function(tableID, pages) {
         pageDirectory[tableID] = pages;
     };
     
     manager.setCurrentPage = function(tableID, page) {
         currentPage[tableID] = page;
     };
     
     manager.toggleCaptureSelection = function(tableID, sessionKey) {
         if (!manager.isBoxChecked(tableID, sessionKey)) {
             manager.addToDownloadQueue(tableID, sessionKey);
         } else {
             manager.removeFromDownloadQueue(tableID, sessionKey);
         }
     };
     
     manager.isBoxChecked = function(tableID, sessionKey) {
         if (downloadQueue[tableID]) {
             return _.contains(downloadQueue[tableID], sessionKey);
         }
         return false;
     };
     
     manager.getCheckedSessions = function(tableID) {
         console.log('checked: ', downloadQueue[tableID]);
     };

     manager.isBulkChecked = function(tableID) {
         if (bulkChecked[tableID]){
             return bulkChecked[tableID];
         }
         return false;
     };
     
     manager.checkBulk = function(tableID) {
         if (!bulkChecked[tableID]){
             bulkChecked[tableID] = {};
         }
         bulkChecked[tableID] = true;
     };
     
     manager.unCheckBulk = function(tableID) {
         if (!bulkChecked[tableID]){
             bulkChecked[tableID] = {};
         }
         manager.clearDownloadQueue(tableID);
         bulkChecked[tableID] = false;
     };
     
     manager.getPageID = function(tableID) {
         return currentPage[tableID].number;
     };
     
     manager.selectAllFromCurrentPage = function(tableID) {
         _.each(currentPage[tableID], function(row){
             if (!manager.isBoxChecked(tableID, row._id)){
                 manager.addToDownloadQueue(tableID, row._id);
             }
         });
     };
     
     manager.selectAllCaptures = function(tableID) {
         downloadQueue[tableID] = [];
         _.each(pageDirectory[tableID], function(page){
             _.each(page, function(row){
                manager.addToDownloadQueue(tableID, row._id);
             });
         });
     };
     
     return manager;
 });
});