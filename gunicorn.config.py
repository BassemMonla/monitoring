import os
import platform

if platform.system() == "Darwin":
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

bind = "0.0.0.0:4444"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
workers = int(os.environ.get("GUNICORN_WORKERS", "4"))
