var ResourceTable, ChassisTable, QueueTable, GlobalQueueTable;

$(document).ready(function()
{  
    // Initialize HTML elements for resources page
    if ($('body').hasClass('resources'))
    {
        $('#ResoursesActionSelect').selectmenu(); // init fancy select menu
        $('#ResourcesCommitIndicator').hide();  // hide loading indicator
        $('#ResourceTable').hide(); //hide table during ajax call
        $.get("/resources/getresources", callback_GetResources); //get resources using ajax
        $('#ResourcesActionButton').click(ResourcesActionButtonClick); 
    }
    // Initialize HTML elements for resources router page
    if ($('body').hasClass('resource_router'))
    {
        $('#tabs').tabs();   // Initialize tabs
        $.get("/resources/getresource/" + $('#resourcename').attr('value'), callback_GetResource); // get resource config using Ajax call
        $.get("/router/" + $('#resourcename').attr('value') + "/queue?action=get", callback_GetQueue); // get resource queue using Ajax call
        //$('#QueueActionSelect').selectmenu(); doesnt work yet
        $('#QueueActionButton').click(QueueActionButtonClick); // assign function to click event
    }
    if ($('body').hasClass('global_queue'))
    {
        $('#GlobalQueueActionSelect').selectmenu(); // init fancy select menu
        $('#GlobalQueueTable').hide(); //hide table during ajax call
        $('#GlobalQueueCommitIndicator').hide(); 
        $.get("/resources/getresources", callback_GetGlobalQueue); //get resources using ajax
        $('#GlobalQueueActionButton').click(GlobalQueueButtonClick); 
    }
});

///
/// Resource overview functions
///


// initializes the Resource table
function init_ResourceTable(columnArray, VLANarray) {
    ResourceTable = $('#ResourceTable').dataTable(buildTableParameters([10,10,10,10,10,10], { "data": columnArray  , "aaSorting": [[ 1, "desc" ]]}));
    $('#ResourceTable').DataTable().columns.adjust().draw();
    return ResourceTable;
}

function ResourcesActionButtonClick()
{
    $('#ResourcesCommitIndicator').show(); 
    var values = $('input:checkbox:checked').map(function () {   return this.value;    }).get();
   
    $.ajax({
        type: "POST",
        url: "/resources/status/?action=" + $('#ResoursesActionSelect option:selected').val() ,
        data: JSON.stringify(values),
        dataType: 'json',
        error: function( jqXHR, textStatus, errorThrown ){
            alert("jsoncall failed! reason:" + textStatus);
        },
        success: callback_CommitResourceAction
    });
}

function callback_CommitResourceAction(data,status) 
{
    $.get("/resources/getresources", callback_GetResources); // get resources using ajax
}

function callback_GetResources(data,status) 
{
    var columnArray =[];
    console.log(data);
    if (ResourceTable) ResourceTable.fnDestroy(); // destroy the current Resource table
    for (var i=0; i < Object.keys(data).length; i++) 
    {     
        columnArray[i] = [i, 
            "<a href='/router/" + data[i].name + "'>" + 
            data[i].name + "</a>", data[i].type , data[i].capabilities , data[i].status, "<input type='checkbox' value='" + data[i].id + "'>" ];  
    }  
    $("#ResourceTable").show();  
    $('#ResourcesCommitIndicator').hide(); 
    ResourceTable = init_ResourceTable(columnArray);
};

///
/// Global queue functions
///

function callback_GetGlobalQueue(data,status) {
    var columnArray =[];
    if (GlobalQueueTable) GlobalQueueTable.fnDestroy(); // destroy the current Queue table
    var index = 0;
    for (var i=0; i < Object.keys(data).length; i++) 
    {
       if (data[i].queue[0].length > 0) {    
            for (var q = 0; q < data[i].queue.length; q++)
            {
                columnArray[index] = [index, data[i].name, q, data[i].queue[q], "<input type='checkbox' value='" + data[i].name + "'>" ];
                index ++;
            }         
       }    
    }  
    GlobalQueueTable = $('#GlobalQueueTable').dataTable(buildTableParameters([10,10,10,10,10], { "data": columnArray, "aaSorting": [[ 1, "desc" ]] }));
    $("#GlobalQueueTable").show();
    $('#GlobalQueueCommitIndicator').hide(); 
}

function GlobalQueueButtonClick()
{
    $('#GlobalQueueCommitIndicator').show(); 
     
    // Make array of all resources in the table
    var resources = [];
    jQuery.each( $("#GlobalQueueTable tr"), function( i, val ) { 

        resources.push($("#GlobalQueueTable tr:eq(" + i + ") td:eq(0)").text());
    });
    resources = unique(resources);   //make array unique
    $.ajax({
        type: "POST",
        url: "/queue/" + $('#GlobalQueueActionSelect option:selected').val() ,
        data: JSON.stringify(resources),
        dataType: 'json',
        error: function( jqXHR, textStatus, errorThrown ){
            alert("jsoncall failed! reason:" + textStatus);
        },
        success: $.get("/resources/getresources", callback_GetGlobalQueue)
    });
}


///
/// Resource router functions
///

function init_ChassisTable(columnArray) {
    ChassisTable = $('#ChassisTable').dataTable(buildTableParameters([10,10,200,10,10,10,10], { "data": columnArray })).makeEditable( {
        "aoColumns": [
            null,
            {
                tooltip: 'Click to change description',
                event: 'click',
                submit: 'Ok',
                sUpdateURL: function(value, cellpos){ addToQueue(value,ChassisTable.fnGetPosition( this )); }
            },
            {
                tooltip: 'Click to change IPv4 address',
                event: 'click',
                submit: 'Ok',
                sUpdateURL: function(value, cellpos){ addToQueue(value,ChassisTable.fnGetPosition( this )); }
            },
                        {
                tooltip: 'Click to change IPv6 address',
                event: 'click',
                submit: 'Ok',
                sUpdateURL: function(value, cellpos){ addToQueue(value,ChassisTable.fnGetPosition( this )); }
            },
            {
                tooltip: 'Click to enable / shutdown port',
                type: 'select',
                event: 'click',
                onblur: 'cancel',
                submit: 'Ok',
                data: "{'':'Please select...', 'up':'enabled','down':'shutdown'}",
                sUpdateURL: function(value, settings){  addToQueue(value,ChassisTable.fnGetPosition( this )); }
            },
        ]        
    });
    $('#ChassisTable').DataTable().columns.adjust().draw();
    return ChassisTable;
}

function callback_GetResource(data,status) 
{
    $('#resourcelabel').text(data.name);

    if (data.status != 'ACTIVE') {
        alert("resource is not ACTIVE!");
        $('#tabs').tabs( "option", "disabled", [0, 1, 2] );
        $('#tabs').tabs( "option", "active", 3 );  
        return 0;
    };
    $.get("/router/" + $('#resourcename').attr('value') + "/getinterfaces", callback_GetInterfaces);
};

function callback_GetInterfaces(data,status)
{
    var columnArray =[];
    if (ChassisTable) ChassisTable.fnDestroy(); // destroy the current Resource table
    for (var i=0; i < Object.keys(data).length; i++) 
    {     
        columnArray[i] = [i, data[i].name , data[i].description, data[i].ip , data[i].ip, data[i].state, "<input type='checkbox' value='" + data[i].name + "'>" ];

    }  
    $("#ChassisTable").show();
    $('#ChassisCommitIndicator').hide(); 
    ChassisTable = init_ChassisTable(columnArray);   
}

function callback_GetQueue(data,status) {
    var columnArray =[];
   
    if (QueueTable) QueueTable.fnDestroy(); // destroy the current Queue table
    $('#tabs ul:first li:eq(1) a').text("Queue");
    if (data[0].length > 4) {
        $('#tabs ul:first li:eq(1) a').text("Queue (" + Object.keys(data).length.toString() + ")");
        for (var i=0; i < Object.keys(data).length; i++) 
        {    
            columnArray[i] = [i, $('#resourcename').attr('value'), i, data[i], "<input type='checkbox' value='" + data[i] + "'>" ];
        }  
    }    
    
    QueueTable = init_QueueTable(columnArray); 
    $("#QueueTable").show();
    $('#QueueCommitIndicator').hide(); 
}

function init_QueueTable(columnArray) {
    QueueTable = $('#QueueTable').dataTable(buildTableParameters([10,10,10,10,10], { "data": columnArray }));
    $('#QueueTable').DataTable().columns.adjust().draw();
    return QueueTable;
}

function QueueActionButtonClick()
{
    $('#QueueCommitIndicator').show(); 
    var values = $('input:checkbox:checked').map(function () {   return this.value;    }).get();
    console.log(values)
    $.ajax({
        type: "POST",
        url: "/router/" + $('#resourcename').attr('value') + "/queue?action=" + $('#QueueActionSelect option:selected').val() ,
        data: JSON.stringify(values),
        dataType: 'json',
        error: function( jqXHR, textStatus, errorThrown ){
            alert("jsoncall failed! reason:" + textStatus);
        },
        success: callback_CommitQueueAction
    });
}

function addToQueue(queueItem,cellpos) {
   
    // get interface name using the cellpos position values of the selected cell
    interface = $("#ChassisTable tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(0)").text();
   
    // determine the type of change from the cellpos position values of the selected cell
    if (cellpos[2] == 2) type = 'description';
    if (cellpos[2] == 3) type = 'ipv4address';
    if (cellpos[2] == 4) type = 'ipv6address';
    if (cellpos[2] == 5) type = 'status';

    value = queueItem;
    // Adjust the color of the cell, and update the text with the new value
    $("#ChassisTable tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(" + (cellpos[2]-1).toString() + ")").css({"background": "#eeffee","border": "1px solid #dddddd"});
    ChassisTable.fnUpdate( value, cellpos[0], cellpos[2] );       // update text in cell

    $.get("/router/" + $('#resourcename').attr('value') + "/queue?action=add&interface=" + interface + "&type=" + type + "&value=" + value, callback_AddToQueue);
    return "ok"
}

function callback_AddToQueue(data,status) {
    $.get("/router/" + $('#resourcename').attr('value') + "/queue?action=get", callback_GetQueue);
}

function callback_CommitQueueAction(data,status) 
{
    $.get("/router/" + $('#resourcename').attr('value') + "/queue?action=get", callback_GetQueue);
    $.get("/resources/getresource/" + $('#resourcename').attr('value'), callback_GetResource);
}



