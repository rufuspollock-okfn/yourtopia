function yourtopiaSunburst() {
  var vis = new pv.Panel()
    .width(400)
    .height(400)
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
    .fillStyle(pv.Colors.category19().by(function(d) {
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

