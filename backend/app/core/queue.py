import json
import asyncio
import logging
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from app.core.redis import redis_manager

logger = logging.getLogger(__name__)


class TaskQueue:
    """Redis-based task queue for background processing"""
    
    def __init__(self, queue_name: str = "default"):
        self.queue_name = f"queue:{queue_name}"
        self.processing_key = f"{self.queue_name}:processing"
        self.failed_key = f"{self.queue_name}:failed"
    
    async def enqueue(self, task_data: Dict[str, Any], priority: int = 0) -> str:
        """
        Enqueue a task for background processing
        
        Args:
            task_data: Task data including type, payload, etc.
            priority: Task priority (higher = more priority)
            
        Returns:
            Task ID
        """
        redis = redis_manager.get_redis()
        
        task_id = f"task:{datetime.utcnow().timestamp()}:{id(task_data)}"
        task = {
            "id": task_id,
            "data": task_data,
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0,
            "max_attempts": task_data.get("max_attempts", 3)
        }
        
        # Add to priority queue (Redis sorted set)
        await redis.zadd(self.queue_name, {json.dumps(task): priority})
        
        logger.info(f"Enqueued task {task_id} with priority {priority}")
        return task_id
    
    async def dequeue(self, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Dequeue a task for processing
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            Task data or None if timeout
        """
        redis = redis_manager.get_redis()
        
        # Get highest priority task (BZPOPMAX blocks until available)
        result = await redis.bzpopmax(self.queue_name, timeout=timeout)
        
        if not result:
            return None
        
        _, task_json, _ = result
        task = json.loads(task_json)
        
        # Move to processing queue
        await redis.hset(self.processing_key, task["id"], task_json)
        
        logger.debug(f"Dequeued task {task['id']}")
        return task
    
    async def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        redis = redis_manager.get_redis()
        result = await redis.hdel(self.processing_key, task_id)
        
        if result:
            logger.info(f"Completed task {task_id}")
        return bool(result)
    
    async def fail_task(self, task_id: str, error: str, retry: bool = True) -> bool:
        """
        Mark task as failed and optionally retry
        
        Args:
            task_id: Task ID
            error: Error message
            retry: Whether to retry the task
            
        Returns:
            True if task was handled, False if not found
        """
        redis = redis_manager.get_redis()
        
        # Get task from processing queue
        task_json = await redis.hget(self.processing_key, task_id)
        if not task_json:
            return False
        
        task = json.loads(task_json)
        task["attempts"] += 1
        task["last_error"] = error
        task["failed_at"] = datetime.utcnow().isoformat()
        
        # Remove from processing
        await redis.hdel(self.processing_key, task_id)
        
        if retry and task["attempts"] < task["max_attempts"]:
            # Re-queue with lower priority
            priority = -task["attempts"]  # Lower priority for retries
            await redis.zadd(self.queue_name, {json.dumps(task): priority})
            logger.warning(f"Retrying task {task_id} (attempt {task['attempts']})")
        else:
            # Move to failed queue
            await redis.hset(self.failed_key, task_id, json.dumps(task))
            logger.error(f"Task {task_id} failed permanently after {task['attempts']} attempts")
        
        return True
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        redis = redis_manager.get_redis()
        
        pending = await redis.zcard(self.queue_name)
        processing = await redis.hlen(self.processing_key)
        failed = await redis.hlen(self.failed_key)
        
        return {
            "pending": pending,
            "processing": processing,
            "failed": failed
        }


class TaskWorker:
    """Background task worker"""
    
    def __init__(self, queue: TaskQueue, handlers: Dict[str, Callable]):
        self.queue = queue
        self.handlers = handlers
        self.running = False
    
    async def start(self):
        """Start the worker"""
        self.running = True
        logger.info("Task worker started")
        
        while self.running:
            try:
                task = await self.queue.dequeue(timeout=5)
                if task:
                    await self._process_task(task)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        logger.info("Task worker stopped")
    
    async def _process_task(self, task: Dict[str, Any]):
        """Process a single task"""
        task_id = task["id"]
        task_data = task["data"]
        task_type = task_data.get("type")
        
        if task_type not in self.handlers:
            await self.queue.fail_task(task_id, f"No handler for task type: {task_type}", retry=False)
            return
        
        try:
            handler = self.handlers[task_type]
            await handler(task_data)
            await self.queue.complete_task(task_id)
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await self.queue.fail_task(task_id, str(e))


# Pre-configured queues
class Queues:
    # Different priority queues for different types of work
    high_priority = TaskQueue("high_priority")
    default = TaskQueue("default")
    low_priority = TaskQueue("low_priority")
    
    # Specific purpose queues
    email_queue = TaskQueue("email")
    analytics_queue = TaskQueue("analytics")
    cleanup_queue = TaskQueue("cleanup")


# Task types
class TaskTypes:
    SEND_EMAIL = "send_email"
    PROCESS_ANALYTICS = "process_analytics"
    CLEANUP_DATA = "cleanup_data"
    GENERATE_REPORT = "generate_report"
    SYNC_DATA = "sync_data"


# Example task handlers
async def send_email_handler(task_data: Dict[str, Any]):
    """Handle email sending tasks"""
    email_data = task_data.get("payload", {})
    # Implement email sending logic here
    logger.info(f"Sending email to {email_data.get('to')}")
    await asyncio.sleep(1)  # Simulate email sending


async def analytics_handler(task_data: Dict[str, Any]):
    """Handle analytics processing tasks"""
    analytics_data = task_data.get("payload", {})
    # Implement analytics processing logic here
    logger.info(f"Processing analytics for user {analytics_data.get('user_id')}")
    await asyncio.sleep(2)  # Simulate processing


# Default task handlers
DEFAULT_HANDLERS = {
    TaskTypes.SEND_EMAIL: send_email_handler,
    TaskTypes.PROCESS_ANALYTICS: analytics_handler,
}
