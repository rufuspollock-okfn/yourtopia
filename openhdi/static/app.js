var OpenHDI = (function($, my) {

  my.renderPieChart = function() {
    var data = $('.question').map(function(idx, el) {
      var sliderDiv = $(el).find('.weighting');
      var questionLabel = $(el).find('h3').first().text();
      return { label: questionLabel, data: sliderDiv.slider('value') }
    });

    function shortenLabel(label) {
      if(label && label.length>0) {
        return label.slice(0,15) + ' ...';
      } else {
        return '';
      }
    }

    options = {
      series: {
        pie: { 
          show: true,
          label: {
            // show: false,
            radius: 3/4,
            formatter: function(label, series){
                var out = '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                  + shortenLabel(label)
                  + '</div>';
                return out;
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
              $.each(plot.getData(), function(idx, item) {
                  $("#question-" + item.label).css('color', item.color);
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

  my.setWeighting = function(questionId, val) {
    $("#weighting-" + questionId + '-percent').val(val);
  }

  my.getWeighting = function(questionId) {
    return $("#weighting-" + questionId + '-percent').val();
  }

  my.setupApp = function() {
    var $notification = $('#inline-notification');
    $notification
      .find('button').one('click', function() {
        $(this).parent().slideUp(200);
      }).end()

    $('.weighting').slider({
      value: 100,
      min: 0,
      max: 100,
      step: 1,
      animate: 'fast',
      slide: function(event, ui) {
        questionId = event.target.id.split('-')[1];
        var newValueThis = ui.value;

        var sum = newValueThis;
        $(".weighting").not(this).each(function(s) {
            sum += $(this).slider('value');
        });

        // weights in smallest first order
        var weightList = [];
        $(".weighting").not(this).each(function(idx, el) {
          var curValue = $(el).slider('value');
          weightList.push([curValue, el.id]);
        });
        weightList.sort();

        var toChange = 100 - sum;
        // deduct/add from other value until nothing left
        // we deduct/add equal amounts taking account of min/max
        var numQuestions = $('.question').length-1;
        $(weightList).each(function(idx, tuple) {
          var curValue = tuple[0];
          var _change = Math.round(toChange / (numQuestions));
          var _change = Math.max(0-curValue, Math.min(_change, 100-curValue));
          var newval = curValue + _change;
          toChange -= _change; 
          numQuestions -= 1;
          $('#'+tuple[1]).slider('value', newval);
        });
        
        $(".weighting").not(this).each(function(idx, el) {
            var val = $(this).slider('value');
            fieldId = this.id.split('-')[1];
            my.setWeighting(fieldId, val);
        }); 

        // this field
        // do it separately so we use updated value
        fieldId = this.id.split('-')[1];
        my.setWeighting(fieldId, newValueThis);

        my.renderPieChart();
      }
    });

    // set up slider from weights provided
    $('.weighting-val').each(function(idx, el) {
      fieldId = el.id.split('-')[1];
      el = $(el);
      $('#weighting-' + fieldId).slider('value', el.attr('value'));
    });
  }

  return my;

}(jQuery, OpenHDI || {}));

