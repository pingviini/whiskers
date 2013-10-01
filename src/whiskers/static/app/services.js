angular.module('hostsService', ['ngResource']).
  factory('Hosts', function($resource) {
    var url = '/api/hosts';
    return $resource(url, {}, {
      query: {method:'GET', isArray:false}
    });
  }
);

angular.module('packagesService', ['ngResource']).
  factory('Packages', function($resource) {
    var url = '/api/packages';
    return $resource(url, {}, {
      query: {method:'GET', isArray:false}
    });
  }
);

angular.module('buildoutsService', ['ngResource']).
  factory('Buildouts', function($resource) {
    var url = '/api/buildouts';
    return $resource(url, {}, {
      query: {method:'GET', isArray:false}
    });
  }
);
