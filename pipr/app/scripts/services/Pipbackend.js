'use strict';

angular.module('piprApp')
  .service('Pipbackend', function Pipbackend($resource) {
      this.pips = $resource('http://pippypips.herokuapp.com/api/pips/:id');
  });
