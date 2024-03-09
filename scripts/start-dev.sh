#!/usr/bin/env bash

# Exit immediately if any command exits with a non-zero status
set -e

# Default module name
DEFAULT_MODULE_NAME=src.main

# Use the value of MODULE_NAME environment variable if set, otherwise use the default module name
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}

# Use the value of VARIABLE_NAME environment variable if set, otherwise use 'app' as the variable name
VARIABLE_NAME=${VARIABLE_NAME:-app}

# Set the APP_MODULE environment variable to the combination of MODULE_NAME and VARIABLE_NAME
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

# Set the host, port, log level, and log config variables if they are not already set
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}
LOG_CONFIG=${LOG_CONFIG:-/src/logging.ini}

# Start Uvicorn with live reload, using the specified host, port, log config, and app module
exec uvicorn --reload --proxy-headers --host $HOST --port $PORT --log-config $LOG_CONFIG "$APP_MODULE"