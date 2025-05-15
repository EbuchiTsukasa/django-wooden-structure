const renderUnit = (unit, container) => {
    // 1つ描画
    const div = document.createElement('div');
    div.className = 'unit';
    div.innerHTML = `<div>${unit.name}</div>`;
    container.appendChild(div);

    // 子を段階的に描画
    if (unit.children && unit.children.length > 0) {
        const childrenDiv = document.createElement('div');
        childrenDiv.className = 'children';
        div.appendChild(childrenDiv);

        // 1つずつ（非同期で少しずつ描画）
        let i = 0;
        function drawNext() {
            if (i >= unit.children.length) return;
            renderUnit(unit.children[i], childrenDiv);
            i++;
            setTimeout(drawNext, 10);  // 10msごとに1つ描画
        }
        drawNext();
    }
}

window.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('tree-root');
    renderUnit(rootUnit, container);
});