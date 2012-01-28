/*Data pulling */
var title = "My Title";
var subtitle = "none";

var categories = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 
                    2009, 2010, 2011];
                    
var data_series = [{
			name: 'Campania',
			data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
		}, {
			name: 'Molise',
			data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
		}, {
			name: 'Lazio',
			data: [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
		}, {
			name: 'Marche',
			data: [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
		}]

var ylabel = "My index";

/*Data Pulling end*/
var chart;
$(document).ready(function() {
	chart = new Highcharts.Chart({
		chart: {
			renderTo: 'container',
			defaultSeriesType: 'line',
			marginRight: 130,
			marginBottom: 25
		},
		title: {
			text: title,
			x: -20 //center
		},
		subtitle: {
			text: subtitle,
			x: -20
		},
		xAxis: {
			categories: categories
		},
		yAxis: {
			title: {
				text: ylabel
			},
			plotLines: [{
				value: 0,
				width: 1,
				color: '#808080'
			}]
		},
		tooltip: {
			formatter: function() {
	                return '<b>'+ this.series.name +'</b><br/>'+
					this.x +': '+ this.y +'°C';
			}
		},
		legend: {
			layout: 'vertical',
			align: 'right',
			verticalAlign: 'top',
			x: -10,
			y: 100,
			borderWidth: 0
		},
		series: data_series
	});
	
	
});
	
