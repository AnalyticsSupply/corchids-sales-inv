var Utils = {
    renderFieldErrorTooltip: function (selector, msg, placement) {
        var elem;
        if (typeof placement === 'undefined') {
            placement = 'right'; // default to right-aligned tooltip
        }
        elem = $(selector);
        elem.tooltip({'title': msg, 'trigger': 'manual', 'placement': placement});
        elem.tooltip('show');
        elem.addClass('error');
        elem.on('focus click', function(e) {
            elem.removeClass('error');
            elem.tooltip('hide');
        });
    }
};

/* Your custom JavaScript here */

function clear_create_rows(wk_summ){
	var tbody = d3.select("tbody#summary")
    
    wk_summ.forEach(function (row){
    	var tr = tbody.append('tr');
    	tr.append('td').text(row.plant);
    	tr.append('td').text(row.wanted);
    	tr.append('td').text(row.actual);
    	tr.append('td').text(row.forecast);
    	tr.append('td').text(row.reserved);
    	var td = tr.append('td');
    	var form = td.append('form');
    	form.attr('method','get');
    	var act = '/plantweek/'+row.week_key+'/'+row.plant_key;
    	form.attr('action',act);
    	var button = form.append('button').text('view');
    	button.attr('class','btn');
    });

}

function call_wk_summ(year, wk_num)
{
	var tbody = d3.select("tbody#summary");
    tbody.selectAll('tr').remove();
	
	$(".col-xs-12.col-md-8 h3").html("Week #"+wk_num+", in "+year+".");
	  var api = "/week_summary/"+year+"/"+wk_num;
	  $.getJSON( api)
	    .done(function( data ) {
	      clear_create_rows(data);
	    });
	}


