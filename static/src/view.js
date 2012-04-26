YOURTOPIA.View = function($) {

  var views = {};

  views.About= Backbone.View.extend({
    initialize: function() {},
    render: function() {
      var page_title = 'About page headline h1';
      $('.page-header h1').html(page_title);
    }
  });

  views.IndexCreate = Backbone.View.extend({
    initialize: function() {},
    render: function() {
      //var page_title = 'This is Yourtopia';
      var measure, measure_name;
      var measures_shuffled = [];
      //$('.page-header h1').html(page_title);
      var self = this;
      var svg_el = this.$el;
      // main slider config
      self.width = svg_el.width();
      self.height = svg_el.height();
      self.sliderPaddingTop = 45;
      self.sliderPaddingBottom = 20;
      self.sliderRange = self.height - self.sliderPaddingTop - self.sliderPaddingBottom;
      self.startY = 0; // dragging start value
      // sub slider config
      self.subSliderWidth = 390;
      self.subSliderHeight = 120;
      self.subSliderPaddingTop = 30;
      self.subSliderPaddingBottom = 9;
      self.subSliderSizeFactor = 300;
      self.subSliderRange = self.subSliderHeight - self.subSliderPaddingTop - self.subSliderPaddingBottom;
      self.svg = Raphael(svg_el[0], self.width, self.height);

      // collect info on which model parameters are
      // actually backed by data.
      // Get a randomized list of names.
      for (var n in this.model.attributes.weighted_measures) {
        measure = this.model.attributes.weighted_measures[n];
        if (!this.model.has(measure + '_weight')) {
          console.log('Warning: ' + measure + ' is not defined in model.');
          continue;
        }
        measures_shuffled.push(measure);
      }
      self.num_sliders = measures_shuffled.length;
      measures_shuffled = views.shuffle(measures_shuffled);
      self.slider_width = self.width / self.num_sliders;
      var slider_count = 0;

      // Create main sliders
      for (var m in measures_shuffled) {
        measure = measures_shuffled[m];
        measure_name = measure + '_weight';
        var x_middle = slider_count * self.slider_width + (self.slider_width / 2);
        // draw vertical slider line
        self.line = self.svg.path(
          'M' + parseInt(x_middle, 10) + ' ' + self.sliderPaddingTop +
          'L' + parseInt(x_middle, 10) + ' ' + (self.sliderRange + self.sliderPaddingTop))
          .attr({'stroke': '#666', 'stroke-width': '1'});
        // draw text label
        // TODO: replace with i18n label
        /*
        self.svg.text(x_middle, self.sliderPadding + self.sliderRange + 40, this.model.attributes.weighted_measures[m])
          .attr({'font-size': '13px'});
          */
        // draw slider handle
        self.handle = self.svg.circle(
          x_middle,
          self.sliderRange - (this.model.get(measure_name) * self.sliderRange) + self.sliderPaddingTop,
          views.radius(this.model.get(measure_name)))
          .attr({
              'cursor': 'pointer',
              'fill': 'white',
              'stroke': '#666',
              'stroke-width': '2'
          });
        self.handle.id = measure_name;
        self.handle.drag(onMoveSliderHandler, startDragSliderHandler);
        self.handle.hover(onMouseEnterSliderHandler, onMouseOutSliderHandler);
        slider_count++;
      }  // end: iterate main index categories

      // iterate categories once more to create detail panels
      var details_el = $('.measure-details');
      var buttons_el = $(document.createElement('div')).attr('class', 'buttons');
      var panels_el = $(document.createElement('div')).attr('class', 'panels');
      var subslider_svg = {}; // for further reference

      for (m in measures_shuffled) {
        measure = measures_shuffled[m];
        measure_name = measure + '_weight';

        // button bar element
        var div = $(document.createElement('div')).attr('class', 'details-button ' + measure);
        div.css({width: self.slider_width + 'px'});
        var a = $(document.createElement('a')).attr('href', '#');
        a.text(i18n('category_headline_' + measure));
        a.click(measure, detailPanelClickHandler);
        div.append(a);
        buttons_el.append(div);

        // detail panel
        var detail_panel = $(document.createElement('div')).attr('class', 'details-panel ' + measure);
        detail_panel.append('<div class="text">' + i18n('category_headline_' + measure) + '</div>');
        var subsliders_cnt_el = $(document.createElement('div')).addClass('subsliders-container');
        subsliders_cnt_el.css({width: self.subSliderWidth + 'px'});
        detail_panel.append(subsliders_cnt_el);
        var subsliders_el = $(document.createElement('div')).addClass('subsliders');
        var subsliderLabels_el = $(document.createElement('div')).addClass('subslider-labels');
        subsliderLabels_el.css({width: self.subSliderWidth + 'px'});
        subsliders_cnt_el.append(subsliders_el);
        subsliders_cnt_el.append(subsliderLabels_el);

        // create sliders
        // each measure has 3 sub-measures. Hardcoded here for now.
        var sub_measures = ['1', '2', '3'];
        sub_measures = views.shuffle(sub_measures);
        subslider_svg[measure] = Raphael(subsliders_el[0], self.subSliderWidth, self.subSliderHeight);
        // width of one sub-slider
        var subSliderSingleWidth = self.subSliderWidth / sub_measures.length;

        for (var i in sub_measures) {
          var submeasure_name = measure + sub_measures[i];
          var x = i * subSliderSingleWidth + (subSliderSingleWidth / 2);
          // skip if metadata undefined
          if (typeof this.sourceMetadata[submeasure_name] === 'undefined') {
            continue;
          }
          // draw vertical slider line
          self.line = subslider_svg[measure].path(
            'M' + parseInt(x, 10) + ' ' + self.subSliderPaddingTop +
            'L' + parseInt(x, 10) + ' ' + (self.subSliderRange + self.subSliderPaddingTop))
            .attr({'stroke': '#666', 'stroke-width': '1'});
          // draw text label
          // TODO: replace with i18n label
          subslider_svg[measure].text(x, self.subSliderPaddingTop + self.sliderRange + 10, submeasure_name)
            .attr({'font-size': '13px'});
          // draw slider handle
          self.handle = subslider_svg[measure].circle(
            x,
            self.subSliderPaddingTop, // default = max
            views.radius(1.0, self.subSliderSizeFactor))
            .attr({
                'cursor': 'pointer',
                'fill': 'white',
                'stroke': '#666',
                'stroke-width': '2'
            });
          self.handle.id = submeasure_name + '_weight';
          self.handle.drag(onMoveSubSliderHandler, startDragSubSliderHandler);
          self.handle.hover(onMouseEnterSliderHandler, onMouseOutSliderHandler);
          // description text
          // TODO: make language user-selectable
          if (typeof this.sourceMetadata[submeasure_name] !== 'undefined') {
            if (typeof this.sourceMetadata[submeasure_name].label[LANG] !== 'undefined') {
              detail_panel.find('.text').append('<p class="head '+ submeasure_name +'">'+ this.sourceMetadata[submeasure_name].label[LANG] +'</p>');
              subsliderLabels_el.append('<div class="subslider-label" style="width:'+ (self.subSliderWidth/sub_measures.length - 10) +'px">'+ this.sourceMetadata[submeasure_name].label[LANG] +'</div>');
            } else {
              console.log('WARNING: Undefined label: ', submeasure_name);
            }
            if (typeof this.sourceMetadata[submeasure_name].description[LANG] !== 'undefined') {
              detail_panel.find('.text').append('<p class="description '+ submeasure_name +'">'+ this.sourceMetadata[submeasure_name].description[LANG] +'</p>');
            } else {
              console.log('Undefined description: ', submeasure_name);
            }
          } else {
            console.log('Undefined metadata: ', submeasure_name);
          }
        } // end for sub_measures iteration
        panels_el.append(detail_panel);
        //console.log(measure_name, this.model.get(measure_name));
      }
      details_el.append(buttons_el);
      details_el.append(panels_el);

      // mouse enter/out
      function onMouseEnterSliderHandler() {
        this.attr('fill', 'lightyellow');
      }
      function onMouseOutSliderHandler() {
        this.attr('fill', 'white');
      }
      // drag handlers
      function onMoveSliderHandler(dx,dy,x,y,evt) {
        var newY = Math.min(self.sliderRange + self.sliderPaddingTop, Math.max(self.sliderPaddingTop, self.startY + dy));
        var newVal = (self.sliderRange + self.sliderPaddingTop - newY) / self.sliderRange;
        //console.log(dx, dy, newY, newVal);
        this.attr({
          'cy': newY,
          'r': views.radius(newVal)}
        );
        self.model.set(this.id, newVal);
      }
      function startDragSliderHandler(x,y){
        self.startY = this.attr('cy');
      }
      function onMoveSubSliderHandler(dx,dy,x,y,evt) {
        var newY = Math.min(self.subSliderRange + self.subSliderPaddingTop, Math.max(self.subSliderPaddingTop, self.startY + dy));
        var newVal = (self.subSliderRange + self.subSliderPaddingTop - newY) / self.subSliderRange;
        //console.log(dx, dy, newY, newVal);
        this.attr({
          'cy': newY,
          'r': views.radius(newVal, self.subSliderSizeFactor)}
        );
        if (newVal === 0.0) {
          // TODO: check if all subsliders of this category are zero
          // and disable main slider in case
        }
        self.model.set(this.id, newVal);
      }
      function startDragSubSliderHandler(x,y) {
        self.startY = this.attr('cy');
      }
      // detail panel click
      function detailPanelClickHandler(evt) {
        evt.preventDefault();
        self.showDetailPanel(evt.data);
      }

    },
    showDetailPanel: function(measure) {
      //console.log('showDetailPanel:', measure);
      // hide all which might be open
      $('.details-panel').hide();
      // is clicked one the current one?
      var isCurrent = $('.details-button.' + measure).hasClass('current');
      $('.details-button').removeClass('current');
      if (!isCurrent) {
        // set button active
        $('.details-button.' + measure).addClass('current');
        // show panel
        var panel = $('.details-panel.' + measure);
        panel.show();
      }
    },
    setSourceMetadata: function(data){
      //console.log('views.IndexCreate.setSourceMetadata() called.');
      this.sourceMetadata = data;
    }
  });
  
  /**
   The view for displaying an index with some data visualization
   **/
  views.IndexView = Backbone.View.extend({
    initialize: function() {},
    render: function() {
      var self = this;
      // load SVG map and place it's region shapes in the DOM
      // as Raphael objects
      self.map_regions = {};
      jQuery.get('/static/maps/italy.svg', {}, function(data){
        var svg_el = self.$('.svgmap');
        var targetHeight = 500;
        var originalMapWidth = 500; // this is only true for the used SVG italy map
        var originalMapHeight = 701; // this is only true for the used SVG italy map
        var scaleFactor = targetHeight / originalMapHeight;
        var svg = new Raphael(svg_el[0], originalMapWidth*scaleFactor, originalMapHeight*scaleFactor);
        var path_list = jQuery(data).find('path');
        for (var p in path_list) {
          // jQuery(data).find('path') returns a whole lot of crap...
          // Some additional tests are made to only use SVG path objects
          var el = path_list[p];
          if (typeof el == 'object') {
            var d = jQuery(el).attr('d');
            if (d) {
              var region = jQuery(el).attr('data-nuts2');
              self.map_regions[region] = svg.path(d.replace(',', ' '))
                .attr({'stroke': '#cccccc', 'stroke-width': '1px'})
                .hover(onRegionMouseEnter, onRegionMouseOut);
              self.map_regions[region].transform('s'+ scaleFactor.toFixed(5) +','+ scaleFactor.toFixed(5) +',0,0');
              self.map_regions[region].id = 'path-' + region;
            }
          }
        }
      }, 'xml');
      // event handlers
      function onRegionMouseEnter(a,b,c) {
        var idparts = this.id.split('-');
        self.highlightRankingRegion(this, idparts[1]);
      }
      function onRegionMouseOut(a,b,c) {
        self.lowlightRankingRegions(this);
      }
    },
    // if updateAfterSetSourceData is true, setSourceData will trigger update function
    updateAfterSetSourceData: false,
    setSourceData: function(data){
      //console.log('views.IndexView.setSourceData() called.');
      this.sourceData = data;
      // remove load notification
      this.$('.result-loading').hide();
      this.$('.result-available').show();
      if (this.updateAfterSetSourceData) {
        this.update();
      }
    },
    setSourceMetadata: function(data){
      //console.log('views.IndexView.setSourceMetadata() called.');
      this.sourceMetadata = data;
    },
    update: function() {
      //console.log('Result update triggered');
      var self = this;
      /**
       Here the index calculation and display is done
       **/
      //console.log(this.sourceData);
      if (typeof this.sourceData == 'undefined') {
        // queue execution for when data is available
        this.updateAfterSetSourceData = true;
        return;
      }
      // calculate region ranking
      var region_ranking = []; // tuples for sorting!
      var categories = this.model.get('weighted_measures');
      var region_code;
      for (region_code in this.sourceData.regions) {
        var index_value = 0;
        var num_index_values = 0;
        //console.log(region_code, this.sourceData.regions[region_code]);
        for (var c in categories) {
          // categories[c] is the index category, e.g. "environment"
          var category_weight = this.model.get(categories[c] + '_weight');
          for (var series_id in this.sourceData.series[categories[c]]) {
            // series_id is e.g. "environment1"
            //console.log(series_id);
            if (typeof this.sourceData.series[categories[c]][series_id][region_code] == 'undefined'){
              console.log('WARNING: No data for region "' + region_code + '", series "' + series_id + '"');
            } else {
              // we use the value from the most recent year
              var years = [];
              for (var year in this.sourceData.series[categories[c]][series_id][region_code]){
                years.push(parseInt(year, 10));
              }
              years.sort();
              var max_year = years[years.length-1];
              //console.log('region:', region_code, 'series_id:', series_id, 'years:', years, 'max_year:', max_year);
              var value = this.sourceData.series[categories[c]][series_id][region_code][max_year].value_normalized;
              if (typeof value != 'number') {
                console.log('WARNING: series=' + series_id + ' region=' + region_code + ' year=' + max_year + ' normalized value has invalid type: ' + (typeof value));
              } else if (isNaN(value)) {
                console.log('WARNING: series=' + series_id + ' region=' + region_code + ' year=' + max_year + ' normalized value is NaN');
              }
              //console.log('region:', region_code, 'series_id:', series_id, 'years:', years, 'max_year:', max_year, 'value:', value);
              
              var subWeight = 1.0; // default single measure factor
              if (self.model.has(series_id + '_weight')) {
                subWeight = self.model.get(series_id + '_weight');
              }

              if (this.sourceMetadata[series_id].high_is_good) {
                index_value += value * subWeight * category_weight;
              } else {
                index_value += (1 - value) * subWeight * category_weight;
              }
              
              num_index_values++;
            }
            
          }
        }
        region_ranking.push({region_code: region_code, value: index_value / num_index_values});
      }
      // sort ranking descending
      region_ranking.sort(function(a,b){
        return b.value - a.value;
      });
      //// display ranking
      // color scale for use in the map
      var map_color_scale = new chroma.ColorScale({
        //colors: ['#FAFBF9', '#10C3EA'],
        colors: chroma.brewer['Blues'],
        limits: [-0.0000001, region_ranking[0].value]
      });
      this.$('#rank').empty();
      for (var n in region_ranking) {
        region_code = region_ranking[n].region_code;
        var row = jQuery(document.createElement('div')).addClass('rankrow ' + region_code);
        this.$('#rank').append(row);
        row.append('<div class="rowlabel"><span>' + this.sourceData.regions[region_code] +
            '</span></div><dic class="barcontainer"></div>');
        // create bars
        console.log('region rank value:', region_ranking[n].value);
        var color = map_color_scale.getColor(region_ranking[n].value);
        var bar_element = jQuery(document.createElement('div'))
          .addClass('bar')
          .css({
            'background-color': color.hex(),
            'width': ((region_ranking[n].value / region_ranking[0].value) * 100.0).toFixed(1) + '%'
          })
          .html('&nbsp;');
        row.find('.barcontainer').append(bar_element);
        row.find('*').mouseenter({'context': self, 'region': region_code}, self.rankRowMouseEnterHandler);
        row.find('*').mouseout({'context': self, 'region': region_code}, self.rankRowMouseOutHandler);
        // adjust region color in map
        self.map_regions[region_code].attr('fill', color.hex());
      }
      this.$('#rank').append('</tbody></table>');
      this.$el.show();
    },
    rankRowMouseEnterHandler: function(evt){
      evt.stopPropagation();
      //console.log(evt.data.context.map_regions);
      //console.log(this, self, self.map_regions, evt.data, self.map_regions[evt.data]);
      evt.data.context.highlightRankingRegion(evt.data.context.map_regions[evt.data.region], evt.data.region);
    },
    rankRowMouseOutHandler: function(evt){
      evt.stopPropagation();
      evt.data.context.lowlightRankingRegions(evt.data.context.map_regions[evt.data.region]);
    },
    showMapTooltip: function(evt, x, y, obj) {
      var self = this;
      var w = $(window).width();
      //console.log('showMapTooltip', evt, obj.id);
      var el = $('#bubble');
      // get region ID
      var idparts = obj.id.split('-');
      el.html(self.sourceData.regions[idparts[1]]);
      el.css({top: evt.pageY + 10});
      if (evt.pageX < (w - el.width() - 30)) {
        el.css({left: evt.pageX + 30});
      } else {
        el.css({left: evt.pageX - 30 - el.width()});
      }
      el.show();
    },
    hideMapTooltip: function(obj) {
      $('#bubble').hide();
    },
    highlightRankingRegion: function(raphael_obj, region) {
      // Ranking highlight
      jQuery('#rank .' + region + ' .rowlabel. span').addClass('highlight');
      // Map highlight
      raphael_obj.toFront();
      raphael_obj.attr('stroke', '#ce6600');
      raphael_obj.g = raphael_obj.glow({
        width: 1,
        color: '#ce6600',
        opacity: 1
      });
    },
    lowlightRankingRegions: function(raphael_obj) {
      // Ranking bar
      jQuery('#rank .rowlabel. span.highlight').removeClass('highlight');
      // Map element
      raphael_obj.attr('stroke', '#ffffff');
      raphael_obj.g.remove();
    }
  });
  
  /**
   The view for displaying an index with some data visualization
   **/
  views.IndexShare = Backbone.View.extend({
    initialize: function() {},
    render: function() {
      var self = this;
      console.log('views.IndexShare.render: model.hasChanged? ', self.model.hasChanged());
    }
  });
  

  views.radius = function(value, factor) {
    if (typeof factor == 'undefined') {
      factor = 700;
    }
    return 7 + Math.sqrt(factor * value);
  };

  views.shuffle = function(ary) {
    var s = [];
    while (ary.length) {
      s.push(ary.splice(Math.random() * ary.length, 1)[0]);
    }
    return s;
  };

  return views;

}(jQuery);


