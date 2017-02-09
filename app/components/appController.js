angular.module("notificationApp.controllers").
controller("appController", function($scope, $rootScope) {

  $rootScope.currentPageIndex = 1;

  $scope.renderTemplate = function() {
    if ($rootScope.currentPageIndex ==1)
      return "page1.html";
    else if ($rootScope.currentPageIndex == 2)
      return "page2.html";
    else
            return "";
  }

});
