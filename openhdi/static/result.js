function yourtopiaSunburst() {
  var vis = new pv.Panel()
    .width(sunburstWidth)
    .height(sunburstWidth)
		.canvas('weights')
	
    ;

  var partition = vis.add(pv.Layout.Partition.Fill)
    .nodes(pv.dom(weights).root("Weightings").nodes())
	
    .size(function(d) {
      return d.nodeValue
      })
      .order("descending")
      .orient("radial");
	
  partition.node.add(pv.Wedge)
    .fillStyle(pv.colors("#f0f0f0", "#999999", "#cb4b4b", "#afd8f8", "#edc240", "green", "blue", "yellow", "white", "blue", "black", "red", "green", "pink", "yellow", "blue").by(function(d) {
        return d.parentNode && d.parentNode.nodeName
      }))
      .strokeStyle("#fff")
      .lineWidth(.5)
	
	  
      .title(function(d) {
          return d.nodeName
        })
      ;

  partition.label.add(pv.Label)
    .text(function(d) {
        return d.nodeName.substr(0,15)
      })
    .visible(function(d) { 
        // return d.angle * d.outerRadius >= 6
        return d.angle * d.outerRadius >= 6
        });

  vis.render();
}

