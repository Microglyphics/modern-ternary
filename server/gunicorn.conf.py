# server/gunicorn.conf.py
import multiprocessing
import os

# Gunicorn config
bind = "0.0.0.0:" + str(os.getenv("PORT", "8080"))
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120

# Module imports config
chdir = os.path.dirname(os.path.abspath(__file__))
pythonpath = os.path.dirname(chdir)