angular.module('notificationApp.footballController', []).
controller('footballController', function($scope, $interval, $timeout, footballFactory) {

    $scope.currentTeam = footballFactory.getCurrentTeam();

    $scope.rowClick = function(inputTeam) {
        $scope.currentTeam = inputTeam;
        footballFactory.setCurrentTeam(inputTeam);
        $scope.updateFixtures();
    };

    $scope.getCSSClass = function(inputTeam){
      return footballFactory.getCSSClass(inputTeam);
    }

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
