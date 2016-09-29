angular.module('notificationApp').
factory('mapFactory', function($http, $cacheFactory, UserConfig) {

    return {
        getDirections: function() {
            if (!UserConfig.APIkeys.googleMapsAPIkey)
                return Promise.reject("No Google Maps API key");
            var startAddr = "origin=" + UserConfig.address.startingAddress.replace(" ", "+");
            var destAddr = "destination=" + UserConfig.address.destinationAddress.replace(" ", "+");
            return $http({
                method: 'GET',
                cache: true,
                url: 'https://maps.googleapis.com/maps/api/directions/json?' +
                    startAddr + '&' + destAddr + '&mode=transit' + '&key=' + UserConfig.APIkeys.googleMapsAPIkey
            });
        },

        getNextBus: function(inputData) {
            if (!UserConfig.APIkeys.googleMapsAPIkey)
                return Promise.reject("No Google Maps API key");
            var count = 0;
            while (inputData.data.routes[0].legs[0].steps[count].travel_mode != "TRANSIT")
                count++;
            return "Next Bus " + moment(inputData.data.routes[0].legs[0].steps[count].transit_details.departure_time.value* 1000).fromNow();
        },

        clearCache: function() {
            var startAddr = "origin=" + UserConfig.address.startingAddress.replace(" ", "+");
            var destAddr = "destination=" + UserConfig.address.destinationAddress.replace(" ", "+");
            $cacheFactory.get('$http').remove('https://maps.googleapis.com/maps/api/directions/json?' +
                startAddr + '&' + destAddr + '&mode=transit' + '&key=' + UserConfig.APIkeys.googleMapsAPIkey);
        }

    }
});
