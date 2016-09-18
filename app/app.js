startApplication();

function startApplication() {

    fetchData().then(bootstrapApplication);

    function fetchData() {

        var $http = angular.injector(["ng"]).get("$http");

        return $http.get("UserConfig.json").then(function(response) {
            angular.module('notificationApp').constant("UserConfig", angular.fromJson(response.data));
        }, function() {
            alert("Error: Could not find UserConfig.json. Make sure it is at the root of the application");
            throw new Error();
        });
    }

    function bootstrapApplication() {
        angular.element(document).ready(function() {
            angular.bootstrap(document, ["notificationApp"]);
        });
    }
}
