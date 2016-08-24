angular.module('notificationApp')
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.
        when("/", {
            templateUrl: "views/partials/home.html"
        }).
        when("/weather", {
            templateUrl: "views/partials/weatherDisplay.html",
            controller: "weatherController"
        })
}]);
