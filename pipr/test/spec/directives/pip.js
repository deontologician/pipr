'use strict';

describe('Directive: pip', function () {

  // load the directive's module
  beforeEach(module('piprApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<pip></pip>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the pip directive');
  }));
});
