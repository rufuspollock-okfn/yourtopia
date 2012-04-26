/**
 * Returns a translated string from
 * the global object 'i18n_strings'
 */
function i18n(key) {
  if (typeof LANG === 'undefined') {
    console.log('WARNING: LANG global variable does not exist.');
    return "UNDEFINED";
  }
  if (typeof i18nStrings === 'undefined') {
    console.log('WARNING: i18nStrings object does not exist.');
    return "UNDEFINED";
  }
  if (typeof i18nStrings[key] === 'undefined') {
    console.log('WARNING: key 18nStrings.' + key + ' does not exist.');
    return "UNDEFINED";
  }
  if (typeof i18nStrings[key][LANG] === 'undefined') {
    console.log('WARNING: key 18nStrings.' + key + ' not translated to ' + LANG);
    return "NOT TRANSLATED";
  }
  return i18nStrings[key][LANG];
}

jQuery(function () {
  var app = new YOURTOPIA.Application();
  Backbone.history.start();
});

var x = function($) {

YOURTOPIA.Application = Backbone.Router.extend({

  routes: {
    '': 'indexCreate',
    'all': 'indexList',
    'about': 'about'
  },

  indexview_update_timeout: null,

  about: function(){
    var view = new YOURTOPIA.View.About();
    view.render();
    this.switchView('about');
  },

  indexCreate: function() {
    var sharing_bar_visible = false;
    var newIndex = new YOURTOPIA.Model.Index();
    var sliders = new YOURTOPIA.View.IndexCreate({
      model: newIndex,
      el: '.index-create .sliders'
    });
    // load data - that might take a while
    // See http://thedatahub.org/dataset/yourtopia-italy/

    //var webstore_metadata_url = 'http://thedatahub.org/api/data/fffc6388-01bc-44c4-ba0d-b860d93e6c7c/_search';
    var webstore_metadata_url = '/static/data/metadata.json';
    //var webstore_data_url = 'http://thedatahub.org/api/data/4faaef85-3b22-4ebb-ad28-fcc6bd4f5f3d/_search';
    var webstore_data_url = '/static/data/data.json';

    // load metadata
    jQuery.get(webstore_metadata_url, {size: 1000, dataType: 'jsonp'}, function(data){
      var mdata = {};
      if (data.hits.hits.length === 0) {
        console.log('WARNING: Metadata has no recognizable data rows. Empty or bad format?');
      }
      for (var n in data.hits.hits) {
        //console.log(data.hits.hits[n]._source);
        if (typeof data.hits.hits[n]._source.id == 'undefined') {
          console.log('WARNING: Metadata row has no id value.');
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
      sliders.setSourceMetadata(mdata);
      sliders.render();
      indexView.setSourceMetadata(mdata);
    });

    /* load and process webstore data */
    jQuery.get(webstore_data_url, {size: 6000, dataType: 'jsonp'}, function(data){
      var pdata = {};
      pdata.series = {};
      pdata.regions = {};
      if (data.hits.hits.length === 0) {
        console.log('WARNING: Data has no recognizable data rows. Empty or bad format?');
      }
      for (var n in data.hits.hits) {
        var row = data.hits.hits[n]._source;
        var year = parseInt(row.year, 10);
        var series_category_key = null;
        if (typeof row.series_id == 'undefined') {
          console.log('WARNING: Data row has no series_id value.');
          continue;
        }
        if (row.series_id === '') {
          console.log('WARNING: Data row has empty series_id.');
          continue;
        }
        if (row.value_normalized === '') {
          console.log('WARNING: Data row has no value_normalized. Skipped.');
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
      indexView.setSourceData(pdata);
    });
    
    // create the indexView (real-time visualization of index data during weight adjustment)
    var indexView = new YOURTOPIA.View.IndexView({
      model: newIndex,
      el: '.index-create .resultview',
      sourceData: null
    });
    indexView.render();
    indexView.delayedUpdate = function() {
      // delaying the result view update so that it's only
      // called after the user stops dragging the sliders
      window.clearTimeout(YOURTOPIA.Application.indexview_update_timeout);
      YOURTOPIA.Application.indexview_update_timeout = window.setTimeout(function(){indexView.update();}, 250);
    };
    indexView.delayedShowSharingBar = function() {
      sharing_bar_visible = true;
      window.setTimeout(function(){
        jQuery('#sharing-top').slideDown('700', 'swing');
      }, 3000);
    };
    newIndex.on('change', function(){
      indexView.delayedUpdate();
      if (!sharing_bar_visible) {
        indexView.delayedShowSharingBar();
      }
    });
    //this.switchView('index-create');

    // saving / sharing
    var indexShare;
    jQuery('.sharing button').click(function(){
      var json_data = JSON.stringify(newIndex);
      console.log('data to be sent: ', {'data': json_data});
      jQuery.post('/share/', {'data': json_data}, function(data, textStatus){
        // success callback
        console.log('post success:', data, textStatus);
      });
    });

  },

  switchView: function(path) {
    $('.backbone-page').hide();
    var cssClass = path.replace('/', '-');
    $('.' + cssClass).show();
  }
});

}(jQuery);
