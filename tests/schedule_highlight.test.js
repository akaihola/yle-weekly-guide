import { updateTimeHighlight } from '../templates/schedule.js';

const TEST_HTML = `
  <table>
    <tr>
      <th>Time</th>
      <th data-date="2024-11-25" data-weekday="1">25.11.</th> <!-- Monday -->
    </tr>
    <tr><td>06:30</td><td class="marked"></td></tr>
    <tr><td>07:00</td><td class="marked"></td></tr>
    <tr><td>08:00</td><td class="marked"></td></tr>
    <tr><td>09:00</td><td></td></tr>
  </table>
`;

describe('Schedule highlighting', () => {
  beforeEach(() => {
    document.body.innerHTML = TEST_HTML;
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
    document.body.innerHTML = '';
  });

  it('should highlight correct column and row at 7:30', () => {
    // Arrange
    const testDate = new Date('2024-11-25T07:30:00'); // Monday
    jest.setSystemTime(testDate);

    // Act
    updateTimeHighlight();

    // Assert
    const markedCells = document.querySelectorAll('.current-week');
    expect(markedCells).toHaveLength(4);
    markedCells.forEach(cell => {
      expect(cell.cellIndex).toBe(1);  // Second column (Monday)
    });

    const rows = document.querySelectorAll('tr');
    expect(rows[2]).toHaveClass('current-time');  // 7:00 row
    expect(rows[1]).not.toHaveClass('current-time'); // 6:30 row
    expect(rows[3]).not.toHaveClass('current-time'); // 8:00 row
  });

  it('should highlight previous program when no programs at current time', () => {
    // Arrange
    const testDate = new Date('2024-11-25T09:30:00');  // Monday
    jest.setSystemTime(testDate);

    // Act
    updateTimeHighlight();

    // Assert
    const highlightedRows = document.querySelectorAll('.current-time');
    expect(highlightedRows).toHaveLength(1);
    
    const rows = document.querySelectorAll('tr');
    expect(rows[3]).toHaveClass('current-time');  // 8:00 row should be highlighted
  });

  it('should not highlight any column when viewing on a week outside the range', () => {
    // Arrange
    const testDate = new Date('2024-11-24T22:20:00');  // Sunday
    jest.setSystemTime(testDate);

    // Act
    updateTimeHighlight();

    // Assert
    const markedCells = document.querySelectorAll('.current-week');
    expect(markedCells).toHaveLength(0);
    
    const highlightedRows = document.querySelectorAll('.current-time');
    expect(highlightedRows).toHaveLength(0);
  });

  it('should highlight column when viewing on Monday of the week', () => {
    // Arrange
    const testDate = new Date('2024-11-25T22:20:00');  // Monday
    jest.setSystemTime(testDate);

    // Act
    updateTimeHighlight();

    // Assert
    const markedCells = document.querySelectorAll('.current-week');
    expect(markedCells).toHaveLength(4); // Should highlight Saturday's column
  });
});
