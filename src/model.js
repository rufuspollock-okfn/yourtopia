window.YOURTOPIA = window.YOURTOPIA || {};

YOURTOPIA.Model = function($) {
var my = {};

my.Profile = Backbone.Model.extend({
});

my.Series = Backbone.Model.extend({
  initialize: function() {
  }
});

my.SeriesList = Backbone.Collection.extend({
  model: my.Series
});

my.Index= Backbone.Model.extend({
});

return my;

}(jQuery);

