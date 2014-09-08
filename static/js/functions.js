
function buildTableParameters(columnwidths, addparams) {
    var parameters =  { 
        "bJQueryUI": true,
        "bProcessing": true,
        "sPaginationType": "full_numbers",
        "aaSorting": [[ 0, "asc" ]],
        "aLengthMenu": [[25, 50, 75, -1], [25, 50, 75, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [0] }, //set column visibility            
            {"sType": "numeric", "aTargets": [0] }, //define data type for specified columns
            {"iDataSort": 0, "aTargets": [1] } //sort based on a hidden column when another column is clicked            
        ]
    }; 
    var columns = [];
    for (var i=0; i < columnwidths.length; i++) {
        columns.push({ 'width':  columnwidths[i].toString() + "px" })
    }
    parameters.columns = columns;
    for (var key in addparams) {
        parameters[key] = addparams[key];
    }
    return parameters
}