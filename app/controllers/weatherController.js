angular.module('notificationApp.weatherController', []).
controller('weatherController', function($scope, $http, $timeout, APIkeys) {

    $scope.$watch('weatherCity', function() {
        $scope.getCurrentWeather();
        $scope.getForecast();
    });

    $scope.reSize = function(str) {
        var charWidth = 20;
        return {
            "width": (str.length + 1) * charWidth + "px"
        };
    };

    $scope.weatherCity = "Calgary";
    $scope.weatherCountry = "Canada";

    // Function to get the data
    $scope.getCurrentWeather = function() {
        $http({
            method: 'GET',
            url: 'http://api.wunderground.com/api/' + APIkeys.weatherAPIkey + '/conditions/q/' + $scope.weatherCountry + '/' + $scope.weatherCity + '.json',
        }).then(function(response) {
            $scope.currentWeatherData = angular.fromJson(response.data);
        });
    };

    $scope.getForecast = function() {
        $http({
            method: 'GET',
            url: 'http://api.wunderground.com/api/' + APIkeys.weatherAPIkey + '/forecast/q/' + $scope.weatherCountry + '/' + $scope.weatherCity + '.json',
        }).then(function(response) {
            $scope.forecastWeatherData = angular.fromJson(response.data);
        });
    };
    // Function to replicate setInterval using $timeout service.
    $scope.intervalFunction = function() {
        $scope.getCurrentWeather();
        $scope.getForecast();
        $timeout(function() {

            $scope.intervalFunction();
        }, 1800000)
    };

    // Kick off the interval
    $scope.intervalFunction();

    function determineFutureForecast(forecastWeatherData) {
        var date = new Date();
        var count = 0;
        var forecastDate;

        switch (true) {
            case (date.getHours() <= 6 || date.getHours() > 19):
                do {
                    forecastDate = new Date(forecastWeatherData.list[count].dt * 1000);
                    count++;
                } while (forecastDate.getHours() != 9)
                return "Expect " + forecastWeatherData.list[count].weather[0].description + " in the morning";
                break;

            case (date.getHours() > 6 && date.getHours() <= 13):
                do {
                    forecastDate = new Date(forecastWeatherData.list[count].dt * 1000);
                    count++;
                } while (forecastDate.getHours() != 15)
                return "Expect " + forecastWeatherData.list[count].weather[0].description + " in the afternoon";
                break;

            case (date.getHours() > 13 && date.getHours() <= 19):
                do {
                    var forecastDate = new Date(forecastWeatherData.list[count].dt * 1000);
                    count++;
                } while (forecastDate.getHours() != 21)

                return "Expect " + forecastWeatherData.list[count].weather[0].description + " this evening";
                break;

            default:
                return "Error. Could not generate future forecast data";
        }
    };

});
