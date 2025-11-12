"""
OSWizard Patch Queue Service (root-level)
Handles enqueueing and execution of patch tasks (Ventoy, cleanup, vendor discovery).
"""

import os
import time
import logging
from queue import Queue, Empty
from threading import Thread

log = logging.getLogger("osw.patchqueue")


class PatchJob:
    def __init__(self, job_id, command, meta=None):
        self.job_id = job_id
        self.command = command
        self.meta = meta or {}
        self.timestamp = time.time()

    def __repr__(self):
        return f"<PatchJob {self.job_id} cmd={self.command}>"


class PatchQueue:
    def __init__(self):
        self.queue = Queue()
        self.active = False
        self.worker = None

    def enqueue(self, job):
        log.info(f"Enqueued patch job: {job}")
        self.queue.put(job)

    def run(self):
        if self.active:
            log.warning("PatchQueue already running.")
            return
        self.active = True
        self.worker = Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        log.info("PatchQueue started.")

    def _worker_loop(self):
        while self.active:
            try:
                job = self.queue.get(timeout=1)
                log.info(f"Executing patch job: {job}")
                self._execute(job)
                self.queue.task_done()
            except Empty:
                continue
            except Exception as e:
                log.error(f"Patch job error: {e}")

    def _execute(self, job):
        rc = os.system(job.command)
        if rc != 0:
            raise RuntimeError(f"Command failed with exit {rc}: {job.command}")
        log.info(f"Job {job.job_id} completed.")

    def flush(self):
        while not self.queue.empty():
            self.queue.get()
            self.queue.task_done()
        log.info("PatchQueue flushed.")

    def stop(self):
        self.active = False
        if self.worker:
            self.worker.join(timeout=2)
        log.info("PatchQueue stopped.")
