
angular.module('notificationApp.weatherController', []).
controller('weatherController', function($scope, $http, $timeout) {


  // Function to get the data
  $scope.getForecast = function(){
    $http.get('http://api.openweathermap.org/data/2.5/forecast/daily?id=5913490&units=metric&&APPID=f9dbd911bc01df1d9ce563b2ba4d3209')
      .then(function(response) {
      $scope.forecastWeatherData=angular.fromJson(response.data);
    });
  };

  $scope.getCurrentWeather = function(){
    $http.get('http://api.openweathermap.org/data/2.5/weather?id=5913490&units=metric&&APPID=f9dbd911bc01df1d9ce563b2ba4d3209')
      .then(function(response) {
      $scope.currentWeatherData=angular.fromJson(response.data);
    });
  };

  // Function to replicate setInterval using $timeout service.
  $scope.intervalFunction = function(){
    $timeout(function() {
      $scope.getCurrentWeather();
      $scope.intervalFunction();
    }, 1000)
  };

  // Kick off the interval
  $scope.intervalFunction();

});
