angular.module('notificationApp')
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.
        when("/", {
            templateUrl: "home.html"
        });
        $routeProvider.
        when("/weather", {
            templateUrl: "weatherDisplay.html",
            controller: "weatherController"
        });
    }]);
