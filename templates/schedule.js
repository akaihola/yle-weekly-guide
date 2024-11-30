// Load hidden programs from localStorage
function loadHiddenPrograms() {
    const hiddenPrograms = JSON.parse(localStorage.getItem('hiddenPrograms') || '[]');
    hiddenPrograms.forEach(programName => {
        toggleProgram(programName, false);
    });
}

// Save hidden programs to localStorage
function saveHiddenPrograms() {
    const hiddenList = document.getElementById('hidden-programs');
    const hiddenPrograms = Array.from(hiddenList.children).map(li => 
        li.querySelector('.program-name').textContent
    );
    localStorage.setItem('hiddenPrograms', JSON.stringify(hiddenPrograms));
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
document.addEventListener('DOMContentLoaded', loadHiddenPrograms);
