/**
 * Returns a translated string from
 * the global object 'i18n_strings'
 */
function i18n(key) {
  if (typeof LANG === 'undefined') {
    //onsole.log('WARNING: LANG global variable does not exist.');
    return "UNDEFINED";
  }
  if (typeof i18nStrings === 'undefined') {
    //console.log('WARNING: i18nStrings object does not exist.');
    return "UNDEFINED";
  }
  if (typeof i18nStrings[key] === 'undefined') {
    //console.log('WARNING: key 18nStrings.' + key + ' does not exist.');
    return "UNDEFINED";
  }
  if (typeof i18nStrings[key][LANG] === 'undefined') {
    //console.log('WARNING: key 18nStrings.' + key + ' not translated to ' + LANG);
    return "NOT TRANSLATED";
  }
  return i18nStrings[key][LANG];
}

/**
 * Loads the series metadata, parses it, and passes it
 * as one object to the callback function.
 */
function loadMetadata(url, callback) {
  jQuery.getJSON(url, function(data){
    var mdata = {};
    if (data.hits.hits.length === 0) {
      //console.log('WARNING: Metadata has no recognizable data rows. Empty or bad format?');
    }
    for (var n in data.hits.hits) {
      //console.log(data.hits.hits[n]._source);
      if (typeof data.hits.hits[n]._source.id == 'undefined') {
        //console.log('WARNING: Metadata row has no id value.');
        continue;
      }
      mdata[data.hits.hits[n]._source.id] = {
        'series_id': data.hits.hits[n]._source.id,
        'high_is_good': true,
        'label': {},
        'description': {}
      };
      if (data.hits.hits[n]._source.high_is_good == 'FALSE') {
        mdata[data.hits.hits[n]._source.id].high_is_good = false;
      }
      // grab content by key
      for (var key in data.hits.hits[n]._source) {
        var val = data.hits.hits[n]._source[key];
        if (val === "") {
          continue;
        }
        if (key.indexOf('@') > -1) {
          // i18n strings
          var parts = key.split('@');
          mdata[data.hits.hits[n]._source.id][parts[0]][parts[1]] = val;
        }
      }
    }
    callback(mdata);
  });
}

/**
 * Loads the data series data, parses it and
 * passes it as one object to the callback function.
 */
function loadSourceData(url, callback) {
  jQuery.getJSON(url, function(data){
      var pdata = {};
      pdata.series = {};
      pdata.regions = {};
      if (data.hits.hits.length === 0) {
        //console.log('WARNING: Data has no recognizable data rows. Empty or bad format?');
      }
      for (var n in data.hits.hits) {
        var row = data.hits.hits[n]._source;
        var year = parseInt(row.year, 10);
        var series_category_key = null;
        if (typeof row.series_id == 'undefined') {
          //console.log('WARNING: Data row has no series_id value.');
          continue;
        }
        if (row.series_id === '') {
          //console.log('WARNING: Data row has empty series_id.');
          continue;
        }
        if (row.value_normalized === '') {
          //console.log('WARNING: Data row has no value_normalized. Skipped.');
          continue;
        }
        // category keys are split into alphabetic and numeric parts
        var matches = row.series_id.match(/([a-z]+)([0-9]+)/);
        if (matches) {
          series_category_key = matches[1];
        }
        if (typeof pdata.series[series_category_key] == 'undefined') {
          pdata.series[series_category_key] = {};
        }
        if (typeof pdata.series[series_category_key][row.series_id] == 'undefined') {
          pdata.series[series_category_key][row.series_id] = {};
        }
        if (typeof pdata.series[series_category_key][row.series_id][row.region_id] == 'undefined') {
          pdata.series[series_category_key][row.series_id][row.region_id] = {};
        }
        if (typeof pdata.series[series_category_key][row.series_id][row.region_id][year] == 'undefined') {
          pdata.series[series_category_key][row.series_id][row.region_id][year] = {
            value: parseFloat(row.value),
            value_normalized: parseFloat(row.value_normalized)
          };
        }
        if (typeof pdata.regions[row.region_id] == 'undefined') {
          pdata.regions[row.region_id] = row.region;
        }
      }
      // hand parsed data over to the index view object
      callback(pdata);
    });
}

jQuery(function () {

  // we select page by page which app to start
  var app;
  // home page
  if ($('.backbone-page.index-create').length) {
    app = new YOURTOPIA.Home();
  }
  else if ($('.backbone-page.edit').length) {
    app = new YOURTOPIA.Edit();
  }
  else if ($('.backbone-page.details').length) {
    app = new YOURTOPIA.Details();
  }
  if (typeof app != 'undefined') {
    Backbone.history.start();
  }
});


YOURTOPIA.config = {};

// will mark the resulting dataset's country field
// (ue two- or three-letter code)
YOURTOPIA.config.country = 'IT';

// will be written to the dataset as version field
// and should be changed whenever the source data criteria
// change. Use Integer.
YOURTOPIA.config.version = 1;

// These are the main categories the user can adjust weights for.
// They can have sub-categories.
YOURTOPIA.config.indicator_categories = ['employment',
    'education', 'health', 'environment', 'equality',
    'science', 'safety', 'social'];

// The default value for main category weights
YOURTOPIA.config.category_value_default = 0.5;

// Data source: http://thedatahub.org/dataset/yourtopia-italy/
//var YOURTOPIA.config.webstore_metadata_url = 'http://thedatahub.org/api/data/fffc6388-01bc-44c4-ba0d-b860d93e6c7c/_search';
YOURTOPIA.config.webstore_metadata_url = '/static/data/metadata.json';
//var YOURTOPIA.config.webstore_data_url = 'http://thedatahub.org/api/data/4faaef85-3b22-4ebb-ad28-fcc6bd4f5f3d/_search';
YOURTOPIA.config.webstore_data_url = '/static/data/data.json';

var x = function($) {

YOURTOPIA.Home = Backbone.Router.extend({

  routes: {
    '': 'indexCreate'
  },

  indexview_update_timeout: null,

  /**
   * indexCreate reflects the start page. Allows user to adjust
   * weights of various criteria and hit save to progress.
   */
  indexCreate: function() {

    var sharing_bar_visible = false;
    var newWeights = new YOURTOPIA.Model.Weights();
    var sliders = new YOURTOPIA.View.IndexCreate({
      model: newWeights,
      el: '.index-create .sliders'
    });

    var resultIndex = new YOURTOPIA.Model.AllRegionsTimeSeries();
    resultIndex.setWeights(newWeights);

    // load metadata
    loadMetadata(YOURTOPIA.config.webstore_metadata_url, function(data){
      resultIndex.setSourceMetaData(data);
      //indexView.setSourceMetadata(data);
      sliders.setSourceMetadata(data);
      sliders.render();
    });

    // load data series
    loadSourceData(YOURTOPIA.config.webstore_data_url, function(data){
      //indexView.setSourceData(data);
      resultIndex.setSourceData(data);
    });
    
    // create the indexView (real-time visualization of index data during weight adjustment)
    var indexView = new YOURTOPIA.View.IndexView({
      //model: newWeights,
      model: resultIndex,
      el: '.index-create .resultview'
      //sourceData: null
    });
    indexView.render();

    indexView.delayedUpdate = function() {
      // delaying the result view update so that it's only
      // called after the user stops dragging the sliders
      window.clearTimeout(YOURTOPIA.Home.indexview_update_timeout);
      YOURTOPIA.Home.indexview_update_timeout = window.setTimeout(function(){
        resultIndex.update();
        //indexView.update();
      }, 250);
    };

    indexView.delayedShowSharingBar = function() {
      sharing_bar_visible = true;
      window.setTimeout(function(){
        jQuery('#sharing-top').slideDown('700', 'swing');
      }, 1000);
    };
    // propagate slider change events
    newWeights.on('change', function(){
      indexView.delayedUpdate();
      if (!sharing_bar_visible) {
        indexView.delayedShowSharingBar();
      }
    });

  }

});


/**
 * Share allows the user to add his user details to a dataset and
 * share it via different channels
 */
YOURTOPIA.Edit = Backbone.Router.extend({
  routes: {
    '': 'edit'
  },
  edit: function() {
    var savedWeights = new YOURTOPIA.Model.Weights(userDataset);

    var saveForm = new YOURTOPIA.View.SaveForm({
      el: '#saveform',
      model: savedWeights
    });
    saveForm.render();

    var resultIndex = new YOURTOPIA.Model.AllRegionsTimeSeries();
    resultIndex.setWeights(savedWeights);

    var sliders = new YOURTOPIA.View.IndexCreate({
      model: savedWeights,
      el: '.sliders'
    });
    sliders.readOnly = true;

    var indexView = new YOURTOPIA.View.IndexView({
      model: resultIndex,
      el: '.resultview',
      sourceData: null
    });

    indexView.render();
    loadMetadata(YOURTOPIA.config.webstore_metadata_url, function(data){
      resultIndex.setSourceMetaData(data);
      sliders.setSourceMetadata(data);
      sliders.render();
    });
    loadSourceData(YOURTOPIA.config.webstore_data_url, function(data){
      resultIndex.setSourceData(data);
    });

  }
});

/**
 * Share allows the user to add his user details to a dataset and
 * share it via different channels
 */
YOURTOPIA.Details = Backbone.Router.extend({
  routes: {
    '': 'details'
  },
  details: function() {
    var savedWeights = new YOURTOPIA.Model.Weights(userDataset);
    var sliders = new YOURTOPIA.View.IndexCreate({
      model: savedWeights,
      el: '.sliders'
    });
    sliders.readOnly = true;
    
    var resultIndex = new YOURTOPIA.Model.AllRegionsTimeSeries();
    resultIndex.setWeights(savedWeights);

    var indexView = new YOURTOPIA.View.IndexView({
      //model: savedWeights,
      model: resultIndex,
      el: '.resultview'
      //sourceData: null
    });
    indexView.render();

    loadMetadata(YOURTOPIA.config.webstore_metadata_url, function(data){
      resultIndex.setSourceMetaData(data);
      sliders.setSourceMetadata(data);
      sliders.render();
    });
    loadSourceData(YOURTOPIA.config.webstore_data_url, function(data){
      resultIndex.setSourceData(data);
    });

  }
});

}(jQuery);
