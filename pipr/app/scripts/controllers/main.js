'use strict';

angular.module('piprApp')
    .controller('MainCtrl', function ($scope, Pipbackend) {
        $scope.refreshPips = function(){
            Pipbackend.pips.query(
                {limit: 10, offset: 0},
                function onSuccess(pipList){
                    $scope.pips = pipList;
                    $scope.clearError();
                },
                $scope.setError // on error
            );
        };
        $scope.makePip = function(){
            Pipbackend.pips.save(
                $scope.newPip,
                function onSuccess(newPip){
                    $scope.newPip = {name: $scope.newPip.name};
                    $scope.refreshPips();
                },
                $scope.setError // on error
            );
        };
        $scope.deletePip = function(pipId) {
            Pipbackend.pips.delete(
                {id: pipId},
                $scope.refreshPips, // on success
                $scope.setError);   // on error
        };
        $scope.setError = function(resp){ $scope.error = resp.data.error};
        $scope.clearError = function(){ $scope.error = null };
        $scope.refreshPips();
  });