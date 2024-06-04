function colorRenderer(params) {
    if (params.value !== undefined && params.value !== null) {
        const value = parseFloat(params.value);
        const max = params.colDef.maxValue;
        const min = params.colDef.minValue;

        if (value > 0) {
            const green = Math.floor(255 - (value / max) * 255);
            params.eGui.style.backgroundColor = `rgb(${green}, 255, ${green})`;
        } else {
            const red = Math.floor(255 + (value / min) * 255);
            params.eGui.style.backgroundColor = `rgb(255, ${red}, ${red})`;
        }
    }
    params.eGui.textContent = params.value;
}
