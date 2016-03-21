define(function (require) {
  require('netmon_libs/custom_modules/download/services/downloadQueueManager');
  require('netmon_libs/custom_modules/download/services/fileDownloader');
  var _ = require('lodash');
  var app = require('modules').get('netmon/download');
  
  app.factory('DownloadModalManager', function ($q, $timeout, $http, Restangular,
    DownloadQueueManager, fileDownloader) {
    var manager = {};
    var reconModalContent = {};
    var filesToDownload = [];
    var downloadStatus = {};
    var loadingModalContent = {
        header: 'Downloading Selected Files',
        body: 'Depending on the size of the files, this may take a few minutes',
        closeButton: 'Cancel Download',
        isLoadingModal: true,
        headerClass: ''
    };
    var downloadSuccessModalContent = {
        header: 'Success',
        body: 'File download complete.',
        closeButton: 'Close',
        isLoadingModal: false,
        headerClass: 'alert alert-success'
    };
    
    var downloadSettings = {
      prepareCallback: function (url) { 
          _.each(filesToDownload, function(session){
            downloadStatus[session] = {status: 'waiting'};
          });
         manager.setReconModalContent(loadingModalContent);
         console.log('show reconstructor modal')
        //  $('#pcap-reconstructor-modal').modal('show');
        //  $('#pcap-reconstructor-modal').data('modal').isShown = false;
      },
      progressCallback: function (status) {
         downloadStatus = status;
      },
      successCallback: function (status) { 
         downloadStatus = status;
         manager.setReconModalContent(downloadSuccessModalContent);
        //  $('#pcap-reconstructor-modal').data('modal').isShown = true;
      },
      failCallback: function (data, status, showModal) {
        downloadStatus = status;
        if (data.header === 'Canceled'){
             _.each(downloadStatus, function(status, session){
                status.status = 'canceled';
             });
        }
         manager.setReconModalContent(
          {
            header: data.header,
            body: data.body,
            closeButton: 'Close',
            isLoadingModal: false,
            headerClass: data.class
          });
         if (showModal){
            // $('#pcap-reconstructor-modal').modal('show');
            console.log('show the download modal');
         }
        //  $('#pcap-reconstructor-modal').data('modal').isShown = true;
      },
      fileList: null
    };
     
    manager.getLoadingModalContent = function() {
        return loadingModalContent;
    };
    
    manager.getDownloadSuccessModalContent = function () {
        return downloadSuccessModalContent;
    };
    
    manager.setReconModalContent = function(modalContentObj){
        reconModalContent = modalContentObj;
    };
    
    manager.download = function(tableID, rowData) {
        var downloadQueue = DownloadQueueManager.getDownloadQueue(tableID);
        filesToDownload = [];
        downloadStatus = {};
        if (_.isEmpty(downloadQueue[tableID])) {
           filesToDownload.push(rowData._source.Session);
        } else {
            _.each(downloadQueue[tableID], function(id){
                if (!_.contains(filesToDownload, id)){
                    filesToDownload.push(id);
                }
          });
        }
        downloadSettings.fileList = filesToDownload;
        var downloadRequest = fileDownloader.get(downloadSettings, 'pcap');
};
    
    manager.downloadReconstructedFile = function(rowData) {
        downloadStatus = {};
        filesToDownload = fileDownloader.deDupeFiles(rowData._source.Filename.split(','));
        downloadSettings.fileList = filesToDownload;
        var downloadRequest = fileDownloader.get(downloadSettings, 'reconstruction', rowData._source.Session);
    };
  
    manager.formatFileNameForModal = function(fileName){
     return fileDownloader.formatFileNameForModal(fileName);
  };
    
    return manager;
 });
});