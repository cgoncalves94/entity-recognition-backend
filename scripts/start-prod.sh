#!/usr/bin/env bash

set -e

# Set the default module name
DEFAULT_MODULE_NAME=src.main

# Use the value of MODULE_NAME environment variable if set, otherwise use the default module name
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}

# Set the default variable name
VARIABLE_NAME=${VARIABLE_NAME:-app}

# Set the APP_MODULE environment variable to the combination of MODULE_NAME and VARIABLE_NAME
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

# Set the default Gunicorn configuration file path
DEFAULT_GUNICORN_CONF=/src/gunicorn/gunicorn_conf.py

# Use the value of GUNICORN_CONF environment variable if set, otherwise use the default Gunicorn configuration file path
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}

# Set the default worker class
export WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}

# Start Gunicorn with the specified options
gunicorn --forwarded-allow-ips "*" -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"