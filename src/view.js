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
    'click .universe li': 'selectSeries',
    'click .selection li': 'removeSeries'
  },

  selectSeries: function(e) {
    e.preventDefault();
    var $target = $(e.target);
    var selected = this.collection.get($target.data('key'));
    if (!(this.selected.include(selected))) {
      this.selected.add(selected);
    }
  },

  removeSeries: function(e) {
    console.log('removeSeries');

    e.preventDefault();
    var $target = $(e.target);
    var selected = this.collection.get($target.data('key'));
    if ((this.selected.include(selected))) {
      this.selected.remove(selected);
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

  render: function() {
    var self = this;
    self.el.html('');
    this.collection.each(function(series) {
      var x = $('<li />');
      x.html(series.get('label'));
      self.el.append(x);
    });
  }
});

return my;

}(jQuery);


