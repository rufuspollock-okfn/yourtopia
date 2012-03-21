YOURTOPIA.View = function($) {

var my = {};

my.SeriesListing = Backbone.View.extend({
  initialize: function() {
    var self = this;
    this.el = $(this.el);
    _.bindAll(this, 'selectSeries', 'render');
    this.collection.bind('add', this.render);
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
    var self = this;
    this.el.empty();
    _.each(this.collection.models, function(series) {
			var $li = $('<li>' + series.get('label') + '</li>');
			$li.data('key', series.id);
      self.el.append($li);
    });
  }
});
 
my.SelectedSeriesListing = Backbone.View.extend({
  initialize: function() {
    this.el = $(this.el);
    _.bindAll(this, 'render');
    this.model.series.bind('add', this.render);
    this.model.series.bind('remove', this.render);
  },

  events: {
    'click .selection li': 'removeSeries'
  },

  removeSeries: function(e) {
    e.preventDefault();
    var $target = $(e.target).closest('li');

    var unselected = this.model.series.get($target.data('key'));

    if ((this.model.series.include(unselected))) {
      this.model.series.remove(unselected);
    }
  },

  render: function() {
    var self = this;
    self.el.html('');
    this.model.series.each(function(series, idx) {
      var $li = $('<li />').data('key', series.get('id'));
      $li.append($('<span class="title" />').text(series.get('label')));
      
      /*
      var $select = $('<select class="span1" />');
      for(var ii=1;ii<6;ii++) {
        $select.append($('<option />').text(ii));
      }
      $li.append($select);
      */

      var weighting = 3, $rate = $('<span class="rate" />').data('weighting', weighting);
      for(var ii=1;ii<6;ii++) {
        var char = (ii <= weighting) ? '&#x25CF;' : '&#9675;'; // replace with something prettier
        var $option = $('<span data-weighting="' + ii + '"/>').html(char);
        $rate.append($option);
      }
      $li.append($rate);
      
      self.el.append($li);
    });
  }
});

my.IndexCreate = Backbone.View.extend({
  template: '',
  initialize: function(config) {
    var self = this;
    this.series = config.allSeries;
    this.model.series = new YOURTOPIA.Model.SeriesList();
  },

  render: function() {
    var page_title = 'Create your index';
    $('.page-header h1').html(page_title);

    var $universeComponents = this.el.find('.universe .components');
    var listingView = new YOURTOPIA.View.SeriesListing({
      collection: this.series
      , el: $universeComponents
    });
    listingView.selected = this.model.series;

    var $selectionComponents = this.el.find('.selection .components')
    var selectedView = new YOURTOPIA.View.SelectedSeriesListing({
      model: this.model
      , el: $selectionComponents
    });
  }
});


my.IndexView = Backbone.View.extend({
  template: ' \
    <div class="description"> \
      {{description}} \
    </div> \
    <div class="data-explorer-here"></div> \
  ',

  render: function() {
    var page_title = 'Index: ' + this.model.get('title');
    $('.page-header h1').html(page_title);
    var tmplData = this.model.toJSON();
    var templated = Mustache.render(this.template, tmplData);
    this.el.html(templated);
    var backend = new recline.Backend.Memory();
    var docs = _.filter(this.model.get('data'), function(row) {
      return row.Region == 'Lombardia';
    });
    var inData = {
      metadata: {
        id: 'xyz'
      }
      , fields: [{id: 'Year'}, {id: 'value'}, {id: 'Region'}]
      , documents: docs
    };
    backend.addDataset(inData);
    var dataset = new recline.Model.Dataset({id: 'xyz'}, backend);
    dataset.fetch();
    var grid = new recline.View.DataGrid({
      model: dataset
    });
    var flot = new recline.View.FlotGraph({
      model: dataset
    });
    this.el.find('.data-explorer-here').append(flot.el);
    this.el.find('.data-explorer-here').append(grid.el);
    this.el.addClass('read-only');
    grid.render();
    dataset.query();
  }
});

return my;

}(jQuery);


