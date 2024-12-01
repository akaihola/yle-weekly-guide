export function toggleDrawer() {
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

export function updateTimeHighlight() {
    // Remove existing highlights
    document.querySelectorAll('.current-time, .current-week').forEach(el => 
        el.classList.remove('current-time', 'current-week'));
    
    const now = new Date();
    const today = now.toISOString().split('T')[0];  // YYYY-MM-DD format
    
    // Find today's column and its index
    const todayColumn = document.querySelector(`th[data-date="${today}"]`);
    const columnIndex = todayColumn 
        ? Array.from(todayColumn.parentElement.children).indexOf(todayColumn)
        : -1;

    // Highlight today's column if found
    if (columnIndex >= 0) {
        document.querySelectorAll('tr').forEach(row => {
            const cell = row.children[columnIndex];
            if (cell?.tagName === 'TD') {
                cell.classList.add('current-week');
            }
        });
    }

    // Find the current or most recent program row
    const currentTime = now.getHours() * 60 + now.getMinutes();
    let lastMatchingRow = null;

    // Only process rows if we found today's column
    if (todayColumn) {
        document.querySelectorAll('tr').forEach(row => {
            const timeCell = row.querySelector('td:first-child');
            const programCell = row.children[columnIndex];
            if (timeCell && programCell?.classList.contains('marked')) {
                const [hours, minutes] = timeCell.textContent.trim().split(':').map(Number);
                const rowTime = hours * 60 + minutes;
                if (rowTime <= currentTime) {
                    lastMatchingRow = row;
                }
            }
        });

        if (lastMatchingRow) {
            lastMatchingRow.classList.add('current-time');
        }
    }
}

// Initialize when page loads (only in browser)
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
    // Only run drawer-related code if elements exist
    const drawer = document.getElementById('drawer');
    if (drawer) {
        const hiddenPrograms = JSON.parse(localStorage.getItem('hiddenPrograms') || '[]');
        hiddenPrograms.forEach(program => toggleProgram(program, false));
        updateHiddenCount();
    }
    
    // Initial time highlight
    updateTimeHighlight();
    
    // Update time highlight every minute
    setInterval(updateTimeHighlight, 60000);
    });
}
