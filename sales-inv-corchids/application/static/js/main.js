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
var set_message = function(message){
	jQuery(function () {
		  jQuery.notifyBar({
		    html: message,
		    delay: 2000,
		    animationSpeed: "normal"
		  });  
		});
}

function add_editable(parent,child, data, id, field_name){
	    parent.append(child)
	    .append('span')
	    .attr("contenteditable", true)
	    .attr('id',id+"_"+field_name)
	    .text(data);
	    
}
function add_button(parent,text){
	var button = parent.append('button');
	    button.text(text)
	      .attr('class','btn btn-default btn-xs');
	return button
}

function add_button_onclick(parent,child,function_name,text){
	var ch = parent.append(child);
	var button = add_button(ch,text);
	button.attr('onclick',function_name);
}

function add_button_method(parent, child, action,text){
	var ch = parent.append(child);
	var form = ch.append('form');
	form.attr('method','get');
	form.attr('action',action);
	add_button(form,text);
}
function clear_create_rows(wk_summ){
	var tbody = d3.select("tbody#summary")
    
    wk_summ.forEach(function (row){
    	var tr = tbody.append('tr');
    	tr.append('td').text(row.plant);
    	tr.append('td').text(row.forecast);
    	tr.append('td').text(row.reserved);
    	add_editable(tr,'td',row.wanted,row.plant_key+"_"+row.week_key,'wanted');
    	add_editable(tr,'td',row.actual,row.plant_key+"_"+row.week_key,'actual');
        add_button_method(tr,'td','/plantweek/'+row.week_key+'/'+row.plant_key,'view');
        var msg = "Update of "+row.plant+": ";
        add_button_onclick(tr,'td',"handle_update("+row.plant_key+","+row.week_key+",'"+msg+"')",'update');
    });

}

function update_plantgrow(plt, wk, wnt, act,msg){

	$.ajax({
	    type: "POST",
	    url: "/plantgrow/update/",
	    // The key needs to match your method's input parameter (case-sensitive).
	    data: JSON.stringify({plant:plt,week:wk,wanted:wnt,actual:act}),
	    contentType: "application/json; charset=utf-8",
	    dataType: "json",
	    success: function(data){
	    	var message = msg + " Failed!!";
	    	if (data.status == 'success'){message = msg + " Succeeded!!!";}
	    	set_message(message)
	     },
	    error: function(data){
	        var json = $.parseJSON(data);
	        alert(json.error);},
	    failure: function(data){
	        var json = $.parseJSON(data);
	        alert(json.error);}
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


