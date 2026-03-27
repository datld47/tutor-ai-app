import asyncio
from typing import Callable, Any
import logging

# Cấu hình logging chuyên nghiệp
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskBroker")

class TaskBroker:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_running = False

    async def submit_task(self, task_name: str, func: Callable, *args, **kwargs):
        """Gửi một tác vụ vào hàng đợi"""
        logger.info(f"📥 Task submitted: {task_name}")
        await self.queue.put({
            "name": task_name,
            "func": func,
            "args": args,
            "kwargs": kwargs
        })

    async def start_worker(self):
        """Worker chạy ngầm, xử lý từng task một"""
        self.is_running = True
        logger.info("🚀 Background Worker Started")
        
        while self.is_running:
            # Lấy task từ hàng đợi
            task = await self.queue.get()
            
            try:
                task_name = task["name"]
                logger.info(f"⚙️ Processing: {task_name}")
                
                # Thực thi hàm (có thể là async hoặc sync)
                func = task["func"]
                if asyncio.iscoroutinefunction(func):
                    await func(*task["args"], **task["kwargs"])
                else:
                    await asyncio.to_thread(func, *task["args"], **task["kwargs"])
                    
                logger.info(f"✅ Completed: {task_name}")
                
            except Exception as e:
                logger.error(f"❌ Task Failed: {e}")
            finally:
                self.queue.task_done()

task_broker = TaskBroker()
