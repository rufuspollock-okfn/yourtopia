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

    options = {
      series: {
        pie: { 
          show: true,
		   label: {
                    show: false,
                    radius: 3/4,
                    formatter: function(label, series){
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'+label+'<br/>'+Math.round(series.percent)+'%</div>';
                    },
                    background: { 
                        opacity: 0.5,
                        color: '#000'
                    }
                }
        }
      },
      legend: {
        show: false
      },
      hooks: {
        draw: [
            function(plot, options) {
                plot.getData().forEach(function(i) {
                    $("#question-" + i.label).css('color', i.color);
                }); 
            }
        ]
      }
    }

    $.plot($("#pie"), data, options); 
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
      value: 100/$(".weighting").size(),
      min: 1,
      max: 100,
      step: 1,
	create: function( event, ui ) {
	    $(".weighting").each(function(i) {
		var val = 100 / $(".weighting").size();
		fieldId = this.id.split('-')[1];
		$("#weighting-" + fieldId + '-percent').html(val);
            }); 

	},
      slide: function( event, ui ) {
        questionId = event.target.id.split('-')[1];
        my.renderPieChart();

        var sum = 0;
        $(".weighting").each(function(s) {
            sum += $(this).slider('value');
        });

	  var sumOthers = sum - ui.value;
        
          $(".weighting").not(this).each(function(i) {
              var newval = (100 - ui.value) * ($(this).slider('value') / sumOthers);
            $(this).slider('value', newval);
        });
        
        $(".weighting").each(function(i) {
            var val = $(this).slider('value');
            fieldId = this.id.split('-')[1];
            $("#weighting-" + fieldId + '-percent').html(val);
        }); 
      }
    });

    $('#save').click(function(e) {
      e.preventDefault();
      var weightings = my.getWeightings();
      my.WeightingSets.create(
        {weightings: weightings}
        );
      //my.showNotification('alert', 'Saved your weightings');
      
      // TEMP HACK make this ajax
      document.location.reload();
    });
  }
  return my;
}(jQuery, OpenHDI || {}));

