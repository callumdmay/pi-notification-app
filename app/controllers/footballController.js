angular.module('notificationApp.footballController', []).
controller('footballController', function($scope, $http, $timeout, UserConfig) {

    $scope.class = "";
    $scope.currentTeam;

    $scope.rowClick = function(inputTeam) {
        $scope.currentTeam = inputTeam;
        $scope.getFixtures();
    }

    $scope.selected = function(inputTeam) {
        if ($scope.currentTeam == inputTeam)
            return "bright";
        else
            return "";
    }

    $scope.getLeagueTable = function() {
        $http({
            method: 'GET',
            url: 'http://api.football-data.org//v1/competitions/399/leagueTable',
            headers: {
                'X-Auth-Token': UserConfig.APIkeys.footballAPIkey
            }
        }).then(function(response) {
            $scope.leagueTableData = angular.fromJson(response.data);
        });
    };

    $scope.getFixtures = function() {
        if (!$scope.currentTeam)
            return;

        $http({
            method: 'GET',
            url: $scope.currentTeam._links.team.href + '/fixtures',
            //  url: 'http://api.football-data.org/v1/teams/81/fixtures',
            headers: {
                'X-Auth-Token': UserConfig.APIkeys.footballAPIkey
            }
        }).then(function(response) {
            $scope.teamFixtures = angular.fromJson(response.data);
        });
    };

    //Function loops to fetch new data based on timeout
    $scope.intervalFunction = function() {
        $scope.getFixtures();
        $scope.getLeagueTable();
        $timeout(function() {
            $scope.intervalFunction();
        }, 43200000)
    };

    // Kick off the interval
    $scope.intervalFunction();


});
