var ResourceTable, ChassisTable, QueueTable, GlobalQueueTable, NetworkTable;
var dialog;
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
        $.get("/router/" + $('#resourcename').attr('value') + "/getcontext", callback_GetContext); // get resource queue using Ajax call
        $.get("/router/" + $('#resourcename').attr('value') + "/queue?action=get", callback_GetQueue); // get resource queue using Ajax call
        $( "#port_aggr_dialog" ).hide();
        $( "#port_show_aggr_dialog" ).hide();
        //$('#QueueActionSelect').selectmenu(); doesnt work yet
        $('#ChassisActionButton').click(ChassisActionButtonClick);
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
    if ($('body').hasClass('networks'))
    {     
        $.get("/networks/getnetworks" , callback_GetNetworks); // get Network info using Ajax call
        $('#NetworksActionButton').click(ChassisActionButtonClick);
    }
    if ($('body').hasClass('topology'))
    {     
        $('#TopologyIndicator').hide();
        $('#TopologyActionButton').click(TopologyActionButtonClick);
        $.get("/topology/net1/gettopology" , callback_GetTopology); // get Network info using Ajax call
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

    if (ResourceTable) ResourceTable.fnDestroy(); // destroy the current Resource table
    for (var i=0; i < Object.keys(data).length; i++) 
    {   
        if (data[i].type == "router")
        {
            if (data[i].capabilities != null) 
            {
                var capabilities = data[i].capabilities.capability;
            }
            else 
            {
                var capabilities = "Unknown";
            }
            columnArray[i] = [i, 
                "<a href='/router/" + data[i].name + "'>" + 
                data[i].name + "</a>", data[i].type , capabilities, data[i].state, "<input type='checkbox' value='" + data[i].resourceId + "'>" ];  
        }
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
            if (data[i].type == "router")
            {  
                for (var q = 0; q < data[i].queue.length; q++)
                {
                    columnArray[index] = [index, data[i].name, q, data[i].queue[q], "<input type='checkbox' value='" + data[i].name + "'>" ];
                    index ++;
                }
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
    ChassisTable = $('#ChassisTable').dataTable(buildTableParameters([10,10,200,10,10,10,10], { "data": columnArray, "placeholder" : "..." })).makeEditable( {
        "placeholder" : "...", 
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
    $('td', ChassisTable.fnGetNodes()).editable(function(value, settings) {
    return(value);
    }, {
    placeholder : '&amp;nbsp; '
}); 
    $('#ChassisTable').DataTable().columns.adjust().draw();
    return ChassisTable;
}

function callback_GetResource(data,status) 
{
    $('#resourcelabel').text(data.name);

    if (data.state != 'ACTIVE') {
        alert("resource is not ACTIVE!");
        $('#tabs').tabs( "option", "disabled", [0, 1, 2] );
        $('#tabs').tabs( "option", "active", 3 );  
        return 0;
    };
    $.get("/router/" + $('#resourcename').attr('value') + "/getinterfaces", callback_GetInterfaces);
};

function  callback_GetContext(data,status) 
{
    for (var propt in data) {      
        $('#' + propt.replace(".", "_") ).text(data[propt]);
    }
}
function callback_GetInterfaces(data,status)
{
    var columnArray =[];


    if (ChassisTable) ChassisTable.fnDestroy(); // destroy the current Resource table
    for (var i=0; i < Object.keys(data).length; i++) 
    {     
        // parse IP addresses
        var ipv4 ="";
        var ipv6 ="";
        if (typeof(data[i].ipAddress) == 'object')  // check if there are multiple ip addresses in data[i].ipAddress
        {
        for (var ip=0; ip <data[i].ipAddress.length; ip++)
            {
                if (data[i].ipAddress[ip].indexOf(".") != -1) { ipv4 = ipv4 + data[i].ipAddress[ip] + " "; }
                if (data[i].ipAddress[ip].indexOf(":") != -1) { ipv6 = ipv6 + data[i].ipAddress[ip] + " "; }    
            }
        }
        else 
        {
            if (data[i].ipAddress.indexOf(".") != -1) { ipv4 = data[i].ipAddress}
            if (data[i].ipAddress.indexOf(":") != -1) { ipv6 = data[i].ipAddress} 
        }
        name = data[i].name;
        if (data[i].isAggr == true) 
        {
            name = '<a href="javascript:;" onclick="getAggregate(\'' +data[i].name + '\');">' + data[i].name + "</a>";
            console.log(name)
        }
     
        columnArray[i] = [i, name , data[i].description, ipv4 , ipv6, data[i].state, "<input type='checkbox' value='" + data[i].name + "'>" ];
    }; 
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

function ChassisActionButtonClick()
{
    
    dialog = $( "#port_aggr_dialog" ).dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
            "Create the aggregate": function() { alert ('add aggr1') },
            Cancel: function() {
            dialog.dialog( "close" );
        }
        },
        close: function() {
            form[ 0 ].reset();
            allFields.removeClass( "ui-state-error" );
        }
    });
    dialog.dialog( "open" );
}

function getAggregate(aggr)
{
    aggr = aggr.replace(".0","");
    $//.get("/router/" + $('#resourcename').attr('value') + "/getinterfaces", callback_GetAggregate);
    $.ajax({
        type: "GET",
        url: "/router/" + $('#resourcename').attr('value') + "/getaggr/" + aggr,
        error: callback_GetAggregate,
        success: callback_GetAggregate
    });
}

function callback_GetAggregate(data)
{
    console.log(data);
    dialog = $( "#port_show_aggr_dialog" ).dialog({
        autoOpen: false,
        height: 400,
        width: 350,
        modal: true,
        buttons: {
            Cancel: function() {
            dialog.dialog( "close" );
        }
        },
        close: function() {
            allFields.removeClass( "ui-state-error" );
        }
    });
    dialog.dialog( "open" );

    $('#aggr_name').val(data.id);
    var interfaces ="";
    for (var i=0; i < Object.keys(data.interfaces.interface).length; i++) {
        $('#aggr_interfaces').append($("<option></option>") .attr("value",data.interfaces.interface[i]) .text(data.interfaces.interface[i]));  
        interfaces = interfaces +  data.interfaces.interface[i] + " ";
    }
    $('#aggr_link_speed').val("1g");
  
    options = "";
    //for (var i=0; i < Object.keys(data.aggregationOptions.entry).length; i++) {
        options = options + data.aggregationOptions.entry.key + " " + data.aggregationOptions.entry.value + " ";
    //};
    $('#aggr_options').val(options);
         
        
        
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

///////////////////////
/// Networks overview functions
///////////////////////

function callback_GetNetworks(data,status) 
{
    var columnArray =[];
    if (NetworkTable) NetworkTable.fnDestroy(); // destroy the current Resource table
    
    var i=0;
    for (key in data) 
    {   
        console.log(key,data[key]);
        columnArray[i] = [i,data[key].domainName, data[key].description, data[key].vlanid, data[key].resources, " ", " "," "];
        i++;
        //   "<a href='/router/" + data[i].name + "'>" + 
        //    data[i].name + "</a>", data[i].type , capabilities, data[i].state, "<input type='checkbox' value='" + data[i].resourceId + "'>" ];  
    }
 
    $("#NetworkTable").show();  
    $('#NetworksCommitIndicator').hide(); 
    NetworkTable = init_NetworkTable(columnArray);
    
};

function init_NetworkTable(columnArray) {
    NetworkTable = $('#NetworkTable').dataTable(buildTableParameters([150,150,10,10,10,10,10,10], { "data": columnArray }));
    $('#NetworkTable').DataTable().columns.adjust().draw();
    return NetworkTable;
}

function callback_GetTopology(data,status) 
{
    //if there is data, init canvas, else nothing
    if (data.devices != null ) 
    {
        if (Object.keys(data.devices.device).length > 0) 
        {
            init_Canvas(data);
        }
    }   
};

function buildCircle(x,y,radius)
{
      var circle = new Kinetic.Circle({
          x: x,
          y: y,
          radius: radius,
          stroke: '#666',
          fill: '#ddd',
          strokeWidth: 2,
          draggable: true
        }); 
      return circle;
}

function buildSwitchShape(x,y, description) 
{
    var layer = new Kinetic.Layer();
    var imageObj = new Image(120,75);
    imageObj.src = '/img/switch.png';
    var image = new Kinetic.Image({
        name: description,
        x: x,
        y: y,
        image: imageObj,
        width: 120,
        height: 75
    });
    var label = new Kinetic.Text({ 
        text: description,
        x: x, 
        y: y-20,
        fontSize: 18,
        fontFamily: 'Calibri',
        fill: 'black'
    });
   var group = new Kinetic.Group();
    group.add(image);
    group.add(label);
 
    
    return group;
}

function buildAnchors(x,y, radius, anchors_per_side) 
{
    var layer = new Kinetic.Layer();
    var workable_radius = radius - 4;
    //Horizontal Anchors
    for (var i = 0; i < anchors_per_side ; i++ ) 
    {
        var circle = buildCircle(x - workable_radius +( (workable_radius  / anchors_per_side) * i *2), y - workable_radius, 2);
        layer.add(circle);
        var circle = buildCircle(x - workable_radius +( (workable_radius  / anchors_per_side) * i *2), y + workable_radius, 2);
        layer.add(circle);
    };
    // Vertical Anchors
    for (var i = 0; i < anchors_per_side ; i++ ) 
    {
        if ((i != 0) & (i != anchors_per_side)) {
            var circle = buildCircle(x - workable_radius , y - workable_radius + ((workable_radius  / anchors_per_side) * i *2), 2);
            layer.add(circle);
           var circle = buildCircle(x + workable_radius , y - workable_radius + ((workable_radius  / anchors_per_side) * i *2), 2);
             layer.add(circle);
        }
    };
    return layer;
}

function TopologyActionButtonClick()
{
    $('#TopologyIndicator').show(); 
    $.ajax({
        type: "GET",
        url: "/topology/net1/buildtopology",
        error: callback_BuildTopology,
        success: callback_BuildTopology
    });
}

function callback_BuildTopology(data,status) 
{
    $('#TopologyIndicator').hide(); 
    
    $.get("/topology/net1/gettopology" , callback_GetTopology); // get Network info using Ajax call
}

function get_resourcename_from_resourceid(resourceId,data)
{   
    for (var i=0; i < Object.keys(data.resources).length; i++ )
        if (data.resources[i].resourceId == resourceId) return data.resources[i].name;
}
function init_Canvas(data) 
{
    // Create new Canvas
    var stage = new Kinetic.Stage({
        container: 'container',
        width: 800,
        height: 400,
        draggable: false
    });
    var layer = new Kinetic.Layer();
    // Text information
    var text = new Kinetic.Text({
        x: 10,
        y: 10,
        fontFamily: 'Calibri',
        fontSize: 18,
        text: '',
        fill: 'black'
      });

    layer.add(text);
    var switchInfo = [];
    var xindex=100;
    // Read all the devices from the topology info and create images
    for (var i=0; i < Object.keys(data.devices.device).length; i++) 
    {
        resourcename  = get_resourcename_from_resourceid(data.devices.device[i].resourceID,data)
        switchShape = buildSwitchShape(xindex,100, resourcename);
        switchInfo[i] = ({ x: xindex, y:100 , name: resourcename, deviceid : data.devices.device[i].id});
        layer.add(switchShape);
        switchShape.on('click', function(e) { location.href="/router/" + e.target.name(); });
        switchShape.on('mouseover', function() {  document.body.style.cursor = 'pointer'; });
        switchShape.on('mouseout', function() {  document.body.style.cursor = 'default'; });
        xindex=xindex+300;
    }
  
    // Read all links from the topology info and create lines
    for (var i=0; i < Object.keys(data.links.link).length; i++) {

        from = getSwitchInfo_from_deviceid(data.links.link[i].from.deviceId, switchInfo);
        to = getSwitchInfo_from_deviceid(data.links.link[i].to.deviceId, switchInfo);
        description = from.name + ": " + data.links.link[i].from.id + " -> " + to.name + ": " + data.links.link[i].to.id;
        var line = new Kinetic.Line({
            dash: [10,0,10,0],
            points: [from.x+60, from.y+38+(i*5), to.x+60, to.y+38+(i*5)],
            name: description,
            stroke: 'black',
            strokeWidth: 3,
            lineCap: 'round',
            lineJoin: 'round'
        });  
        
        layer.add(line);
        line.on('mouseover', function() { this.stroke('orange'); this.dashEnabled(true); text.setText(this.name()); layer.draw(); });
        line.on('mouseout', function() { this.stroke('black');  text.setText(""); layer.draw(); });
        line.moveToBottom();
        layer.draw();
    }

    stage.add(layer);
}

function getSwitchInfo_from_deviceid(deviceid, switchInfo)
{
    for (var i=0 ; i< switchInfo.length; i ++) 
        if (switchInfo[i].deviceid == deviceid) return switchInfo[i];
}

