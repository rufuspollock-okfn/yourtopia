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
    var stubIndex = new YOURTOPIA.Model.Index({
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
