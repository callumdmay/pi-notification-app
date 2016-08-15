angular.module('notificationApp.weatherController', []).
controller('weatherController', function($scope, $http, $timeout) {


    // Function to get the data
    $scope.getForecast = function() {
        $http.get('http://api.openweathermap.org/data/2.5/forecast?id=5913490&units=metric&&APPID=f9dbd911bc01df1d9ce563b2ba4d3209')
            .then(function(response) {
                $scope.forecastWeatherData = angular.fromJson(response.data);
                determineFutureForecast($scope.forecastWeatherData);
            });
    };

    $scope.getCurrentWeather = function() {
        $http.get('http://api.openweathermap.org/data/2.5/weather?id=5913490&units=metric&&APPID=f9dbd911bc01df1d9ce563b2ba4d3209')
            .then(function(response) {
                $scope.currentWeatherData = angular.fromJson(response.data);
            });
    };

    // Function to replicate setInterval using $timeout service.
    $scope.intervalFunction = function() {
        $timeout(function() {
            $scope.getCurrentWeather();
            $scope.getForecast();
            $scope.intervalFunction();
        }, 1000)
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
                $scope.forecastSentence = "Expect " + forecastWeatherData.list[count].weather[0].description + " in the morning";
                break;

            case (date.getHours() > 6 && date.getHours() <= 13):
                do {
                    forecastDate = new Date(forecastWeatherData.list[count].dt * 1000);
                    count++;
                } while (forecastDate.getHours() != 15)
                $scope.forecastSentence = "Expect " + forecastWeatherData.list[count].weather[0].description + " in the afternoon";
                break;

            case (date.getHours() > 13 && date.getHours() <= 19):
                do {
                    var forecastDate = new Date(forecastWeatherData.list[count].dt * 1000);
                    count++;
                } while (forecastDate.getHours() != 21)

                // $scope.forecastSentence = "Future night forecast at " + Date(forecastWeatherData.list[count].dt * 1000).toString() + "is" + forecastWeatherData.list[count].weather.description;
                $scope.forecastSentence = "Expect " + forecastWeatherData.list[count].weather[0].description + " this evening";
                break;

            default:
                $scope.forecastSentence = "Error. Could not generate future forecast data";
        }
    };

});
