import multiprocessing
import os

# based on https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker


# Get the host and port from environment variables, default to "0.0.0.0" and "8000" respectively
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8000")

# Get the bind address from the environment variable, if not set, use the host and port
bind_env = os.getenv("BIND", None)
use_bind = bind_env if bind_env else f"{host}:{port}"

# Get the number of workers per core from the environment variable, default to 1
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
workers_per_core = int(workers_per_core_str)

# Get the maximum number of workers from the environment variable, if not set, use the default web concurrency
max_workers_str = os.getenv("MAX_WORKERS")
default_web_concurrency = workers_per_core * multiprocessing.cpu_count() + 1

# Get the web concurrency from the environment variable, if not set, use the default web concurrency
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)
    if max_workers_str:
        use_max_workers = int(max_workers_str)
        web_concurrency = min(web_concurrency, use_max_workers)

# Get the graceful timeout, timeout, and keep alive values from environment variables, default to 120, 120, and 5 respectively
graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "120")
timeout_str = os.getenv("TIMEOUT", "120")
keepalive_str = os.getenv("KEEP_ALIVE", "5")
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)

# Get the log level from the environment variable, default to "info"
use_loglevel = os.getenv("LOG_LEVEL", "info")
loglevel = use_loglevel

# Set the number of workers to the web concurrency
workers = web_concurrency

# Set the bind address to the use_bind value
bind = use_bind

# Set the worker temporary directory to "/dev/shm"
worker_tmp_dir = "/dev/shm"

# Set the log configuration file to "/src/logging_production.ini"
logconfig = os.getenv("LOG_CONFIG", "/src/logging_production.ini")
