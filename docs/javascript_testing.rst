JavaScript Testing Guide
========================

This document describes how to run and write JavaScript tests for the schedule application.

Running Tests in Browser
------------------------

1. Open ``tests/test_runner.html`` in a web browser
2. Test results will be displayed on the page
3. Check browser console (F12) for detailed output

Writing Tests
-------------

Tests use a Jest-like syntax with these available functions:

- ``describe(name, fn)`` - Groups related tests
- ``test(name, fn)`` - Defines a test case
- ``beforeEach(fn)`` - Runs before each test
- ``expect(value)`` - Creates assertions

Example::

    describe('My Feature', () => {
        test('should work correctly', () => {
            expect(2 + 2).toBe(4);
        });
    });

Available Assertions
--------------------

- ``expect(value).toBe(other)`` - Strict equality
- ``expect(value).toEqual(other)`` - Deep equality

Mock Objects
------------

The test framework includes mock DOM elements and document object for testing
UI interactions without a real browser environment.

See ``tests/test_schedule_highlight.js`` for examples of using mocks.
