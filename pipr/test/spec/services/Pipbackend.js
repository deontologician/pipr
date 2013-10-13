'use strict';

describe('Service: Pipbackend', function () {

  // load the service's module
  beforeEach(module('piprApp'));

  // instantiate service
  var Pipbackend;
  beforeEach(inject(function (_Pipbackend_) {
    Pipbackend = _Pipbackend_;
  }));

  it('should do something', function () {
    expect(!!Pipbackend).toBe(true);
  });

});
