angular.module("notificationApp.controllers").
controller("mapController", function($scope, $interval, mapFactory) {

  $scope.updateNextBus = function(){
    mapFactory.getDirections().then(function(response){
      $scope.busStatus = mapFactory.getNextBus(response);
    })
  }

  $scope.updateNextBus();
  $interval(function() {
    mapFactory.clearCache();
    $scope.updateNextBus();
  }, 300000);

});
