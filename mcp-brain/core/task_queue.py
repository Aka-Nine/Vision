import asyncio

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.workers = []
        self.tasks = {}

    def start_workers(self, num_workers=2):
        for _ in range(num_workers):
            task = asyncio.create_task(self._worker())
            self.workers.append(task)

    async def _worker(self):
        while True:
            job_id, func, args, kwargs, retries = await self.queue.get()
            self.tasks[job_id] = "running"
            try:
                await func(*args, **kwargs)
                self.tasks[job_id] = "completed"
            except Exception as e:
                print(f"Task {job_id} failed: {e}")
                if retries > 0:
                    self.tasks[job_id] = "retrying"
                    await self.queue.put((job_id, func, args, kwargs, retries - 1))
                else:
                    self.tasks[job_id] = "failed"
            finally:
                self.queue.task_done()

    async def enqueue(self, job_id, func, *args, retries=3, **kwargs):
        self.tasks[job_id] = "queued"
        await self.queue.put((job_id, func, args, kwargs, retries))
        return job_id

task_queue = TaskQueue()
