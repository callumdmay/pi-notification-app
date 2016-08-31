angular.module('notificationApp.weatherFactory', []).
factory('weatherFactory', function($http, $cacheFactory, UserConfig) {

    return {
        getCurrentWeather: function() {
            if (!UserConfig.APIkeys.weatherAPIkey)
                return Promise.reject("No Weather API key");
            return $http({
                method: 'GET',
                cache: true,
                url: 'http://api.wunderground.com/api/' + UserConfig.APIkeys.weatherAPIkey + '/conditions/q/' + UserConfig.country + '/' + UserConfig.city + '.json'
            });
        },
        getForecast: function() {
            if (!UserConfig.APIkeys.weatherAPIkey)
                return Promise.reject("No Weather API key");
            return $http({
                method: 'GET',
                cache: true,
                url: 'http://api.wunderground.com/api/' + UserConfig.APIkeys.weatherAPIkey + '/forecast10day/q/' + UserConfig.country + '/' + UserConfig.city + '.json'
            });
        },

        clearCache: function() {
            $cacheFactory.get('$http').remove('http://api.wunderground.com/api/' + UserConfig.APIkeys.weatherAPIkey + '/conditions/q/' + UserConfig.country + '/' + UserConfig.city + '.json');
            $cacheFactory.get('$http').remove('http://api.wunderground.com/api/' + UserConfig.APIkeys.weatherAPIkey + '/forecast10day/q/' + UserConfig.country + '/' + UserConfig.city + '.json');
        },

        translateWeatherIcon: function(weatherString) {
            switch (weatherString) {
                case "chanceflurries":
                    return "wi-snow-wind";
                case "chancerain":
                    return "wi-rain";
                case "chancesleat":
                    return "wi-sleet";
                case "chancesnow":
                    return "wi-snow";
                case "chancestorms":
                    return "wi-thunderstorm";
                case "chancetstorms":
                    return "wi-thunderstorm";
                case "clear":
                    return "wi-day-sunny";
                case "cloudy":
                    return "wi-day-cloudy";
                case "flurries":
                    return "wi-snow-wind";
                case "hazy":
                    return "wi-day-haze";
                case "mostlycloudy":
                    return "wi-day-cloudy";
                case "mostlysunny":
                    return "wi-day-sunny";
                case "partlycloudy":
                    return "wi-day-cloudy";
                case "partlysunny":
                    return "wi-day-sunny";
                case "rain":
                    return "wi-showers";
                case "sleat":
                    return "wi-sleet";
                case "snow":
                    return "wi-snow";
                case "sunny":
                    return "wi-day-sunny";
                case "tstorms":
                    return "wi-thunderstorm";

                default:
                    return "wi-na";
            }
        }
    };

});
