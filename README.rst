============================
TV/Radio Schedule Analyzer
============================

Purpose
-------
This script analyzes TV/radio program schedules from YAML files to identify recurring programs
and their regular broadcast times. It helps identify which programs appear regularly on the
same weekday and time slot, making it easier to track regular programming patterns.

Usage
-----
The script requires a directory structure containing YAML schedule files organized as::

    <root_directory>/
        YYYY/           # Year
            MM/         # Month
                DD.yaml  # Day's schedule

Run the script with::

    python3 schedule_analyzer.py -d /path/to/schedule/directory [--format {text|html}] [--debug]

The script will:

1. Look for schedule files covering 5 weeks, prioritizing future weeks and backfilling with past weeks if needed
2. Analyze each program's occurrence patterns
3. Report programs that appear multiple times on the same weekday and time slot
4. Use a 13-minute tolerance for matching time slots

Output Formats
-------------
The script supports two output formats:

Text Format
~~~~~~~~~~
Default text output shows programs by weekday and time::

    Maanantai:
      06:00: Aamun ohjelma
      12:30: Päivän ohjelma (1.12., 8.12., 15.12.)

HTML Format
~~~~~~~~~~
The ``--format html`` option generates an interactive web page that:

You can see a live demo at https://akaihola.github.io/yle-weekly-guide

The page:

- Shows a 5-week schedule grid
- Highlights the current time and week
- Allows hiding/showing programs via a drawer interface
- Marks program occurrences with checkmarks
- Saves hidden program preferences in browser localStorage
- Supports multiple languages (Finnish, Swedish, English)
- Provides responsive layout with proper icon spacing

Implementation Details
--------------------
The script:

- Uses Python's built-in libraries plus ruamel.yaml
- Processes YAML files containing program schedules
- Tracks program occurrences by series name, weekday, and time
- Supports multiple languages (Finnish, Swedish, English)
- Ignores single occurrences to focus on recurring patterns
- Handles timezone information in timestamps
- Generates responsive HTML with JavaScript interactivity
- Provides drawer interface for managing hidden programs
- Persists user preferences in browser localStorage

Requirements
-----------
- Python 3.12 or newer
- ruamel.yaml library
- Node.js and npm (for JavaScript development)
- Web browser (for HTML output)

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~
- ESLint and Prettier for JavaScript linting/formatting
- Stylelint (v15) with stylelint-config-prettier for CSS linting/formatting
- Jest for JavaScript testing
- pytest for Python testing
- uv for Python package management

The YAML files should contain program schedules in the format::

    data:
      <channel_name>:
        programmes:
          - title: <program_title>
            start_time: '2024-11-28T06:30:50+02:00'
            end_time: '2024-11-28T06:50:00+02:00'
            series: <series_name>

Development
----------
The project includes:

- Automated tests (run with ``./run_tests.sh``)
- Code linting and formatting (run with ``./run_lint.sh``)

  - Ruff for Python
  - ESLint and Prettier for JavaScript (with auto-fix)
  - Stylelint for CSS (with auto-fix)

- JavaScript tests using Jest
- Python tests using pytest
- GitHub Actions CI/CD pipeline for:

  - Running tests
  - Linting code
  - Building and deploying to GitHub Pages
