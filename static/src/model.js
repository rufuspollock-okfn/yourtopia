window.YOURTOPIA = window.YOURTOPIA || {};

YOURTOPIA.Model = function($) {
  var my = {};

  // make model capable of
  Backbone.Model.prototype.setByName = function(key, index, value) {
    this.set(key[index], value);
  };

  /**
   * Series
   *
   * Model representing a data series like e.g. "employment rate"
   * with respect to a certain time frame, country and region.
   */
  my.Series = Backbone.Model.extend({
    defaults: {
      title: null,
      description: null,
      // TODO: year, country, region, value, normalized_value
      data: []
    },
    initialize: function() {}
  });

  /*
  // not sure if needed
  my.SeriesList = Backbone.Collection.extend({
    model: my.Series
  });
  */

  /**
   * Index
   *
   * User-created weights of certain categories, plus
   * user name, description text and creation date.
   */
  my.Index = Backbone.Model.extend({
    defaults: {
      user_name: null,
      user_url: null,
      description: null,
      created_at: null,
      weighted_measures: ['employment', 'education',
        'health', 'environment', 'equality',
        'science', 'safety', 'social'],
      employment_weight: 0.5,
      education_weight: 0.5,
      health_weight: 0.5,
      environment_weight: 0.5,
      equality_weight: 0.5,
      science_weight: 0.5,
      safety_weight: 0.5,
      social_weight: 0.5
    },

    initialize: function() {}
  });

  return my;

}(jQuery);

