angular.module('whiskers', ['hostsService', 'packagesService',
                            'buildoutsService']).
  config(function($routeProvider) {
    $routeProvider.
      when('/', {controller: MainCtrl,
                 templateUrl: '/static/partials/main.html'}).
      when('/hosts', {controller: HostsCtrl,
                      templateUrl: '/static/partials/hosts.html'}).
      when('/buildouts', {controller: BuildoutsCtrl,
                          templateUrl: '/static/partials/buildouts.html'}).
      when('/packages', {controller: PackagesCtrl,
                         templateUrl: '/static/partials/packages.html'}).
      otherwise({redirectTo: '/'});

  }
);

function MainCtrl($scope, $location, $routeParams, Hosts, Packages, Buildouts) {
  $scope.hosts = Hosts.query();
  $scope.packages = Packages.query();
  $scope.buildouts = Buildouts.query();
}

function HostsCtrl($scope, $location, $routeParams, Hosts) {
  $scope.hosts = Hosts.query();
}

function BuildoutsCtrl($scope, $location, $routeParams, Buildouts) {
  $scope.buildouts = Buildouts.query();
}

function PackagesCtrl($scope, $location, $routeParams, Packages) {
  $scope.packages = Packages.query();
}
