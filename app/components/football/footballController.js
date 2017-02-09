angular.module("notificationApp.controllers").
controller("FootballController", function($scope, $interval, $location, $anchorScroll, $timeout, footballFactory) {

  $scope.currentTeam = footballFactory.getCurrentTeam();

  $scope.rowClick = function(inputTeam, elementID) {
    $scope.currentTeam = inputTeam;
    footballFactory.setCurrentTeam(inputTeam);
    $scope.scrollToTeam(elementID);
    $scope.updateFixtures();
  };

  $scope.getCSSClass = function(inputTeam) {
    return footballFactory.getCSSClass(inputTeam);
  }

  $scope.updateLeagueTable = function() {
    footballFactory.getLeagues().then(function(response) {
      footballFactory.getLeagueTable(response).then(function(response) {
        $scope.leagueTableData = response.data;
      });
    });
  };

  $scope.scrollToTeam = function(elementID) {
    var id = $location.hash();
    if (elementID > 2)
      $location.hash("team" + (elementID - 2));
    else {
      $location.hash(elementID);
    }
    $anchorScroll();
    $location.hash(id);
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
    footballFactory.clearCache();
    $scope.updateFixtures();
    $scope.updateLeagueTable();
  }, 43200000);

});
