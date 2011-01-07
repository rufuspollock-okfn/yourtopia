var OpenHDI = (function($, my) {

  var User = Backbone.Model.extend({});
  var WeightingSet = Backbone.Model.extend({});
  var UserList = Backbone.Collection.extend({
    model: User,
    initialize: function () {
    }
  });
  var WeightingSetList = Backbone.Collection.extend({
    model: WeightingSet,
    url: '/api/weighting',
    initialize: function () {
    }
  });

  my.Users = new UserList();
  my.WeightingSets = new WeightingSetList();

  //Backbone.sync = function(method, model) {
  //  console.log(method + ": " + JSON.stringify(model));
  //};

  my.getWeightings = function() {
    var weightings = [];
    $('.weighting').each(function(idx, div) {
      var div = $(div);
      weightings.push({ id: div.attr('id').split('-')[1], weighting: div.slider('value') });
    });
    return weightings;
  };

  my.renderPieChart = function() {
    var data = $('.weighting').map(function(idx, div) {
      var div = $(div);
      return { label: div.attr('id').split('-')[1], data: div.slider('value') }
    });

    $.plot($("#pie"), data, {
      series: {
        pie: { 
          show: true
        }
      },
      legend: {
        show: false
      }
    });
  };

  my.showNotification = function(status, message) {
    var $notification = $('#inline-notification');
    $notification
      .attr('class', 'notification')
      .addClass(status)
      .find('.message')
        .html(message).end()
      .find('button').one('click', function() {
        $(this).parent().slideUp(200);
      }).end()
      .slideDown(400);
  };

  my.setupApp = function() {
    $('.weighting').slider({
      value: 50,
      min: 1,
      max: 100,
      step: 1,
      slide: function( event, ui ) {
        questionId = event.target.id.split('-')[1];
        $("#weighting-" + questionId + '-percent').html(ui.value);
        my.renderPieChart();
      }
    });

    $('#save').click(function(e) {
      e.preventDefault();
      var weightings = my.getWeightings();
      my.WeightingSets.create(
        {weightings: weightings}
        );
      my.showNotification('alert', 'Saved your weightings');
    });
  }
  return my;
}(jQuery, OpenHDI || {}));

