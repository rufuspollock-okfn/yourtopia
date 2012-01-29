window.YOURTOPIA = window.YOURTOPIA || {};

YOURTOPIA.Model = function($) {
var my = {};

my.Profile = Backbone.Model.extend({
});

my.Series = Backbone.Model.extend({
  defaults: {
    title: ''
    , description: ''
    , is_index: false
    , transform: '' 
    , series: []
    // year, country, region, value
    // pivot: year, country-a, country-b
    , data: null
  },
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

