#!/usr/bin/env bash

errors=0
py_files=()

# Filter for .py files
for file in "$@"; do
    if [[ $file == *.py ]]; then
        py_files+=("$file")
    fi
done

if [ ${#py_files[@]} -gt 0 ]; then
    ruff format -q "${py_files[@]}" || errors=$?
    ruff check -q --fix --unsafe-fixes --output-format=concise "${py_files[@]}" || errors=$?
fi

exit $errors
