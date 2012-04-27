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
      id: null,
      country: null,
      version: null,
      user_name: null,
      user_url: null,
      user_ip: null,
      description: null,
      created_at: null,
      weighted_measures: null
    },

    /**
     * If parameter data is given, the model is pre-populated
     */
    initialize: function(data) {
      this.set({
        weighted_measures: YOURTOPIA.config.indicator_categories,
        country: YOURTOPIA.config.country,
        version: YOURTOPIA.config.version
      });
      // create weight attributes according to configuration
      for (var c in YOURTOPIA.config.indicator_categories) {
        var category = YOURTOPIA.config.indicator_categories[c];
        this.set(category + '_weight', YOURTOPIA.config.category_value_default);
      }
      // in case we have a 'weights' attribute (which means we got
      // this pre-populated) we fill the values in the right places
      if (this.has('weights')) {
        var weights = JSON.parse(this.get('weights'));
        for (var w in weights) {
          this.set(w, weights[w]);
        }
        this.unset('weights');
      }
    }
  });

  return my;

}(jQuery);

