angular.module('notificationApp.mapController', []).
controller('mapController', function($scope, $interval, mapFactory) {

    $scope.updateNextBus = function(){
      mapFactory.getDirections().then(function(response){
        console.log(response.data.routes[0].legs[0]);
        $scope.busStatus = mapFactory.getNextBus(response);
      })
    }

    $scope.updateNextBus();
    $interval(function() {
        mapFactory.clearCache();
        $scope.updateNextBus();
    }, 300000);

});
