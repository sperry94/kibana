define(function (require) {
    var app = require('modules').get('app/dashboard');
    app.factory('searchAuditor', function (elasticSearchFields,
                                           Restangular) {
        var previousQuery = {
            query    : "",
            fromDate : "",
            toDate   : ""
        };
        var formatQuery = function(query) {
            var _query = _.isArray(query) ? query : [query];
            if (_.isArray(_query)) {
                var count = 0;
                _.each(_query, function($q) {
                    $q = elasticSearchFields.convertQuery($q);
                    _query[count] = $q;
                    ++count;
                });

            } else {
                _query = elasticSearchFields.convertQuery(_query);
            }
            return _query;
        };
        return {
            logQuery : function(query, from, to) {
                console.log('trying to log query from logQuery');
                query = formatQuery(query)[0];

                if (!from || !to || 
                    query === "" || 
                    query === "*" || 
                    query === "+Captured:true") {
                    console.log("weird thing, query: " + query);
                    return;
                }
                var formatString = "YYYY/MM/DD HH:mm:ss";
                var from = moment(from).format(formatString);
                var to = moment(to).format(formatString);
                if (query === previousQuery.query &&
                    from === previousQuery.fromDate &&
                    to === previousQuery.toDate) {
                    return;
                }
                previousQuery = {
                    query    : query,
                    fromDate : from,
                    toDate   : to
                };
                Restangular
                    .all('audit/')
                    .post({
                        query    : query,
                        from     : from,
                        to       : to
                    })
                    .then(function(response){
                        if (response.error){
                            var error = response.message || "An unknown error occured";
                            console.log('Search Audit Error:', error);
                        }
                    });
            }
        };
    });
});
