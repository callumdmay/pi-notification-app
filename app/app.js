startApplication();

function startApplication() {

    fetchData().then(bootstrapApplication);

    function fetchData() {

        var $http = angular.injector(["ng"]).get("$http");

        return $http.get("APIkeys.json").then(function(response) {
            angular.module('notificationApp').constant("APIkeys", angular.fromJson(response.data));
        }, function(errorResponse) {
            var div = document.createElement("div");
            div.style.fontSize = "xx-large";
            div.innerHTML = "Error: Could not find APIkeys.json. Make sure it is at the root of the application";
            document.body.insertBefore(div, document.body.firstChild);
        });
    }

    function bootstrapApplication() {
        angular.element(document).ready(function() {
            angular.bootstrap(document, ["notificationApp"]);
        });
    }
};
