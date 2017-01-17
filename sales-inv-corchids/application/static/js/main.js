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


function add_button(parent,text){
	var button = parent.append('button');
	    button.text(text)
	      .attr('class','btn btn-primary btn-xs');
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
    	tr.append('td').attr('id',row.id+"_"+"wanted").text(row.wanted);
    	tr.append('td').attr('id',row.id+"_"+"actual").text(row.actual);
        add_button_method(tr,'td','/plantweek/'+row.id,'view');
        var msg = "Update of "+row.plant+": ";
        flds = {wanted:'i',actual:'i'};
        var td = tr.append('td');
                 td.append('a')
                       .attr('id',row.id+"_"+"edit")
                       .attr('class',"btn btn-primary edit_row")
                       .on('click', function(){
                    	    editRow(row.id,{},flds);   
                       })
                       .text('Edit');
                 td.append('a')
                 .attr('id',row.id+"_"+"save")
                 .attr('class',"btn btn-primary save_row")
                 .on('click', function(){
                	 update = {service_name:'plantgrow',week:row.week_key,plant:row.plant_key};
                	 saveRow(row.id,{},flds,update);
                 })
                 .text('Save');
       var td2 = tr.append('td');
                td2.append('a')
                .attr('id',row.id+"_"+"notes")
                .attr('class',"btn btn-primary edit_row")
                .on('click', function(){
             	    showNotes(row.id);   
                })
                .text('Notes');
           
        //add_button_onclick(tr,'td',"handle_update("+row.plant_key+","+row.week_key+",'"+msg+"')",'update');
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
	    	else{
	    		console.log(data);
	    	}
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

function editRow(rowId, options, fields){  

	   for (var propertyName in fields)
	   {
		   var typ = fields[propertyName];
		   if (typ == 'o')
		   {
			  var opts = options[propertyName];
			  var optField = $('#'+rowId+"_"+propertyName);
			  var name = optField.text();
			  var val = 0;
			  for (i = 0; i < opts.length; i++) { 
				    var n = opts[i].split(":");
				    if (name == n[0]){
				    	val = n[1];
				    }
				}
			  optField.text("");
			  d3.select('[id="'+rowId+'_'+propertyName+'"]')
			    .append("select")
			        .attr("id",rowId+"_sel"+propertyName)
			        .attr("class","form-control")
			          .selectAll("option").data(opts)
			            .enter().append("option")
			            .text(function (d) { return d.split(":")[0];})
			            .attr("value",function (d){ return d.split(":")[1];})
			  $("#"+rowId+"_sel"+propertyName).val(val);
			  
		   }
		   else{
			   var inField = $('#'+rowId+"_"+propertyName);
			   var val = inField.text();
			   inField.text("");
			   inField.css("background-color",'#fff');
			   inField.css("color",'black');
			   d3.select('[id="'+rowId+'_'+propertyName+'"]')
			     .append('span')
			     .attr('contenteditable',true)
			     .attr('id',rowId+"_span"+propertyName)
			     .text(val);
		   }
		   
	   }
	   $("#"+rowId+"_edit").hide();
	   $("#"+rowId+"_save").show();
	}

	function saveRow(rowId, options, fields, update){
		update['id'] = rowId;
		for (var propertyName in fields)
		{
			var typ = fields[propertyName];
			var idm = rowId+"_"+propertyName;
			
			if (typ == 'o'){
				var opts = options[propertyName];
				var ids = rowId+"_sel"+propertyName;
				var optField = $('#'+ids);
				var txtField = $('#'+idm);
				var val = optField.val();
				var name = "";
				for (i = 0; i < opts.length; i++) { 
				    var n = opts[i].split(":");
				    if (val == n[1]){
				    	name = n[0];
				    }
				}
				optField.remove();
				txtField.text(name);
				
			    update[propertyName] = val;
			}
			else{
				var txtField = $('#'+idm);
				var ids = rowId+"_span"+propertyName;
				var sField = $('#'+ids);
				var val = sField.text();
				sField.remove();
				txtField.text(val);
				txtField.css("background-color",'transparent');
				update[propertyName] = val;
			}
		}
		$("#"+rowId+"_edit").show();
	    $("#"+rowId+"_save").hide();
        call_update_service(update);
	}
	
	function call_update_service(update_fields){
		$.ajax({
		    type: "POST",
		    url: "/"+update_fields.service_name+"/update/",
		    // The key needs to match your method's input parameter (case-sensitive).
		    data: JSON.stringify(update_fields),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
		    success: function(data){
		    	var message = "Row Update Failed!!";
		    	if (data.status == 'success'){message = "Row Update Succeeded!!!";}
		    	set_message(message)
		     },
		     error: function(data){
			        console.log(data.responseText);
			        //alert(json.error);},
			    },
			    failure: function(data){
			        console.log(data.responseText);
			        //alert(json.error);
			        }
		});
	}
	
	function save_note(pg_id, note_info,process_func){
		$.ajax({
			type: "POST",
			url: "/notes/save/"+pg_id,
			data: JSON.stringify({note:note_info.note},null,'\t'),
			conttentType: "application/json; charset=utf-8",
			dataType: "json",
			success: function(data){
		    	process_func(pg_id,data.key,note_info);
		     },
		    error: function(data){
			    console.log(data.responseText);
			     //alert(json.error);},
			    },
		    failure: function(data){
			    console.log(data.responseText);
			    //alert(json.error);
			    }
		});
	}
	
	function display_notes(myNotes){
		if (myNotes.length > 0){
			//var table = d3.select('[id="summary-top"]')
			var div = d3.select('.row').insert("div",":nth-child(2)")
			  .append('div').attr('class','col-xs-12 col-md-12');
			div.append('h3').text("... Notes ...");
			var table = div.append('div').attr('class','table-responsive')
			     .append('table');
			
			table.attr('class','table table-condensed');
			  
			var tr = table.append('thead').append('tr');
			
			tr.append('th').text("Note");
			tr.append('th').text("Added By");
			tr.append('th').text("Added Date");
			
			var tbody = table.append('tbody');
			
			var arrayLength = myNotes.length;
   	        for (var i = 0; i < arrayLength; i++){
   	           var noteInfo = myNotes[i];
   	    	   var tr2 = tbody.append('tr');
   	    	   tr2.attr('class', 'added-note')
                  .attr('id', noteInfo.noteId)
                  .append('td')
                  .text(noteInfo.note);
               tr2.append('td').text(noteInfo.added_by);
               tr2.append('td').text(noteInfo.added_date);
               tr2.append('td').html('<span class="close">&times;</span>')
                  .on('click', function() {
                      delete_note(noteInfo.noteId);
                      d3.select(this.parentNode).remove();
                  });
   	         } 
		}
	}
	
	function get_notes(pg_id, process_func){
		$.ajax({
			//type: "GET",
			url: "/notes/get/"+pg_id,
			dataType: "json",
			success: function(data){
		    	process_func(data);
		     },
		     error: function(data){
			        console.log(data.responseText);
			        //alert(json.error);},
			    },
			    failure: function(data){
			        console.log(data.responseText);
			        //alert(json.error);
			        }
		})
	}
	
	function delete_note(note_id){
		$.ajax({
			//type: "GET",
			url: "/notes/delete/"+note_id,
			dataType: "json",
			success: function(data){
		    	console.log('deleted note')
		     },
		     error: function(data){
			        console.log(data.responseText);
			        //alert(json.error);},
			    },
			    failure: function(data){
			        console.log(data.responseText);
			        //alert(json.error);
			        }
		})
	}
