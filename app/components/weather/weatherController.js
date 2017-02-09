angular.module("notificationApp.controllers").
controller("WeatherController", function($scope, $interval, $timeout, $location, weatherFactory) {

  $scope.queryCount = 0;
  $scope.updateCurrentWeather = function() {
    weatherFactory.getCurrentWeather().then(function(response) {
      $scope.queryCount++;
      $scope.currentWeatherData = response.data;
    });
  };

  $scope.updateForecast = function() {
    weatherFactory.getForecast().then(function(response) {
      $scope.queryCount++;
      $scope.forecastWeatherData = response.data;
    });
  };

  $scope.updateCurrentWeather();
  $scope.updateForecast();
  $interval(function() {
    weatherFactory.clearCache();
    $scope.updateCurrentWeather();
    $scope.updateForecast();
  }, 1800000);

  $scope.getWeatherIcon = function(weatherString) {
    return weatherFactory.translateWeatherIcon(weatherString);
  }

  $scope.startMainScreenTimeout = function() {
    $timeout(function() {
      $location.path("/");
    }, 60000);
  }
});
