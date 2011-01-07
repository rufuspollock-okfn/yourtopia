var OpenHDI = (function($, my) {

   my.getWeightings = function() {
    var weightingsList = $('.weighting').map(function(idx, div) {
      var div = $(div);
      return { id: div.attr('id').split('-')[1], weighting: div.slider('value') }
    });
    var weightings = {};
    $.each(weightingsList, function(idx, item) {
      weightings[item.id] = item.weighting;
    });
    return weightings;
  };

  my.renderPieChart = function() {
    // var ids = $('.question').id.split('-')[1];
    var ids = [ 'noise', 'education', 'inequality' ];
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
      min: 0,
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
      $.cookie('worldtopia', $.toJSON(weightings));
      my.showNotification('alert', 'Saved your weightings');
      });

    var userData = $.parseJSON($.cookie('worldtopia'));
    for(questionId in userData) {
      $('#weighting-' + questionId).slider('value', userData[questionId]);
    }
  }
  return my;
}(jQuery, OpenHDI || {}));

