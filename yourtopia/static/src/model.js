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
  /* unused
  my.Series = Backbone.Model.extend({
    defaults: {
      title: null,
      description: null,
      // TODO: year, country, region, value, normalized_value
      data: []
    },
    initialize: function() {}
  });
  */

  /*
  // not sure if needed
  my.SeriesList = Backbone.Collection.extend({
    model: my.Series
  });
  */

  /**
   * Weights: User-defined weights for criteria
   *
   * User-created weights of certain categories, plus
   * user name, description text and creation date.
   */
  my.Weights = Backbone.Model.extend({
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
  

  /**
   * Calculated Index data series for one region
   * over time
   */
  my.SingleRegionTimeSeries = Backbone.Model.extend({
    defaults: {
      region_label: null,
      from_year: null,
      to_year: null,
      values: {},
      years: []
    },
    /**
     * Pass objects as parameter with year and value property
     * to populate the model
     */
    setYearValue: function(year, value) {
      var self = this;
      //console.log(self, self.id, year, value);
      if (self.get('from_year') === null || self.get('from_year') > year) {
        self.set({from_year: year}, {silent: true});
      }
      if (self.get('to_year') === null || self.get('to_year') < year) {
        self.set({to_year: year}, {silent: true});
      }
      var values = self.get('values');
      var years = self.get('years');
      if (typeof values[year] == 'undefined') {
        values[year] = value;
        years.push(year);
      }
      self.set('values', values, {silent: true});
      self.set('years', years, {silent: true});
    },
    setYearValues: function(vals) {
      var keys = [];
      for (var key in vals) {
        keys.push(key);
      }
      this.set('values', vals, {silent: true});
      this.set('years', keys, {silent: true});
    }
  });

  /**
   * Region index result data collection
   */
  my.AllRegionsTimeSeries = Backbone.Collection.extend({
    model: my.RegionTimeSeries,
    sourceData: null,
    sourceMetaData: null,
    weights: null,
    from_year: null,
    to_year: null,
    /**
     * Create collection items pased on the regions in d
     */
    setSourceData: function(d) {
      var self = this;
      this.sourceData = d;
      //console.log(d);
      // create an entry for each region
      for (var r in d.regions) {
        var srts = new my.SingleRegionTimeSeries({
          id: r,
          region_label: d.regions[r]
        });
        self.push(srts, {silent: true});
      }
      // store the lowest and highest year in the data
      var lowest_year = 1000000;
      var highest_year = 0;
      for (var s in d.series) {
        for (var c in d.series[s]) {
          for (var rg in d.series[s][c]) {
            for (var y in d.series[s][c][rg]) {
              y = parseInt(y, 10);
              if (y > highest_year) {
                highest_year = y;
              }
              if (y < lowest_year) {
                lowest_year = y;
              }
            }
          }
        }
      }
      self.from_year = lowest_year;
      self.to_year = highest_year;
      this.update();
    },
    setSourceMetaData: function(d) {
      this.sourceMetaData = d;
      this.update();
    },
    setWeights: function(w) {
      this.weights = w;
      this.update();
    },
    /**
     * This calcualates the weighted index values.
     */
    update: function() {
      console.log('AllRegionsTimeSeries.update() called!');
      if (this.sourceData === null || this.sourceMetaData === null || this.weights === null) {
        // too early for this.
        console.log('Exiting AllRegionsTimeSeries.update() - incomplete data');
        return;
      }
      var self = this;
      var categories = this.weights.get('weighted_measures');

      // iterate regions
      //this.each(function(region_timeseries, num){
      for (var num=0; num < self.length; num++) {
        var region_timeseries = self.at(num);
        var region_code = region_timeseries.id;
        var values_per_year = {};
        //console.log(num, region_code);
        
        // iterate years
        for (var y=self.from_year; y<=self.to_year; y++) {
          //console.log(num, region_code, y);
          var index_value = 0.0;
          var num_index_values = 0;

          // iterate categories
          for (var c in categories) {
            var category_weight = self.weights.get(categories[c] + '_weight');
            for (var series_id in self.sourceData.series[categories[c]]) {
              if (typeof self.sourceData.series[categories[c]][series_id][region_code] !== 'undefined' &&
                typeof self.sourceData.series[categories[c]][series_id][region_code][y] !== 'undefined') {
                var value = self.sourceData.series[categories[c]][series_id][region_code][y].value_normalized;
                if (typeof value === 'number') {
                  //console.log(num, region_code, y, series_id, value);
                  var subWeight = 1.0; // default single measure factor
                  if (self.weights.has(series_id + '_weight')) {
                    subWeight = self.weights.get(series_id + '_weight');
                  }

                  //console.log(value, subWeight, category_weight, self.sourceMetaData[series_id].high_is_good);
                  if (self.sourceMetaData[series_id].high_is_good) {
                    index_value += value * subWeight * category_weight;
                  } else {
                    index_value += (1 - value) * subWeight * category_weight;
                  }
                  num_index_values++;
                }
              }
            }
          }
          var final_year_region_value = index_value / num_index_values;
          //console.log(region_timeseries, region_code, y, final_year_region_value);
          // finally store value for this year
          region_timeseries.setYearValue(y, final_year_region_value);
          values_per_year[y] = final_year_region_value;
        }
        region_timeseries.setYearValues(values_per_year);
        //console.log(region_code, values_per_year);
      }
      // finally inform all who care about the update
      this.trigger('change');
    }
  });

  return my;

}(jQuery);

