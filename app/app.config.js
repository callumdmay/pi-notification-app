angular.module("notificationApp")
    .config(function ($routeProvider) {
      $routeProvider.
        when("/", {
          templateUrl: "home.html"
        });
      $routeProvider.
        when("/weather", {
          templateUrl: "weatherDisplay.html",
          controller: "WeatherController",
          controllerAs: "vm"
        });
    });
