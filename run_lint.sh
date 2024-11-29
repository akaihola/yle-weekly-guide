#!/usr/bin/env bash

errors=0

ruff format -q $@ || errors=$?
ruff check -q --fix --unsafe-fixes --output-format=concise $@ || errors=$?
exit $errors
