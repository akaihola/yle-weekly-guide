#!/usr/bin/env bash

errors=0
py_files=()
yaml_files=()
js_files=()

# Filter for .py and .yml/.yaml files
for file in "$@"; do
    if [[ $file == *.py ]]; then
        py_files+=("$file")
    elif [[ $file == *.yml ]] || [[ $file == *.yaml ]]; then
        yaml_files+=("$file")
    elif [[ $file == *.js ]]; then
        js_files+=("$file")
    fi
done

if [ ${#py_files[@]} -gt 0 ]; then
    ruff format -q "${py_files[@]}" || errors=$?
    ruff check -q --fix --unsafe-fixes --output-format=concise "${py_files[@]}" || errors=$?
fi

if [ ${#yaml_files[@]} -gt 0 ]; then
    uvx yamllint "${yaml_files[@]}" || errors=$?
fi

if [ ${#js_files[@]} -gt 0 ]; then
    npm run lint:js -- "${js_files[@]}" || errors=$?
    npm run format:js -- "${js_files[@]}" || errors=$?
fi

# Check for CSS files
css_files=()
for file in "$@"; do
    if [[ $file == *.css ]]; then
        css_files+=("$file")
    fi
done

if [ ${#css_files[@]} -gt 0 ]; then
    npm run lint:css -- "${css_files[@]}" || errors=$?
    npm run format:css -- "${css_files[@]}" || errors=$?
fi

exit $errors
