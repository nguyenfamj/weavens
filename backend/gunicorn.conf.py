import os
from multiprocessing import cpu_count

bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8386')}"
workers = int(os.getenv("WORKERS", cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 5
timeout = 120
graceful_timeout = 30

accesslog = "-"
errorlog = "-"
