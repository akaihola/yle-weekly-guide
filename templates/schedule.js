// Import translations
import { getTranslation } from './translations.js';

// Export functions needed for HTML onclick handlers
window.toggleDrawer = toggleDrawer;
window.toggleProgram = toggleProgram;
window.setLanguage = setLanguage;

function setLanguage(lang) {
    localStorage.setItem('preferredLanguage', lang);
    // Retranslate all elements
    document.querySelectorAll('[data-i18n]').forEach((el) => {
        el.textContent = getTranslation(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-title]').forEach((el) => {
        el.title = getTranslation(el.dataset.i18nTitle);
    });
    // Update program actions
    document.querySelectorAll('.program-cell').forEach((cell) => {
        const isHidden = cell.closest('tr').classList.contains('hidden');
        const action = getTranslation(isHidden ? 'show' : 'hide');
        cell.setAttribute('data-action', action);
    });
    // Update hidden count
    updateHiddenCount();
}

function getCurrentTimeInfo() {
    const timezone =
        document.querySelector('table').dataset.timezone || 'Europe/Helsinki';
    const options = { timeZone: timezone };
    const now = new Date();
    const today = now.toLocaleString('sv', options).split(' ')[0];
    const weekday = now.getDay() || 7; // Convert Sunday from 0 to 7
    return { timezone, options, now, today, weekday };
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Set initial action text for all program cells
    document.querySelectorAll('.program-cell').forEach((cell) => {
        const action = getTranslation('hide');
        cell.setAttribute('data-action', action);
    });

    // Only run drawer-related code if elements exist
    const drawer = document.getElementById('drawer');
    if (drawer) {
        const hiddenPrograms = JSON.parse(
            localStorage.getItem('hiddenPrograms') || '[]'
        );
        hiddenPrograms.forEach((program) => toggleProgram(program, false));
        updateHiddenCount();
    }

    // Initial time highlight
    updateTimeHighlight();

    // Update time highlight every minute
    setInterval(updateTimeHighlight, 60000);

    // Scroll to current weekday if no anchor is present
    if (!window.location.hash) {
        const { weekday } = getCurrentTimeInfo();
        const currentHeader = document.getElementById(`iso-weekday-${weekday}`);
        if (currentHeader) {
            currentHeader.scrollIntoView();
        }
    }
});

function toggleDrawer() {
    const drawer = document.getElementById('drawer');
    drawer.classList.toggle('open');
}

function updateHiddenCount() {
    const hiddenList = document.getElementById('hidden-programs');
    const count = hiddenList.children.length;
    const text = `${count} ${getTranslation('programs-hidden')}`;
    document.getElementById('hidden-count').textContent = text;
}

function saveHiddenPrograms() {
    const hiddenList = document.getElementById('hidden-programs');
    const hiddenPrograms = Array.from(hiddenList.children).map(
        (li) => li.querySelector('.program-name').textContent
    );
    localStorage.setItem('hiddenPrograms', JSON.stringify(hiddenPrograms));
    updateHiddenCount();
}

function toggleProgram(programName, save = true) {
    // Update all program cells with correct action text
    document
        .querySelectorAll(`td[data-program='${programName}']`)
        .forEach((cell) => {
            const isHidden = !cell.closest('tr').classList.contains('hidden');
            const action = getTranslation(isHidden ? 'hide' : 'show');
            cell.setAttribute('data-action', action);
        });
    const selector = `tr[data-program='${programName}']`;
    const rows = document.querySelectorAll(selector);
    const isHidden = !rows[0].classList.contains('hidden');
    rows.forEach((row) => row.classList.toggle('hidden'));

    const hiddenList = document.getElementById('hidden-programs');
    const listItem = document.getElementById(`hidden-${programName}`);

    if (isHidden) {
        if (!listItem) {
            const li = document.createElement('li');
            li.id = `hidden-${programName}`;
            li.className = 'toggle-btn';
            li.onclick = () => toggleProgram(programName);
            const showAction = getTranslation('show');
            li.setAttribute('data-action', showAction);
            li.innerHTML = `<span class="program-name">${programName}</span>`;
            hiddenList.appendChild(li);
        }
    } else if (listItem) {
        listItem.remove();
    }

    if (save) {
        saveHiddenPrograms();
    }

    // Update time highlight after visibility changes
    updateTimeHighlight();
}

export function updateTimeHighlight() {
    // Remove existing highlights
    document
        .querySelectorAll('.current-time, .current-week')
        .forEach((el) => el.classList.remove('current-time', 'current-week'));

    const { options, now, today } = getCurrentTimeInfo();

    // Find today's column
    const todayColumn = document.querySelector(`th[data-date="${today}"]`);
    if (!todayColumn) {
        return;
    }

    // Get column index
    const columnIndex = todayColumn
        ? Array.from(todayColumn.parentElement.children).indexOf(todayColumn)
        : -1;

    // Highlight today's column if found
    if (columnIndex >= 0) {
        document.querySelectorAll('tr').forEach((row) => {
            const cell = row.children[columnIndex];
            if (cell?.tagName === 'TD') {
                cell.classList.add('current-week');
            }
        });
    }

    // Get current weekday from getCurrentTimeInfo
    const { weekday } = getCurrentTimeInfo();

    // Find the current or most recent program row
    const timeStr = now.toLocaleTimeString('sv', options);
    const [hours, minutes] = timeStr.split(':').map(Number);
    const currentTime = hours * 60 + minutes;
    let lastMatchingRow = null;

    // Only process rows if we found today's column
    if (todayColumn) {
        const tbody = document.querySelector(
            `tbody[data-iso-weekday="${weekday}"]`
        );
        if (!tbody) return;

        tbody.querySelectorAll('tr').forEach((row) => {
            const timeCell = row.querySelector('td:first-child');
            const programCell = row.children[columnIndex];
            if (timeCell && programCell?.classList.contains('marked')) {
                const [hours, minutes] = timeCell.textContent
                    .trim()
                    .split(':')
                    .map(Number);
                const rowTime = hours * 60 + minutes;
                const nextRow = row.nextElementSibling;

                if (
                    rowTime <= currentTime &&
                    !row.classList.contains('hidden')
                ) {
                    lastMatchingRow = row;
                }
            }
        });

        if (lastMatchingRow) {
            lastMatchingRow.classList.add('current-time');
        }
    }
}
