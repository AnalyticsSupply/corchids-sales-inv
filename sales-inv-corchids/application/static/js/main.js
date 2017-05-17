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
	      .attr('class','btn btn-primary');
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
    	
    	if (row.notes > 0){
    		tr.append('td').attr('class','font-red').append('strong').text("* "+row.plant);
    	}else{
    		tr.append('td').text(row.plant);
    	}
    	tr.append('td').attr('id',row.id+"_"+"forecast").text(row.forecast);
    	tr.append('td').attr('id',row.id+"_"+"reserved").text(row.reserved);
    	tr.append('td').attr('id',row.id+"_"+"available").text(row.available);
    	tr.append('td').attr('id',row.id+"_"+"actual").text(row.actual);
        add_button_method(tr,'td','/plantweek/'+row.id,'View');
        var msg = "Update of "+row.plant+": ";
        flds = {actual:'i'};
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
                	 update = {service_name:'plantgrow/update/',week:row.week_key,plant:row.plant_key};
                	 saveRow(row.id,{},flds,update);
                	 act = d3.select('[id="'+row.id+'_actual"]').text();
                	 act = parseInt(act);
                	 rsv = d3.select('[id="'+row.id+'_reserved"]').text();
                	 rsv = parseInt(rsv);
                	 fcast = d3.select('[id="'+row.id+'_forecast"]').text();
                	 fcast = parseInt(rsv);
                	 
                	 avail = fcast - rsv;
                	 if (act > 0){
                		 avail = act - rsv;
                	 }
                	 d3.select('[id="'+row.id+'_available"]').text(avail);
                	//var table = d3.select('[id="summary-top"]')
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
			  optField.attr('class','edit-cell');
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
		   else if (typ == 'i'){
			   var inField = $('#'+rowId+"_"+propertyName);
			   var val = inField.text();
			   inField.text("");
			   //inField.css("background-color",'#fff');
			   inField.attr('class','edit-cell');
			   inField.css("display",'');
			   inField.css("color",'black');
			   d3.select('[id="'+rowId+'_'+propertyName+'"]')
			     .append('span')
			     .attr('contenteditable',true)
			     .attr('id',rowId+"_span"+propertyName)
			     .text(val);
		   }
		   else {
			   // DISPLAY/HIDDEN FIELDS
		   }
		   
	   }
	   $("#"+rowId+"_edit").hide();
	   $("#"+rowId+"_save").show();
	}

    function saveRowDT(rowId,options,fields,update,order, model_name){
    	var tableId = model_name+'-table';
    	saveRowDT2(rowId,options,fields,update,order, model_name,tableId);
    }

    function saveRowDT2(rowId,options,fields,update,order, model_name,tableId){
    	saveRow(rowId,options,fields,update);
		var t = $('#'+tableId).DataTable();
		var d = t.row($('#'+rowId)).data();
		for (i=0;i<order.length;i++){
			var prop = order[i];
			d[i] = $('#'+rowId+'_'+prop).text();
		}
		d[order.length] = $('#'+rowId+'_buttons').text();
		t.row($('#'+rowId)).data(d).draw();
		var btnId = rowId+"_buttons";
		add_buttons(rowId,model_name,d3.select('[id="'+btnId+'"]'));
		
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
				txtField.attr('class','display-cell');
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
			else if (typ == 'i'){
				var txtField = $('#'+idm);
				txtField.attr('class','display-cell');	
				var ids = rowId+"_span"+propertyName;
				var sField = $('#'+ids);
				var val = sField.text();
				sField.remove();
				txtField.text(val);
				txtField.css("background-color",'transparent');
				update[propertyName] = val;
			}
			else{
				// DISPLAY ONLY or HIDDEN FIELD
			}
		}
		$("#"+rowId+"_edit").show();
	    $("#"+rowId+"_save").hide();
	    if (update.service_name == 'add'){
	    	call_add_service(update.model_name,update,fields);
	    }
	    else{
	    	call_update_service(update);	
	    }
	}
	
	function call_update_service(update_fields){
		var inData = adjust_data(update_fields);
		$.ajax({
		    type: "POST",
		    url: "/"+update_fields.service_name,
		    // The key needs to match your method's input parameter (case-sensitive).
		    data: JSON.stringify(inData),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
		    success: function(data){
		    	var message = "Row Update Succeeded!!!"
		    	if (data.hasOwnProperty('status')){
		    		message = "Row Update Failed!!";
			    	if (data.status == 'success'){message = "Row Update Succeeded!!!";}
		    	}
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
	
	function call_add_service(model_name, update_fields,fields){
		var rowId = update_fields.id;
		var field_values = {};
		for (var propertyName in fields)
		{
			var typ = fields[propertyName];
			if (typ != 'd'){
				field_values[propertyName] = update_fields[propertyName];
			}
		}
		
		var inData = {};
		inData[model_name] = field_values;
		$.ajax({
			type: "POST",
			url: "/rest/"+model_name+"/",
			headers: { 
		        Accept : "application/json; charset=utf-8",
		        "Content-Type": "application/json; charset=utf-8"
		    },
		    data: JSON.stringify(inData),
		    dataType: "json",
		    success: function(data){
		    	//var id = data.key;
		    	set_message("Row Added Successfully");
		    	convert_save(rowId,data,model_name);
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
			//var div = d3.select('.row').insert("div",":nth-child(2)")
			//  .append('div').attr('class','col-xs-12 col-md-12');
			//div.append('h3').text("... Notes ...");
			var table = d3.select('[id="notes-table"]')
			
			//table.attr('class','table table-condensed');
			  
			//var tr = table.append('thead').append('tr');
			
			//tr.append('th').text("Note");
			//tr.append('th').text("Added By");
			//tr.append('th').text("Added Date");
			
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
               tr2.append('td')
                  .attr('id','del_'+noteInfo.noteId)
                  .html('<span class="close">&times;</span>')
                  .on('click', function() {
                	  var delNote = Number(d3.select(this.parentNode).attr('id'));
                      delete_note(delNote);
                      d3.select(this.parentNode).remove();
                  });
   	         } 
		}
	}
	
	function get_availability_default(pg_id){
		get_availability(pg_id,'plant_avail');
	}
	
	function get_availability(pg_id,wk_nm){
		$.ajax({
			url: "/plantgrow/availability/"+pg_id,
			dataType: "json",
			contentType: 'application/json; charset=UTF-8',
			type: 'GET',
			success: function(data){
				d3.select('[id="'+wk_nm+'"]').text(data.availability);
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
	function addRow(model_name,options, fields, data){
		addRowDel(model_name,options, fields, data, false);
	}
	
	function delRow(rowId,options, fields, update){
		update['id'] = rowId;
    	update['soft_delete'] = true;
    	if (update.service_name != 'add'){
    		call_update_service(update);
    	}
    	
    	$('#'+rowId).remove();
    	$('#delete_modal').modal('hide');
    	$('#modal_del_btn').off('click');
    }
	
	function delRowDT(rowId, options, fields, update){
		update['id'] = rowId;
		update['soft_delete'] = true;
		var t = $('#'+update['model_name']+'-table').DataTable();
		if (update.service_name != 'add'){
    		call_update_service(update);
    	}
    	t.row($('#'+rowId)).remove().draw(false);
    	$('#delete_modal').modal('hide');
    	$('#modal_del_btn').off('click');
	}
	
	function addRowDel(model_name, options, fields, data, addDel){
		var tableId = model_name+"-table";	
		var rowId = tableId+"-newrow";
		data['id'] = rowId;
		data['model_name'] = model_name;
		data['service_name'] = 'add';
		var tr = d3.select('[id="'+tableId+'"]')
		  .select('tbody')
		  .append('tr');
		tr.attr('id',rowId);
		for (var propertyName in fields){
			var typ = fields[propertyName];
			if (typ != 'h'){
				tr.append('td')
				  .attr('id',rowId+"_"+propertyName);
			}			
		}
		var btn_td = tr.append('td');
		  btn_td.attr('id',rowId+'_buttons')
		    .append('a')
		    .attr('id',rowId+"_save")
		    .attr('class','btn btn-primary save_row')
		    .on('click',function (){
		    	  saveRow(rowId,options,fields,data);
		    })
		    .text('Save');
		if (addDel == true){
			btn_td.append('a')
			      .attr('id',rowId+"_del")
			      .attr('class','btn btn-primary del_row')
			      .on('click',function(){
			    	  $('#delete_modal').modal('show');
			    	  $('#modal_del_btn').on('click', function(){
			    		  delRow(rowId,options,fields, data);
			    		  get_availability_default(data['plantgrow']);
			    	  })})
			      .text('Delete');    
		}
		//<a id='{{ crw.id }}_save' class="btn btn-primary save_row" onclick="saveRowCust('{{ crw.id }}')">Save</a	
		editRow(rowId,options,fields);		
	}
	
	function addRowDT(model_name, options, fields, data, order, addDel){
		var tableId = model_name+"-table";
		addRowDT2(model_name, options, fields, data, order, addDel, tableId);
	}
	
	function addRowDT2(model_name, options, fields, data, order, addDel, tableId){	
		var rowId = tableId+"-newrow";
		data['id'] = rowId;
		data['model_name'] = model_name;
		data['service_name'] = 'add';
		var t = $("#"+tableId).DataTable();
		var cArray = [];
		for (i=0;i<order.length;i++){
			var prop = order[i];
			var typ = fields[prop];
			if (typ == 'o'){
				cArray.push("");
			}else{
				if (typ != 'h'){
				   cArray.push(0);
				}
			}
		}
		// add button cell
		cArray.push("");
		var r = t.row.add(cArray).draw(false).node();
		$(r).attr('id',rowId);
		var tdArray = $(r).children();
		for (i=0;i<(order.length + 1);i++){
			var cellId = rowId + "_buttons";
			if (i < order.length){
				cellId = rowId + "_" + order[i];
			}
			$(tdArray[i]).attr('id',cellId);
		}
		var cellId = rowId + "_buttons";
		var btn_td = d3.select('[id="'+cellId+'"]');
		btn_td.attr('id',rowId+'_buttons')
	          .append('a')
	          .attr('id',rowId+"_save")
	          .attr('class','btn btn-primary save_row')
	          .on('click',function (){
	    	     saveRowDT(rowId,options,fields,data,order,model_name);
	    	     var values = []
	    	     for (var i=0;i<order.length;i++){
	    	    	 values.push($('#'+rowId+'_'+order[i]).text());
	    	     }
	    	     values.push($('#'+rowId+'_buttons').text()); // for the buttons
	    	     t.row($('#'+rowId)).data(values).draw(false);
	            })
	          .text('Save');
	    if (addDel == true){
		   btn_td.append('a')
		         .attr('id',rowId+"_del")
		         .attr('class','btn btn-primary del_row')
		         .on('click',function(){
		    	      $('#delete_modal').modal('show');
		    	      $('#modal_del_btn').on('click', function(){
		    	    	  data['model_name'] = model_name;
		    		      delRowDT(rowId,options,fields, data);
		    		      get_availability_default(data['plantgrow']);
		    	      })
		    	   })
		      .text('Delete');    
	     }
	    editRow(rowId,options,fields);	
	}
	
	function convert_save(old_id, new_id,model_name){

		 d3.select('[id="'+old_id+'"]')
		  .attr('id',new_id)
		  .selectAll('td')
		  .each(function(){
		      var oId = d3.select(this).attr('id');
		      var end = oId.split("_")[1]
		      d3.select(this).attr('id',oId.replace(old_id,new_id));
		      if (end == 'buttons'){
		    	  add_buttons(new_id,model_name,d3.select(this));

		      }
		  });
		}

		function add_buttons(rowId, model_name, td_node){
			     var msg = td_node.text().trim();
			     td_node.text("");
		         td_node.insert('a',":first-child")
		           .attr('id',rowId+"_edit")
		           .attr('class','btn btn-primary edit_row')
		           .on('click',function(){
		               edit_row(rowId,model_name);
		           })
		           .text('Edit');
		         td_node.append('a')
		           .attr('id',rowId+"_save")
		           .attr('class','btn btn-primary save_row')
		           .on('click',function(){
		               save_row(rowId,model_name);
		           })
		           .text('Save');
		         if (msg.endsWith('Delete')){
		        	 td_node.append('a')
			           .attr('id',rowId+"_del")
			           .attr('class','btn btn-primary del_row')
			           .on('click',function(){
			               del_row(rowId,model_name);
			           })
			           .text('Delete');
		         }
		         
		         $('#'+rowId+'_save').hide();
		         $('#'+rowId+'_edit').show();
		}
