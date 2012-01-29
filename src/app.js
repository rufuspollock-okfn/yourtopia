jQuery(function () {
  var series = new YOURTOPIA.Model.SeriesList([
    {
      id: 'education-spending'
			, label: 'Education spending (% of GDP)'
		},
    {
		  id: 'infrastructure-spending'
			, label: 'Infrastructure spending (% of GDP)'
    }
  ]);
  var selectedSeries = new YOURTOPIA.Model.SeriesList();

  var $universeComponents = $('.universe .components');
  var listingView = new YOURTOPIA.View.SeriesListing({
    collection: series
    , el: $universeComponents
  });
  listingView.selected = selectedSeries;

  var $selectionComponents = $('.selection .components')
  var selectedView = new YOURTOPIA.View.SelectedSeriesListing({
    collection: selectedSeries
    , el: $selectionComponents
  });

  var app = new YOURTOPIA.Application();
  Backbone.history.start();
});

var x = function($) {

// ## The primary view for the entire application
//
YOURTOPIA.Application = Backbone.Router.extend({
  routes: {
    'index/create': 'indexCreate'  
    , 'index/:id':    'indexView'
  },

  indexCreate: function() {
    // TODO: wire up existing view code
  },

  indexView: function() {
    var stubIndex = new YOURTOPIA.Model.Series({
      id: 'abc'
      , is_index: true
      , title: 'My demo index' 
    });
    $el = $('.index-view');
    var view = new YOURTOPIA.View.IndexView({
      el: $el
      , model: stubIndex
    });
    view.render();
    this.switchView('index/view');
  },

  switchView: function(path) {
    $('.backbone-page').hide(); 
    var cssClass = path.replace('/', '-');
    $('.' + cssClass).show();
  }
});

}(jQuery);
