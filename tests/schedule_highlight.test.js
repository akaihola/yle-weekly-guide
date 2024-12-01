import { updateTimeHighlight } from '../templates/schedule.js';

const TEST_HTML = `
  <table>
    <tr>
      <th>Time</th>
      <th data-date="2024-12-01">1.12.</th>
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
    const testDate = new Date('2024-12-01T07:30:00');
    jest.setSystemTime(testDate);

    // Act
    updateTimeHighlight();

    // Assert
    const markedCells = document.querySelectorAll('.current-week');
    expect(markedCells).toHaveLength(4);

    const rows = document.querySelectorAll('tr');
    expect(rows[2]).toHaveClass('current-time');  // 7:00 row
    expect(rows[1]).not.toHaveClass('current-time'); // 6:30 row
    expect(rows[3]).not.toHaveClass('current-time'); // 8:00 row
  });

  it('should not highlight any row when no programs at current time', () => {
    // Arrange
    const testDate = new Date('2024-12-01T09:30:00');
    jest.setSystemTime(testDate);

    // Act
    updateTimeHighlight();

    // Assert
    const highlightedRows = document.querySelectorAll('.current-time');
    expect(highlightedRows).toHaveLength(0);
  });
});
