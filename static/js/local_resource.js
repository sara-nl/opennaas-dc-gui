var queue = [];
var VLANarray = [];
var oTable, queueTable, statusTable;
var currentRow;
var currentCell;
var queueTable;


$(document).ready(function()
{  
    init_QueueTable();
    $( "#tabs" ).tabs(); // Build tabs   
    $('#configCommitIndicator').hide(); 
    $('#StatusTable').hide(); //hide table during ajax call
    $('#ConfigTable').hide(); //hide table during ajax call
    $.get("/local/" + $('#resourcename').attr('value') + "/getconfig", callback_GetConfig); //get config using ajax
    $.get("/local/" + $('#resourcename').attr('value') + "/getstatus", callback_GetStatus); //get status using ajax
  
    // event handling for clicking the commit config button in the queue tab
    $("#commitConfigButton").click(function(){
        $('#configCommitIndicator').show(); 
        var myJsonString = JSON.stringify(queue);
        $.ajax({
            type: "POST",
            url: "/local/" + $('#resourcename').attr('value') + "/commit",
            data: myJsonString,
            dataType: 'json',
            async: false,
            error: function( jqXHR, textStatus, errorThrown ){
                console.log(textStatus);
            },
            success: callback_CommitConfig
        });
    });
});

// Function which is called when a config change is succesfully committed
function callback_CommitConfig(data,status) 
{
    $('#configCommitIndicator').hide(); 
    $("#ConfigTable").hide();
    $('#configLoadIndicator').show(); // show the loading gif
    oTable.fnDestroy(); // destroy the current configuration table
    $.get("/local/" + $('#resourcename').attr('value') + "/getconfig", callback_GetConfig); // get config using ajax
    $("#StatusTable").hide();
    $('#statusLoadIndicator').show(); // show the loading gif
    statusTable.fnDestroy(); // destroy the current configuration table
    $.get("/local/" + $('#resourcename').attr('value') + "/getstatus", callback_GetStatus); // get config using ajax
    
    queue = [];
    console.log(queueTable);
    queueTable.fnClearTable();
    $('#tabs ul:first li:eq(2) a').text("Queue");
    console.log(queueTable);
    //queueTable = initQueueTable();
    console.log(queueTable);
}

function callback_GetStatus(data,status) 
{
    var columnArray =[]; 
    for (var i=0; i < Object.keys(data).length; i++) 
    {      
        columnArray[i] = [i, data[i].interfacelong , data[i].adminstatus , data[i].protocolstatus , data[i].description , data[i].macaddresses];  
    }
    statusTable = statusTable = $('#StatusTable').dataTable(buildTableParameters([10,10,10,10,300,10], { "data": columnArray }));
    $("#StatusTable").show();
    $('#statusLoadIndicator').hide();
    $("#StatusTable tr:eq(10)").css({"background": "#eeffee","border": "1px solid #dddddd"});
    
    // Adjust the coloring of the table rows to reflect the status of the interface. Admin down = grey, down = red, up = green
    jQuery.each( $("#StatusTable tr"), function( i, val ) { 
        adminstate = $("#StatusTable tr:eq(" + i + ") td:eq(1)").text();
        if (adminstate == "admin down")  $("#StatusTable tr:eq(" + i + ")").css({"background": "#dddddd","border": "1px solid #dddddd"});
        if (adminstate == "down")  $("#StatusTable tr:eq(" + i + ")").css({"background": "#ffd5d5","border": "1px solid #dddddd"});
        if (adminstate == "up")  $("#StatusTable tr:eq(" + i + ")").css({"background": "#d1ffd1","border": "1px solid #dddddd"});
    });
};

function callback_GetConfig(data,status) 
{
    var columnArray =[];  
    for (var i=0; i < Object.keys(data.interfaces).length; i++) 
    {
        var vlan_string ="";
        for (var v=0 ; v < Object.keys(data.vlans).length; v++) 
        {
            if (data.vlans[v].vlan_id == data.interfaces[i].vlan) vlan_string = data.vlans[v].vlan_id + " - " + data.vlans[v].name;
            
        }
        columnArray[i] = [i, data.interfaces[i].ifname , data.interfaces[i].adminstate , vlan_string , data.interfaces[i].description, "<input type='checkbox' name='checkbox_647c0a15-885c-4cd7-bee4-01cbdfa11ad5'>"];  
    }

    for (var v=0 ; v < Object.keys(data.vlans).length; v++) 
    {
        VLANarray[data.vlans[v].vlan_id] = data.vlans[v].vlan_id + " - " + data.vlans[v].name;
    }
    
    oTable = init_ConfigTable(columnArray,VLANarray);
    $("#ConfigTable").show();
    $('#configLoadIndicator').hide();
};



function init_ConfigTable(columnArray, VLANarray) {
    oTable = $('#ConfigTable').dataTable(buildTableParameters([10,10,10,10,10,10], { "data": columnArray })).makeEditable( {
        "aoColumns": [
            null,
            {
                tooltip: 'Click to enable / shutdown port',
                type: 'select',
                event: 'click',
                onblur: 'cancel',
                submit: 'Ok',
                data: "{'':'Please select...', 'enabled':'enabled','shutdown':'shutdown'}",
                sUpdateURL: function(value, settings){  addToQueue(value,oTable.fnGetPosition( this )); }
            },
            {
                tooltip: 'Click to edit VLAN',
                type: 'select',
                event: 'click',
                onblur: 'cancel',
                submit: 'Ok',
                data: VLANarray,
                sUpdateURL: function(value, settings){ addToQueue(value,oTable.fnGetPosition( this )); }
            },
            {
                tooltip: 'Click to change description',
                event: 'click',
                submit: 'Ok',
                sUpdateURL: function(value, cellpos){ addToQueue(value,oTable.fnGetPosition( this )); }
            }
        ]        
    });

    $('#ConfigTable').DataTable().columns.adjust().draw();
    return oTable;
}

function init_QueueTable()
{
    // Build queueTable
    //queueTable = $('#queueTable').dataTable(buildTableParameters([], { "sDom": '', "columns" : [], "aoColumnDefs": [] }));
    queueTable = $('#queueTable').dataTable({ 
        "bJQueryUI": true,
        "bProcessing": true,
        "bPaginate": false,
        "sDom": ''
    });
    return queueTable;
}

function addToQueue(queueItem,cellpos) {
   
    // get interface name using the cellpos position values of the selected cell
    interface = $("#ConfigTable tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(0)").text();
    console.log(interface)
    // determine the type of change from the cellpos position values of the selected cell
    if (cellpos[2] == 2) type = 'adminstate';
    if (cellpos[2] == 3) type = 'vlan';
    if (cellpos[2] == 4) type = 'description';

    value = queueItem;
    console.log(value)
    // Adjust the color of the cell, and update the text with the new value
    $("#ConfigTable tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(" + (cellpos[2]-1).toString() + ")").css({"background": "#eeffee","border": "1px solid #dddddd"});
    oTable.fnUpdate( value, cellpos[0], cellpos[2] );       // update text in cell
  
    // add the queue item to the queue array and update the table entries
    queue.push([interface,type,value]);         // add new queue entry to queue array
    $('#queueTable').DataTable().row.add([interface,type,value]).draw();        // update the queuetable with the new entry
    if (queue.length > 0) {
        $('#tabs ul:first li:eq(2) a').text("Queue (" + queue.length.toString() + ")");
    }
    else { $('#tabs ul:first li:eq(2) a').text("Queue"); }
}




