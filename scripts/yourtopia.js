var IndexBuilder = function () {
	this.page = {
		$universeComponents: $('.universe .components'),
		$selectionComponents: $('selection .components')
	};

	this.selection = [];

	this.universe = {
		'education-spending': {
			label: 'Education spending (% of GDP)'
		},
		'infrastructure-spending': {
			label: 'Infrastructure spending (% of GDP)'
		},
		'life-expectancy': {
			label: 'Life expectancy at birth'
		},
		'schooling': {
			label: 'Mean years of schooling'
		},
		'press-freedom': {
			label: 'Press freedom index'
		},
		'undernourishment': {
			label: 'Undernourishment (% of population)'
		},
		'birth-rate': {
			label: 'Birth rate'
		}
	};
};

IndexBuilder.prototype = {
	init: function () {
		var listHTML = '';

		$.each(this.universe, function (key, value) {
			var $li = $('<li>' + value.label + '</li>');

			$li.data('key', key);

			$li.click(function () {
				$(this).remove();
				
			})


			listHTML += '<li>' + value.label + '</li>';
		});

		this.page.$universeComponents.append(listHTML);
	},



}



$(function () {
	var ib = new IndexBuilder();
	ib.init();
});