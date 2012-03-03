YOURTOPIA.View = function($) {

var my = {};

my.SeriesListing = Backbone.View.extend({
  initialize: function() {
    var self = this;
    this.el = $(this.el);
    _.each(this.collection.models, function(series) {
			var $li = $('<li>' + series.get('label') + '</li>');
			$li.data('key', series.id);
      self.el.append($li);
    });
  },

  events: {
    'click .universe li': 'selectSeries'
  },

  selectSeries: function(e) {
    e.preventDefault();
    var $target = $(e.target);
    var selected = this.collection.get($target.data('key'));
    if (!(this.selected.include(selected))) {
      this.selected.add(selected);
    }
  },

  render: function() {
  }
});
 
my.SelectedSeriesListing = Backbone.View.extend({
  initialize: function() {
    this.el = $(this.el);
    _.bindAll(this, 'render');
    this.collection.bind('add', this.render);
    this.collection.bind('remove', this.render);
  },

  events: {
    'click .selection li': 'removeSeries'
  },

  removeSeries: function(e) {
    e.preventDefault();
    var $target = $(e.target);

    var unselected = this.collection.get($target.data('key'));

    if ((this.collection.include(unselected))) {
      this.collection.remove(unselected);
    }
  },

  render: function() {
    var self = this;
    self.el.html('');
    this.collection.each(function(series, idx) {
      var $li = $('<li />').data('key', series.get('id'));
      $li.append($('<span class="title" />').text(series.get('label')));
      var $select = $('<select class="span1" />');
      for(var ii=1;ii<6;ii++) {
        $select.append($('<option />').text(ii));
      }
      $li.append($select);
      self.el.append($li);
    });
  }
});

my.IndexCreate = Backbone.View.extend({
  template: '',
  initialize: function() {
    this.series = new YOURTOPIA.Model.SeriesList([
      {
        id: 'education-spending'
        , label: 'Education spending (% of GDP)'
      },
      {
        id: 'infrastructure-spending'
        , label: 'Infrastructure spending (% of GDP)'
      }
    ]);
    this.selectedSeries = new YOURTOPIA.Model.SeriesList();
  },

  render: function() {
    var page_title = 'Create your index';
    $('.page-header h1').html(page_title);

    var $universeComponents = this.el.find('.universe .components');
    var listingView = new YOURTOPIA.View.SeriesListing({
      collection: this.series
      , el: $universeComponents
    });
    listingView.selected = this.selectedSeries;

    var $selectionComponents = this.el.find('.selection .components')
    var selectedView = new YOURTOPIA.View.SelectedSeriesListing({
      collection: this.selectedSeries
      , el: $selectionComponents
    });
  }
});


my.IndexView = Backbone.View.extend({
  template: '',

  render: function() {
    var page_title = 'Index: ' + this.model.get('title');
    $('.page-header h1').html(page_title);
    this.el.html('Index view will go here');
  }
});

return my;

}(jQuery);


