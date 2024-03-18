document.addEventListener("DOMContentLoaded", function () {
    const fontSelect = document.getElementById('font');
    const colorSelect = document.getElementById('color');

    const colorOptionsMap = new Map([
        ['Blue', 'Blue'],
        ['Orange-1', 'Orange 1'],
        ['Orange-2', 'Orange 2'],
        ['Yellow', 'Yellow']
    ]);

    const colorMap = new Map([
        ['1', new Set(['Blue', 'Orange-1', 'Orange-2'])],
        ['2', new Set(['Blue', 'Orange-1', 'Orange-2'])],
        ['3', new Set(['Blue', 'Orange-1'])],
        ['4', new Set(['Blue', 'Orange-1', 'Yellow'])],
        ['5', new Set(['Orange-1'])]
    ]);

    if (fontSelect) {
        fontSelect.addEventListener('change', updateColorOptions);
    }

    function updateColorOptions() {
        const fontValue = fontSelect.value;
        const colors = colorMap.get(fontValue) || new Set();
        const colorOptions = [...colors].map(color => {
            const value = color.toLowerCase();
            const text = colorOptionsMap.get(color);
            return `<option value="${value}">${text}</option>`;
        }).join('');

        colorSelect.innerHTML = colorOptions;
    }
});
