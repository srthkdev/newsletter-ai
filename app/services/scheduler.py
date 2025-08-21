"""
Newsletter Scheduler Service for Automated Background Processing
Handles frequency-based scheduling and Portia agent orchestration
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass

from app.portia.agent_orchestrator import agent_orchestrator
from app.services.memory import memory_service
from app.core.database import get_db
from app.models.user import User
from app.models.preferences import UserPreferences


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    """Represents a scheduled newsletter job"""
    user_id: str
    frequency: str
    send_time: str
    timezone: str
    last_sent: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
    status: str = "active"  # active, paused, error


class NewsletterScheduler:
    """
    Newsletter scheduling service with Portia agent orchestration
    Handles automated newsletter generation and delivery
    """

    def __init__(self):
        self.jobs: Dict[str, ScheduledJob] = {}
        self.agent_orchestrator = agent_orchestrator
        self.memory_service = memory_service
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False

    async def start_scheduler(self):
        """Start the background scheduler"""
        logger.info("🚀 Starting Newsletter Scheduler Service")
        self.running = True
        
        # Load existing scheduled jobs
        await self.load_scheduled_jobs()
        
        # Schedule regular job checks
        schedule.every(1).minutes.do(self._check_scheduled_jobs)
        schedule.every(1).hours.do(self._refresh_jobs)
        schedule.every(24).hours.do(self._cleanup_old_jobs)
        
        # Run scheduler loop
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute

    async def stop_scheduler(self):
        """Stop the scheduler gracefully"""
        logger.info("🛑 Stopping Newsletter Scheduler Service")
        self.running = False
        self.executor.shutdown(wait=True)

    async def load_scheduled_jobs(self):
        """Load scheduled jobs from database"""
        try:
            # Get all users with preferences set
            db = next(get_db())
            users_with_prefs = db.query(User).join(UserPreferences).all()
            
            for user in users_with_prefs:
                if hasattr(user, 'preferences') and user.preferences:
                    await self.add_user_schedule(
                        user_id=str(user.id),
                        frequency=user.preferences.frequency,
                        send_time=user.preferences.send_time or "09:00",
                        timezone=user.preferences.timezone or "UTC"
                    )
            
            logger.info(f"📅 Loaded {len(self.jobs)} scheduled jobs")
            
        except Exception as e:
            logger.error(f"❌ Failed to load scheduled jobs: {e}")

    async def add_user_schedule(
        self, 
        user_id: str, 
        frequency: str, 
        send_time: str = "09:00", 
        timezone: str = "UTC"
    ):
        """Add or update a user's newsletter schedule"""
        
        job = ScheduledJob(
            user_id=user_id,
            frequency=frequency,
            send_time=send_time,
            timezone=timezone,
            next_scheduled=self._calculate_next_send_time(frequency, send_time, timezone)
        )
        
        self.jobs[user_id] = job
        logger.info(f"📅 Scheduled newsletter for user {user_id}: {frequency} at {send_time} {timezone}")

    async def remove_user_schedule(self, user_id: str):
        """Remove a user's schedule"""
        if user_id in self.jobs:
            del self.jobs[user_id]
            logger.info(f"🗑️ Removed schedule for user {user_id}")

    async def pause_user_schedule(self, user_id: str):
        """Pause a user's schedule"""
        if user_id in self.jobs:
            self.jobs[user_id].status = "paused"
            logger.info(f"⏸️ Paused schedule for user {user_id}")

    async def resume_user_schedule(self, user_id: str):
        """Resume a user's schedule"""
        if user_id in self.jobs:
            self.jobs[user_id].status = "active"
            logger.info(f"▶️ Resumed schedule for user {user_id}")

    def _calculate_next_send_time(
        self, 
        frequency: str, 
        send_time: str, 
        timezone: str
    ) -> datetime:
        """Calculate the next send time based on frequency"""
        
        now = datetime.utcnow()
        
        # Parse send_time (assuming HH:MM format)
        try:
            hour, minute = map(int, send_time.split(':'))
        except:
            hour, minute = 9, 0  # Default to 9:00 AM
        
        # Calculate next send time based on frequency
        if frequency == "daily":
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send += timedelta(days=1)
                
        elif frequency == "every_2_days":
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send += timedelta(days=2)
                
        elif frequency == "weekly":
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            days_until_next = (7 - now.weekday()) % 7
            if days_until_next == 0 and next_send <= now:
                days_until_next = 7
            next_send += timedelta(days=days_until_next)
            
        elif frequency == "monthly":
            next_send = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            if next_send.month == 12:
                next_send = next_send.replace(year=next_send.year + 1, month=1)
            else:
                next_send = next_send.replace(month=next_send.month + 1)
                
        else:
            # Default to weekly
            next_send = now + timedelta(days=7)
        
        return next_send

    def _check_scheduled_jobs(self):
        """Check and execute scheduled jobs"""
        asyncio.create_task(self._async_check_scheduled_jobs())

    async def _async_check_scheduled_jobs(self):
        """Async version of job checking"""
        now = datetime.utcnow()
        
        for user_id, job in self.jobs.items():
            if (job.status == "active" and 
                job.next_scheduled and 
                job.next_scheduled <= now):
                
                logger.info(f"🎯 Triggering scheduled newsletter for user {user_id}")
                
                # Execute newsletter generation in background
                asyncio.create_task(self._generate_scheduled_newsletter(job))

    async def _generate_scheduled_newsletter(self, job: ScheduledJob):
        """Generate and send a scheduled newsletter"""
        try:
            logger.info(f"🤖 Generating scheduled newsletter for user {job.user_id}")
            
            # Use agent orchestrator to generate newsletter
            result = await self.agent_orchestrator.generate_newsletter(
                user_id=job.user_id,
                custom_prompt=None,  # Use default preferences
                send_email=True,
                user_email=None  # Will be retrieved from user data
            )
            
            if result.get("success"):
                # Update job status
                job.last_sent = datetime.utcnow()
                job.next_scheduled = self._calculate_next_send_time(
                    job.frequency, job.send_time, job.timezone
                )
                job.status = "active"
                
                logger.info(f"✅ Successfully sent scheduled newsletter to user {job.user_id}")
                
                # Store in memory for tracking
                await self.memory_service.store_user_context(
                    job.user_id,
                    "scheduled_newsletter",
                    {
                        "sent_at": job.last_sent.isoformat(),
                        "frequency": job.frequency,
                        "newsletter_data": result.get("newsletter")
                    }
                )
                
            else:
                # Handle failure
                job.status = "error"
                logger.error(f"❌ Failed to generate newsletter for user {job.user_id}: {result.get('error')}")
                
        except Exception as e:
            job.status = "error"
            logger.error(f"❌ Exception in scheduled newsletter generation for user {job.user_id}: {e}")

    def _refresh_jobs(self):
        """Refresh job schedules from database"""
        asyncio.create_task(self.load_scheduled_jobs())

    def _cleanup_old_jobs(self):
        """Clean up old or inactive jobs"""
        asyncio.create_task(self._async_cleanup_old_jobs())

    async def _async_cleanup_old_jobs(self):
        """Async cleanup of old jobs"""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        jobs_to_remove = []
        for user_id, job in self.jobs.items():
            if (job.last_sent and job.last_sent < cutoff_date and 
                job.status == "error"):
                jobs_to_remove.append(user_id)
        
        for user_id in jobs_to_remove:
            del self.jobs[user_id]
            logger.info(f"🧹 Cleaned up old job for user {user_id}")

    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        active_jobs = sum(1 for job in self.jobs.values() if job.status == "active")
        paused_jobs = sum(1 for job in self.jobs.values() if job.status == "paused")
        error_jobs = sum(1 for job in self.jobs.values() if job.status == "error")
        
        return {
            "running": self.running,
            "total_jobs": len(self.jobs),
            "active_jobs": active_jobs,
            "paused_jobs": paused_jobs,
            "error_jobs": error_jobs,
            "next_jobs": [
                {
                    "user_id": job.user_id,
                    "frequency": job.frequency,
                    "next_scheduled": job.next_scheduled.isoformat() if job.next_scheduled else None
                }
                for job in sorted(
                    self.jobs.values(), 
                    key=lambda x: x.next_scheduled or datetime.max
                )[:5]
            ]
        }

    async def get_user_schedule_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule information for a specific user"""
        if user_id not in self.jobs:
            return None
        
        job = self.jobs[user_id]
        return {
            "user_id": job.user_id,
            "frequency": job.frequency,
            "send_time": job.send_time,
            "timezone": job.timezone,
            "status": job.status,
            "last_sent": job.last_sent.isoformat() if job.last_sent else None,
            "next_scheduled": job.next_scheduled.isoformat() if job.next_scheduled else None
        }

    async def trigger_immediate_newsletter(self, user_id: str) -> Dict[str, Any]:
        """Trigger an immediate newsletter for a user (outside of schedule)"""
        try:
            logger.info(f"🚀 Triggering immediate newsletter for user {user_id}")
            
            result = await self.agent_orchestrator.generate_newsletter(
                user_id=user_id,
                custom_prompt=None,
                send_email=True,
                user_email=None
            )
            
            if result.get("success"):
                logger.info(f"✅ Successfully sent immediate newsletter to user {user_id}")
                return {"success": True, "message": "Newsletter sent successfully"}
            else:
                logger.error(f"❌ Failed to send immediate newsletter to user {user_id}")
                return {"success": False, "message": result.get("error", "Unknown error")}
                
        except Exception as e:
            logger.error(f"❌ Exception in immediate newsletter generation: {e}")
            return {"success": False, "message": str(e)}


# Global scheduler instance
newsletter_scheduler = NewsletterScheduler()


# Scheduler control functions
async def start_newsletter_scheduler():
    """Start the global newsletter scheduler"""
    await newsletter_scheduler.start_scheduler()


async def stop_newsletter_scheduler():
    """Stop the global newsletter scheduler"""
    await newsletter_scheduler.stop_scheduler()


async def add_user_to_scheduler(user_id: str, frequency: str, send_time: str = "09:00", timezone: str = "UTC"):
    """Add a user to the newsletter scheduler"""
    await newsletter_scheduler.add_user_schedule(user_id, frequency, send_time, timezone)


async def remove_user_from_scheduler(user_id: str):
    """Remove a user from the newsletter scheduler"""
    await newsletter_scheduler.remove_user_schedule(user_id)


async def get_scheduler_status():
    """Get the current status of the newsletter scheduler"""
    return await newsletter_scheduler.get_scheduler_status()