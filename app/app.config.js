angular.module('notificationApp')
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.
        when("/", {
            templateUrl: "components/home.html"
        }).
        when("/weather", {
            templateUrl: "components/weatherModule/weatherDisplay.html",
            controller: "weatherController"
        })
}]);
