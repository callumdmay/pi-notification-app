angular.module('notificationApp.footballController', []).
controller('footballController', function($scope, $interval, footballFactory) {

    $scope.currentTeam = footballFactory.getCurrentTeam();

    $scope.rowClick = function(inputTeam) {
        $scope.currentTeam = inputTeam;
        footballFactory.setCurrentTeam(inputTeam);
        $scope.updateFixtures();
    };

    $scope.selected = function(inputTeam) {
        return footballFactory.highlightTeam(inputTeam);
    };

    $scope.updateLeagueTable = function() {
        footballFactory.getLeagueTable().then(function(response) {
            $scope.leagueTableData = response.data;
        });
    };

    $scope.updateFixtures = function() {
        if (!$scope.currentTeam)
            return;
        footballFactory.getFixtures($scope.currentTeam).then(function(response) {
            $scope.fixtureStatus = footballFactory.getNextFixtureString(response);
        });
    };

    $scope.updateFixtures();
    $scope.updateLeagueTable();
    $interval(function() {
        footballFactory.clearCache($scope.currentTeam);
        $scope.updateFixtures();
        $scope.updateLeagueTable();
    }, 43200000);

});
