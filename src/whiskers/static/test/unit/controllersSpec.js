'use strict';

/* jasmine specs for controllers go here */

describe('whiskers controllers', function() {
  describe('PackagesCtrl', function() {
    it('should create "Packages" model', function() {
      var scope = {};
      ctrl = new PackagesCtrl(scope);
      expect(scope.packages);
    });
  });
});
