YOURTOPIA.View = function($) {

  var views = {};

  views.IndexCreate = Backbone.View.extend({
    readOnly: false,
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
        // draw slider handle
        self.handle = self.svg.circle(
          x_middle,
          self.sliderRange - (this.model.get(measure_name) * self.sliderRange) + self.sliderPaddingTop,
          views.radius(this.model.get(measure_name)))
          .attr({
              'fill': 'white',
              'stroke': '#666',
              'stroke-width': '2'
          });
        self.handle.id = measure_name;
        if (!this.readOnly) {
          self.handle.attr('cursor', 'pointer');
          self.handle.drag(onMoveSliderHandler, startDragSliderHandler);
          self.handle.hover(onMouseEnterSliderHandler, onMouseOutSliderHandler);
        }
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
        detail_panel.append('<div class="text"></div>');
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
                'fill': 'white',
                'stroke': '#666',
                'stroke-width': '2'
            });
          self.handle.id = submeasure_name + '_weight';
          if (!this.readOnly) {
            self.handle.attr('cursor', 'pointer');
            self.handle.drag(onMoveSubSliderHandler, startDragSubSliderHandler);
            self.handle.hover(onMouseEnterSliderHandler, onMouseOutSliderHandler);
          }
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

      // saving / sharing
      if (!this.readOnly) {
        jQuery('.sharing button').click(function(){
          var json_data = JSON.stringify(self.model);
          // create a form on the page
          $('body').append('<form id="saveform" action="/edit/" method="post"><input type="hidden" class="input-data" name="data" /></form>');
          $('#saveform .input-data').val(json_data);
          // form is submitted and user redirected to /edit/<id>/
          $('#saveform').trigger('submit');
        });
      }

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
    isRendered: false,
    timelineIsRendered: false,
    isMapInitialized: false,
    mapRegions: {},
    timelineLineObjects: {},
    timelineLabelObjects: {},
    config: {
      timeline: {
        paddingTop: 0,
        paddingRight: 0,
        paddingBottom: 0,
        labelColumnWidth: 90,
        slotLabelHeight: 30
      }
    },
    initialize: function() {
      console.log('IndexView initialize()');
      var self = this;
      this.model.on('change', function(){
        if (!self.isRendered) {
          self.render();
        } else {
          self.update();
        }
      });
    },
    render: function() {
      console.log('IndexView render()');
      var self = this;
      // load SVG map and place it's region shapes in the DOM
      // as Raphael objects
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
              self.mapRegions[region] = svg.path(d.replace(',', ' '))
                .attr({'stroke': '#cccccc', 'stroke-width': '1px'})
                .hover(onRegionMouseEnter, onRegionMouseOut);
              self.mapRegions[region].transform('s'+ scaleFactor.toFixed(5) +','+ scaleFactor.toFixed(5) +',0,0');
              self.mapRegions[region].id = 'path-' + region;
            }
          }
        }
        self.isMapInitialized = true;
      }, 'xml');
      // event handlers
      function onRegionMouseEnter(a,b,c) {
        var idparts = this.id.split('-');
        self.highlightRankingRegion(this, idparts[1]);
      }
      function onRegionMouseOut(a,b,c) {
        self.lowlightRankingRegions(this);
      }

      // when timeline tab is shown, re-render the timeline view.
      // this is due to a Raphael/Webkit bug.
      this.$('a[data-toggle="tab"]').on('shown', function (e) {
        var href = $(e.target).attr('href');
        if (href === '#timeline') {
          self.renderTimeline();
        }
      });

      self.isRendered = true;
    },
    renderTimeline: function() {
      console.log('IndexView renderTimeline()');
      // render timeline view
      var self = this;
      var tl_el = self.$('#timeline');
      tl_el.empty();
      if (typeof self.model.to_year === null) {
        // model is not yet ready
        return;
      }
      self.config.timeline.width = tl_el.width();
      self.config.timeline.height = tl_el.height();
      self.config.timeline.numSlots = self.model.to_year - self.model.from_year + 1;
      var tl_svg = new Raphael(tl_el[0], self.config.timeline.width, self.config.timeline.height);
      //var frame = tl_svg.rect(0, 0, self.config.timeline.width, self.config.timeline.height)
      //  .attr('stroke', '#ff0000')
      //  .attr('stroke-width', 1);
      self.config.timeline.slotWidth = (self.config.timeline.width -
        self.config.timeline.paddingRight - self.config.timeline.labelColumnWidth) /
        self.config.timeline.numSlots;
      self.config.timeline.slotHeight = (self.config.timeline.height -
        self.config.timeline.paddingTop - self.config.timeline.paddingBottom -
        self.config.timeline.slotLabelHeight);
      // slot lines and labels
      var slotXOffset;
      var values;
      for (var n=0; n<self.config.timeline.numSlots; n++) {
        var labelText = self.model.from_year + n;
        slotXOffset = n * self.config.timeline.slotWidth + (self.config.timeline.slotWidth / 2);
        var textYPos = self.config.timeline.paddingTop + 10;
        var lineYPosTop = self.config.timeline.paddingTop + self.config.timeline.slotLabelHeight;
        var lineYPosEnd = self.config.timeline.height - self.config.timeline.paddingBottom;
        tl_svg.text(slotXOffset, textYPos, labelText)
          .attr({
            'font-family':'Helvetica Neue',
            'fill':'#333'
          });
        tl_svg.path('M' + slotXOffset + ',' + lineYPosTop + 'L' + slotXOffset + ',' + lineYPosEnd)
          .attr('stroke', '#cccccc');
      }
      // get minimum and maximum value
      var min = 1;
      var max = 0;
      var span = 0;
      for (var p=0; p<self.model.length; p++) {
        values = self.model.at(p).get('values');
        for (var v in values) {
          min = Math.min(min, values[v]);
          max = Math.max(max, values[v]);
        }
      }
      span = max - min;
      // time series
      for (var t=0; t<self.model.length; t++) {
        var series = self.model.at(t);
        //console.log(series, series.id);
        values = series.get('values');
        var positions = []; // all positions for this time series
        var yPos;
        for (n=0; n<self.config.timeline.numSlots; n++) {
          var thisYear = self.model.from_year + n;
          slotXOffset = n * self.config.timeline.slotWidth + (self.config.timeline.slotWidth / 2);
          yPos = ((1-((values[thisYear]-min)/(max - min))) * (self.config.timeline.slotHeight-10)) +
            self.config.timeline.paddingTop + self.config.timeline.slotLabelHeight + 5;
          positions.push([slotXOffset, yPos]);
          // circle dot
          /*
          tl_svg.circle(slotXOffset, yPos, 2)
            .attr('fill', '#2b8ec1')
            .attr('stroke', 'none');
          */
          
        }
        // draw line
        var pathstring = '';
        for (pos = 0; pos<positions.length; pos++) {
          if (pos === 0) {
            pathstring += 'M';
          } else {
            pathstring += 'L';
          }
          pathstring += positions[pos][0] + ',' + positions[pos][1];
        }
        self.timelineLineObjects[series.id] = tl_svg.path(pathstring)
          .attr({
            'stroke': '#3d9bc8',
            'stroke-width': 1.5,
            'title': series.get('region_label')
          });
        self.timelineLineObjects[series.id].hover(onLineMouseEnter,
          onLineMouseOut, {id: series.id});
        // label (invisible) at last y position

        var labelX = positions[(positions.length - 1)][0];
        var labelY = positions[(positions.length - 1)][1];
        self.timelineLabelObjects[series.id] = tl_svg.text(labelX + 7, labelY, series.get('region_label'))
          .attr({
            'font-family': 'Helvetica Neue',
            'font-size': '12px',
            'fill': '#fff',
            'text-anchor': 'start'
          });
      }

      function onLineMouseEnter(evt, x, y){
        //console.log(evt, x, y, this);
        var self2 = this;
        self.timelineLabelObjects[this.id]
          .toFront()
          .animate({fill: '#000'});
        self.timelineLineObjects[this.id]
          .attr('stroke-width', 3)
          .attr('stroke', '#3d9bc8')
          .toFront();
        $.each(self.timelineLineObjects, function(id,obj){
          if (self2.id != id) {
            obj.animate({'stroke-width': 1.5, stroke: '#9fbcc9'}, 200, 'linear');
            self.timelineLabelObjects[id].attr({fill: '#fff'});
          }
        });
        
      }
      function onLineMouseOut(evt){
        /*
        $.each(self.timelineLineObjects, function(id,obj){
          obj.animate({'stroke-width': 3, stroke: '#3d9bc8'}, 200, 'linear');
        });
        $.each(self.timelineLabelObjects, function(id,obj){
          obj.animate({fill: '#fff'}, 200, 'linear');
        });
        */
      }

      self.timelineIsRendered = true;
    },
    update: function() {
      console.log('IndexView update()');
      if (!this.isMapInitialized) {
        // too early yet
        return;
      }
      this.$('.result-loading').hide();
      this.$('.result-available').show();
      var self = this;

      self.renderTimeline();
      
      //console.log('IndexView.update() model:', this.model);
      var region_ranking = []; // tuples for sorting!
      
      // iterate through model and collect sortable regions list
      for (var i=0; i<self.model.length; i++) {
        var regionSeries = self.model.at(i);
        //console.log(regionSeries.id, regionSeries);
        var vals = regionSeries.get('values');
        var val = vals[regionSeries.get('to_year')]; // last available year
        //console.log(regionSeries.id, val);
        region_ranking.push({
          region_code: regionSeries.id,
          value: val
        });
      }
      // sort ranking descending
      region_ranking.sort(function(a,b){
        return b.value - a.value;
      });

      // color scale for use in the map
      var map_color_scale = new chroma.ColorScale({
        //colors: ['#FAFBF9', '#10C3EA'],
        colors: chroma.brewer['Blues'],
        limits: [-0.0000001, region_ranking[0].value]
      });
      this.$('#rank').empty();
      for (var n in region_ranking) {
        var myRegionSeries = self.model.get(region_ranking[n].region_code);
        //console.log(myRegionSeries.id, region_ranking[n].value, region_ranking[0].value, region_ranking[n].value / region_ranking[0].value);
        var row = jQuery(document.createElement('div')).addClass('rankrow ' + myRegionSeries.id);
        this.$('#rank').append(row);
        row.append('<div class="rowlabel"><span>' + myRegionSeries.get('region_label') +
            '</span></div><dic class="barcontainer"></div>');
        // create bars
        //console.log('region rank value:', region_ranking[n].value);
        var color = map_color_scale.getColor(region_ranking[n].value);
        var bar_element = jQuery(document.createElement('div'))
          .addClass('bar')
          .css({
            'background-color': color.hex(),
            'width': ((region_ranking[n].value / region_ranking[0].value) * 100.0).toFixed(1) + '%'
          })
          .html('&nbsp;');
        row.find('.barcontainer').append(bar_element);
        row.find('*').mouseenter({'context': self, 'region': myRegionSeries.id}, self.rankRowMouseEnterHandler);
        row.find('*').mouseout({'context': self, 'region': myRegionSeries.id}, self.rankRowMouseOutHandler);
        // adjust region color in map
        //console.log(self.isMapInitialized, self.mapRegions, myRegionSeries.id, self.mapRegions[myRegionSeries.id]);
        self.mapRegions[myRegionSeries.id].attr('fill', color.hex());
      }
      this.$el.show();
    },
    rankRowMouseEnterHandler: function(evt){
      evt.stopPropagation();
      //console.log(evt.data.context.mapRegions);
      //console.log(this, self, self.mapRegions, evt.data, self.mapRegions[evt.data]);
      evt.data.context.highlightRankingRegion(evt.data.context.mapRegions[evt.data.region], evt.data.region);
    },
    rankRowMouseOutHandler: function(evt){
      evt.stopPropagation();
      evt.data.context.lowlightRankingRegions(evt.data.context.mapRegions[evt.data.region]);
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
  views.SaveForm = Backbone.View.extend({
    initialize: function() {},
    render: function() {
      var self = this;
      // set characters left plugin
      //console.log(jQuery('.description-textarea'));
      //console.log(this.$('.description-textarea'));
      
      this.$('.description-textarea').charsLeft({
          maxChars: 200,
          charPrefix: "",
          charSuffix: i18n('sharing_url_charsleft')
      });

      // saving
      jQuery('#save').click(function(evt){
        evt.preventDefault();
        jQuery('#saveform').trigger('submit');
      });
      
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


