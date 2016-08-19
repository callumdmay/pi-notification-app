angular.module('notificationApp.weatherController', []).
controller('weatherController', function($scope, $http, $timeout, UserConfig) {

    $scope.currentCity = UserConfig.city;

    $scope.getCurrentWeather = function() {
        $http({
            method: 'GET',
            url: 'http://api.wunderground.com/api/' + UserConfig.APIkeys.weatherAPIkey + '/conditions/q/' + UserConfig.country + '/' + UserConfig.city + '.json',
        }).then(function(response) {
            $scope.currentWeatherData = response.data;
        });
    };

    $scope.getForecast = function() {
        $http({
            method: 'GET',
            url: 'http://api.wunderground.com/api/' + UserConfig.APIkeys.weatherAPIkey + '/forecast10day/q/' + UserConfig.country + '/' + UserConfig.city + '.json',
        }).then(function(response) {
            $scope.forecastWeatherData = response.data;
        });
    };

    //Function loops to fetch new data based on timeout
    $scope.intervalFunction = function() {
        $scope.getCurrentWeather();
        $scope.getForecast();
        $timeout(function() {
            $scope.intervalFunction();
        }, 1800000)
    };

    // Kick off the interval
    $scope.intervalFunction();

});
