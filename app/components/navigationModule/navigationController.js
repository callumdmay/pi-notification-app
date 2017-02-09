angular.module("notificationApp.controllers").
controller("navigationController", function($scope, $rootScope) {

  $scope.numberOfPages = 2;

  $scope.navigate = function(inputButton) {
    if (inputButton == "right") {
      if ($rootScope.currentPageIndex + 1 > $scope.numberOfPages) {
        $rootScope.currentPageIndex = 1;
      }
      else {
        $rootScope.currentPageIndex++;
      }
    }

    if (inputButton == "left") {
      if ($rootScope.currentPageIndex - 1 < 1) {
        $rootScope.currentPageIndex = $scope.numberOfPages;
      }
      else {
        $rootScope.currentPageIndex--;
      }
    }
  }
});
