angular.module('notificationApp.weatherController', []).
controller('weatherController', function($scope, $http, $interval, UserConfig, weatherFactory) {

    $scope.updateCurrentWeather = function() {
        weatherFactory.getCurrentWeather().then(function(response) {
            $scope.currentWeatherData = response.data;
        });
    };

    $scope.updateForecast = function() {
        weatherFactory.getForecast().then(function(response) {
            $scope.forecastWeatherData = response.data;
        });
    };

    $scope.updateCurrentWeather();
    $scope.updateForecast();
    $interval(function() {
        $scope.updateCurrentWeather();
        $scope.updateForecast();
    }, 1800000);

    $scope.getWeatherIcon = function(weatherString) {
        return weatherFactory.translateWeatherIcon(weatherString);
    }

});
