function toggleDrawer() {
    const drawer = document.getElementById('drawer');
    drawer.classList.toggle('open');
}

function updateHiddenCount() {
    const hiddenList = document.getElementById('hidden-programs');
    const count = hiddenList.children.length;
    document.getElementById('hidden-count').textContent = count;
}

function saveHiddenPrograms() {
    const hiddenList = document.getElementById('hidden-programs');
    const hiddenPrograms = Array.from(hiddenList.children).map(li => 
        li.querySelector('.program-name').textContent
    );
    localStorage.setItem('hiddenPrograms', JSON.stringify(hiddenPrograms));
    updateHiddenCount();
}

function toggleProgram(programName, save = true) {
    const selector = `tr[data-program='${programName}']`;
    const rows = document.querySelectorAll(selector);
    const isHidden = !rows[0].classList.contains('hidden');
    rows.forEach(row => row.classList.toggle('hidden'));

    const hiddenList = document.getElementById('hidden-programs');
    const listItem = document.getElementById(`hidden-${programName}`);

    if (isHidden) {
        if (!listItem) {
            const li = document.createElement('li');
            li.id = `hidden-${programName}`;
            li.className = 'toggle-btn';
            li.onclick = () => toggleProgram(programName);
            li.innerHTML = `<span class="program-name">${programName}</span>`;
            hiddenList.appendChild(li);
        }
    } else if (listItem) {
        listItem.remove();
    }

    if (save) {
        saveHiddenPrograms();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    const hiddenPrograms = JSON.parse(localStorage.getItem('hiddenPrograms') || '[]');
    hiddenPrograms.forEach(program => toggleProgram(program, false));
    updateHiddenCount();
});
