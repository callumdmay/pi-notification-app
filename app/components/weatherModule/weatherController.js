angular.module('notificationApp').
controller('weatherController', function($scope, $interval, $timeout, $location, weatherFactory) {

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
        weatherFactory.clearCache();
        $scope.updateCurrentWeather();
        $scope.updateForecast();
    }, 1800000);

    $scope.getWeatherIcon = function(weatherString) {
        return weatherFactory.translateWeatherIcon(weatherString);
    }

    $scope.startMainScreenTimeout = function() {
        $timeout(function() {
            $location.path('/');
        }, 60000);
    }
});
