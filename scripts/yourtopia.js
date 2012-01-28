var IndexBuilder = function () {
	this.universe = [ // dummy variables hard-coded in for now
		{
			variable: 'education-spending',
			label: 'Education spending (% of GDP)'
		},
		{
			variable: 'infrastructure-spending',
			label: 'Infrastructure spending (% of GDP)'
		},
		{
			variable: 'life-expectancy',
			label: 'Life expectancy at birth'
		},
		{
			variable: 'schooling',
			label: 'Mean years of schooling'
		},
		{
			variable: 'press-freedom',
			label: 'Press freedom index'
		},
		{
			variable: 'undernourishment',
			label: 'Undernourishment (% of population)'
		},
		{
			variable: 'birth-rate',
			label: 'Birth rate'
		}
	];
};

IndexBuilder.prototype = {
	

}



$(function () {
	var ib = new IndexBuilder();
});