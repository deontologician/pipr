'use strict';

angular.module('piprApp')
  .directive('splitToList', function () {
      return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attrs, modelCtrl) {
            modelCtrl.$parsers.push(function(text){
                return text.split(' ');
            });
        }
    };
  });
