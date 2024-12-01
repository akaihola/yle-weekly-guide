import { updateTimeHighlight } from '../templates/schedule.js';

/*
Test HTML structure represents a schedule table:

SATURDAY SECTION:
Time   | 30.11. | 7.12. | Program
-------|--------|-------|------------------------
21:00  |   ✓    |       | Yle Uutiset
21:05  |   ✓    |   ✓   | Uutispodcast
21:35  |   ✓    |   ✓   | Mielimaisema
22:35  |   ✓    |   ✓   | Keinuva talo
23:40  |        |   ✓   | Syventävää klassista

SUNDAY SECTION:
Time   | 1.12.  | 8.12. | Program
-------|--------|-------|------------------------
21:00  |   ✓    |   ✓   | Yle Uutiset
21:04  |   ✓    |   ✓   | Uutispodcast
21:31  |   ✓    |   ✓   | Elävä historia
22:19  |   ✓    |   ✓   | Klasariparatiisi
23:20  |   ✓    |   ✓   | Romano mirits
23:40  |   ✓    |   ✓   | Syventävää klassista

✓ indicates program is scheduled for that date
*/

const TEST_HTML = `
<table>
    <thead>
        <tr>
            <th>la</th>
            <th data-date="2024-11-30">30.11.</th>
            <th data-date="2024-12-07">7.12.</th>
            <th>Ohjelma</th>
        </tr>
    </thead>
    <tbody data-iso-weekday="6">
        <tr data-program="Yle Uutiset">
            <td>21:00</td>
            <td class="marked">✓</td>
            <td class=""></td>
            <td class="program-cell">Yle Uutiset</td>
        </tr>
        <tr data-program="Uutispodcast">
            <td>21:05</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Uutispodcast</td>
        </tr>
        <tr data-program="Mielimaisema">
            <td>21:35</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Mielimaisema</td>
        </tr>
        <tr data-program="Keinuva talo - Mika Kauhanen">
            <td>22:35</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Keinuva talo - Mika Kauhanen</td>
        </tr>
        <tr data-program="Syventävää klassista">
            <td>23:40</td>
            <td></td>
            <td class="marked">✓</td>
            <td class="program-cell">Syventävää klassista</td>
        </tr>
    </tbody>
    <thead>
        <tr>
            <th>su</th>
            <th data-date="2024-12-01">1.12.</th>
            <th data-date="2024-12-08">8.12.</th>
            <th>Ohjelma</th>
        </tr>
    </thead>
    <tbody data-iso-weekday="7">
        <tr data-program="Yle Uutiset">
            <td>21:00</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Yle Uutiset</td>
        </tr>
        <tr data-program="Uutispodcast">
            <td>21:04</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Uutispodcast</td>
        </tr>
        <tr data-program="Elävä historia">
            <td>21:31</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Elävä historia</td>
        </tr>
        <tr data-program="Klasariparatiisi - Eva Tigerstedt">
            <td>22:19</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Klasariparatiisi - Eva Tigerstedt</td>
        </tr>
        <tr data-program="Romano mirits">
            <td>23:20</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Romano mirits</td>
        </tr>
        <tr data-program="Syventävää klassista">
            <td>23:40</td>
            <td class="marked">✓</td>
            <td class="marked">✓</td>
            <td class="program-cell">Syventävää klassista</td>
        </tr>
    </tbody>
</table>`;

describe('Schedule highlighting', () => {
    beforeEach(() => {
        document.body.innerHTML = TEST_HTML;
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
        document.body.innerHTML = '';
    });

    it('should highlight correct column and row at 23:00', () => {
        // Arrange
        const testDate = new Date('2024-11-30T23:00:00'); // Saturday
        jest.setSystemTime(testDate);

        // Act
        updateTimeHighlight();

        // Assert
        const markedCells = document.querySelectorAll('.current-week');
        expect(markedCells).toHaveLength(11);
        markedCells.forEach((cell) => {
            expect(cell.cellIndex).toBe(1); // Second column 30.11.-1.12.
        });

        const highlightedRows = document.querySelectorAll('tr.current-time');
        expect(highlightedRows).toHaveLength(1);
        const timeCell = highlightedRows[0].querySelector('td:first-child');
        expect(timeCell.textContent).toBe('22:35');
    });

    it('should highlight previous program when no programs at current time', () => {
        // Arrange
        const testDate = new Date('2024-11-30T23:45:00'); // Saturday
        jest.setSystemTime(testDate);

        // Act
        updateTimeHighlight();

        // Assert
        const highlightedRows = document.querySelectorAll('tr.current-time');
        expect(highlightedRows).toHaveLength(1);
        const timeCell = highlightedRows[0].querySelector('td:first-child');
        expect(timeCell.textContent).toBe('22:35');
    });

    it('should not highlight any column when viewing on a week outside the range', () => {
        // Arrange
        const testDate = new Date('2024-11-24T22:20:00'); // Sunday
        jest.setSystemTime(testDate);

        // Act
        updateTimeHighlight();

        // Assert
        const markedCells = document.querySelectorAll('.current-week');
        expect(markedCells).toHaveLength(0);

        const highlightedRows = document.querySelectorAll('.current-time');
        expect(highlightedRows).toHaveLength(0);
    });

    it('should highlight Sunday column and correct program row at 21:10', () => {
        // Arrange
        const testDate = new Date('2024-12-08T21:10:00'); // Sunday
        jest.setSystemTime(testDate);

        // Act
        updateTimeHighlight();

        // Assert
        // Check that Sunday column is highlighted
        const sundayCells = document.querySelectorAll('tbody td:nth-child(3)');
        sundayCells.forEach((cell) => {
            expect(cell).toHaveClass('current-week');
        });

        const highlightedRows = document.querySelectorAll('tr.current-time');
        expect(highlightedRows).toHaveLength(1);
        const timeCell = highlightedRows[0].querySelector('td:first-child');
        expect(timeCell.textContent).toBe('21:04');
    });
});
