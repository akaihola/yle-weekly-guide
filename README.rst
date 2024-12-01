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

- Shows a 5-week schedule grid
- Highlights the current time and week
- Allows hiding/showing programs
- Marks program occurrences with checkmarks
- Saves hidden program preferences locally

Implementation Details
--------------------
The script:

- Uses Python's built-in libraries plus ruamel.yaml and Babel
- Processes YAML files containing program schedules
- Tracks program occurrences by series name, weekday, and time
- Uses system locale for weekday names
- Ignores single occurrences to focus on recurring patterns
- Handles timezone information in timestamps
- Generates responsive HTML with JavaScript interactivity

Requirements
-----------
- Python 3.12 or newer
- ruamel.yaml library
- Babel library
- Web browser (for HTML output)

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
- Code linting (run with ``./run_lint.sh``)
- JavaScript tests using Jest
- GitHub Actions CI/CD pipeline
