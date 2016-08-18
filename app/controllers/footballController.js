angular.module('notificationApp.footballController', []).
controller('footballController', function($scope, $http, $timeout, APIkeys) {

    $scope.getLeagueTable = function() {
        $http({
            method: 'GET',
            url: 'http://api.football-data.org//v1/competitions/399/leagueTable',
            headers: {
                'X-Auth-Token': APIkeys.footballAPIkey
            }
        }).then(function(response) {
            $scope.leagueTableData = angular.fromJson(response.data);
        });
    };

    $scope.getFixtures = function() {
        $http({
            method: 'GET',
            url: 'http://api.football-data.org/v1/teams/81/fixtures',
            headers: {
                'X-Auth-Token': APIkeys.footballAPIkey
            }
        }).then(function(response) {
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
