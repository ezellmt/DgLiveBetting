window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        sgCellStyle: function(params) {
            const value = params.value;
            if (value > 2) {
                return {'backgroundColor': '#d4edda', 'color': '#155724'};  // Green for high values
            } else if (value > 0) {
                return {'backgroundColor': '#fff3cd', 'color': '#856404'};  // Yellow for moderate values
            } else {
                return {'backgroundColor': '#f8d7da', 'color': '#721c24'};  // Red for low values
            }
        }
    }
});
