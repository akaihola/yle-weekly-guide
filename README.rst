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
                DD.yml  # Day's schedule

Run the script with::

    python3 schedule_analyzer.py -d /path/to/schedule/directory

The script will:

1. Look for schedule files from the current date backwards for at least 4 weeks
2. Analyze each program's occurrence patterns
3. Report programs that appear multiple times on the same weekday and time slot
4. Use a 5-minute tolerance for matching time slots

Implementation Details
--------------------
The script:

- Uses Python's built-in libraries plus PyYAML
- Processes YAML files containing program schedules
- Tracks program occurrences by series name, weekday, and time
- Groups recurring programs by channel
- Formats output in Finnish with proper weekday names
- Ignores single occurrences to focus on recurring patterns
- Handles timezone information in timestamps

Requirements
-----------
- Python 3.12 or newer
- ruamel.yaml library

The YAML files should contain program schedules in the format::

    metadata:
      generated_at: '2024-11-28T20:32:31.889226+00:00'
      ...
    data:
      <channel_name>:
        programmes:
          - title: <program_title>
            start_time: '2024-11-28T06:30:50+02:00'
            end_time: '2024-11-28T06:50:00+02:00'
            series: <series_name>
            ...

Output Format
------------
The script outputs recurring programs in the format::

    Sarja: <series_name>
    Kanava: <channel_name>
      <weekday>:
        HH:MM
        ...

Where weekdays are in Finnish and times are in 24-hour format.
