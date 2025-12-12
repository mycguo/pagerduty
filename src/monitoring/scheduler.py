import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from src.monitoring.monitor import Monitor
from src.monitoring.runner import MonitorRunner
from src.storage.storage import Storage

logger = logging.getLogger(__name__)

class MonitorScheduler:
    """Handles automatic scheduling of monitor runs."""
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("MonitorScheduler started")

    def run_monitor_job(self, monitor_id: str):
        """Job function to run a specific monitor."""
        # Reload monitor from storage to get latest config/enabled state
        monitor = self.storage.get_monitor(monitor_id)
        
        if not monitor:
            logger.warning(f"Monitor {monitor_id} not found during scheduled run")
            return
            
        if not monitor.enabled:
            logger.info(f"Monitor {monitor.name} is disabled, skipping scheduled run")
            return

        logger.info(f"Starting scheduled run for {monitor.name}")
        runner = MonitorRunner(headless=True)
        try:
            result = runner.run_monitor(monitor)
            self.storage.save_test_run(result)
            logger.info(f"Scheduled run for {monitor.name} completed: {result.status}")
        except Exception as e:
            logger.error(f"Scheduled run for {monitor.name} failed: {e}")

    def sync_jobs(self):
        """Synchronize scheduler jobs with current monitor configuration."""
        monitors = self.storage.get_monitors()
        active_monitor_ids = set()

        for monitor in monitors:
            job_id = f"monitor_job_{monitor.id}"
            
            if monitor.enabled:
                try:
                    # Update or create job
                    # Note: We replace the old job to ensure schedule is updated
                    self.scheduler.add_job(
                        self.run_monitor_job,
                        CronTrigger.from_crontab(monitor.schedule),
                        args=[monitor.id],
                        id=job_id,
                        replace_existing=True,
                        name=f"Run {monitor.name}"
                    )
                    active_monitor_ids.add(job_id)
                    logger.info(f"Scheduled job for {monitor.name} with schedule: {monitor.schedule}")
                except Exception as e:
                    logger.error(f"Failed to schedule {monitor.name}: {e}")
            else:
                 # If disabled, ensure no job exists
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)

        # Cleanup jobs for deleted monitors
        for job in self.scheduler.get_jobs():
            if job.id.startswith("monitor_job_") and job.id not in active_monitor_ids:
                self.scheduler.remove_job(job.id)
                logger.info(f"Removed stale job: {job.id}")

    def shutdown(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
