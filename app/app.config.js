angular.module('notificationApp')
.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
	when("/", {templateUrl: "app/views/partials/home.html"}).
  when("/weather", {templateUrl: "app/views/partials/weatherDisplay.html", controller: "weatherController"})
}]);
