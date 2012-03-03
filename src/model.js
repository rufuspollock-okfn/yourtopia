window.YOURTOPIA = window.YOURTOPIA || {};

YOURTOPIA.Model = function($) {
var my = {};

my.Profile = Backbone.Model.extend({
});

my.Series = Backbone.Model.extend({
  defaults: {
    title: ''
    , description: ''
    // year, country, region, value, normalized_value
    , data: []
  },
  initialize: function() {
  }
});

my.SeriesList = Backbone.Collection.extend({
  model: my.Series
});

my.Index= Backbone.Model.extend({
  defaults: {
    title: ''
    , description: ''
    , series: []
    , weightings: {}
    , data: null
  },

  initialize: function() {
  }
});

return my;

}(jQuery);

