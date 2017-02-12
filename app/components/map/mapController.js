angular.module("notificationApp.controllers").
controller("MapController", function($scope, $interval, mapFactory, UserConfig) {

  $scope.updateNextBus = function(){
    mapFactory.getDirections().then(function(response){
      $scope.busStatus = mapFactory.getNextBus(response);
    })
  }

  if (UserConfig.APIkeys.googleMapsAPIkey) {
    $scope.updateNextBus();
    $interval(function() {
      mapFactory.clearCache();
      $scope.updateNextBus();
    }, 300000);
  }
});
