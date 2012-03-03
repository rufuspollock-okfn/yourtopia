jQuery(function () {
  var app = new YOURTOPIA.Application();
  Backbone.history.start();
});

var x = function($) {

// ## The primary view for the entire application
//
YOURTOPIA.Application = Backbone.Router.extend({
  routes: {
    '': 'home'
    , 'index/create': 'indexCreate'  
    , 'index/:id':    'indexView'
  },

  home: function() {
    this.switchView('home');
  },

  indexCreate: function() {
    var newIndex = new YOURTOPIA.Model.Index();
    $el = $('.index-create');
    var view = new YOURTOPIA.View.IndexCreate({
      el: $el
      , model: newIndex
    });
    view.render();
    this.switchView('index/create');
  },

  indexView: function() {
    var url = 'http://thedatahub.org/api/data/eca3d7c2-f150-45e4-8749-0c4ba24505fe/_search';
    data = {
      size: 231
    };
    var jqxhr = $.ajax({
      url: url,
      data: data,
      dataType: 'jsonp'
    });
    var employmentSeries = new YOURTOPIA.Model.Series({id: 'employment'});
    jqxhr.done(function(data) {
      _.each(_.pluck(data.hits.hits, '_source'), function(row) {
        employmentSeries.get('data').push({
          Year: parseInt(row.year),
          value: row.employment,
          Region: row.Region
        });
      });
      var stubIndex = new YOURTOPIA.Model.Index({
        id: 'abc'
        , is_index: true
        , title: 'My demo index' 
      });
      stubIndex.series = [ employmentSeries ];
      // HAcK: copy across our single series
      stubIndex.set({data: employmentSeries.get('data')});
      $el = $('.index-view');
      var view = new YOURTOPIA.View.IndexView({
        el: $el
        , model: stubIndex
      });
      view.render();
    });
    this.switchView('index/view');
  },

  switchView: function(path) {
    $('.backbone-page').hide(); 
    var cssClass = path.replace('/', '-');
    $('.' + cssClass).show();
  }
});

}(jQuery);
