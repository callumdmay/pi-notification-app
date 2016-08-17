angular.module('notificationApp.footballController', []).
controller('footballController', function($scope, $http, $timeout) {


    $scope.getLeagueTable = function() {
        $http.get('http://api.football-data.org//v1/competitions/399/leagueTable')
            .then(function(response) {
                $scope.leagueTableData = angular.fromJson(response.data);
            });
    };

    $scope.getFixtures = function() {
        $http.get('http://api.football-data.org/v1/teams/81/fixtures')
            .then(function(response) {
                $scope.teamFixtures = angular.fromJson(response.data);
            });
    };

    // Function to replicate setInterval using $timeout service.
    $scope.intervalFunction = function() {
        $scope.getFixtures();
        $scope.getLeagueTable();
        $timeout(function() {
                $scope.intervalFunction();
            }, 43200000) // wait 12 hours between api queries
    };

    // Kick off the interval
    $scope.intervalFunction();


});
