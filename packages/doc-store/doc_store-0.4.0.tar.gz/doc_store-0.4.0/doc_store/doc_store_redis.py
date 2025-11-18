import os
from typing import Any, Literal
from doc_store.interface import Task, TaskInput
from .doc_store import DocStore as DocStoreMongo, TaskEntity
from .redis_stream import RedisStreamProducer, RedisStreamConsumer
from .config import config

class DocStoreRedis(DocStoreMongo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = RedisStreamProducer()
        self.consumer_group = config.redis.consumer_group
        self.consumer_pool = {}

    def _get_or_create_consumer(self, stream: str) -> RedisStreamConsumer:
        key = f"{stream}:{self.consumer_group}"
        if key not in self.consumer_pool:
            self.consumer_pool[key] = RedisStreamConsumer(None, stream, self.consumer_group, create_group=True)
        return self.consumer_pool[key]

    # TODO: priority
    def insert_task(self, target_id: str, task_input: TaskInput) -> Task:
        """Insert a new task into the database."""
        self._check_writable()
        if not target_id:
            raise ValueError("target_id must be provided.")
        if not isinstance(task_input, TaskInput):
            raise ValueError("task_input must be a TaskInput instance.")
        command = task_input.command
        if not command:
            raise ValueError("command must be a non-empty string.")
        args = task_input.args or {}
        if any(not isinstance(k, str) for k in args.keys()):
            raise ValueError("All keys in args must be strings.")

        if command.startswith("ddp."):
            # command is a handler path.
            command, args["path"] = "handler", command

        task_entity = TaskEntity(
            target=target_id,
            command=command,
            args=args,
            status="new",
            create_user=self.username,
            update_user=None,
            grab_user=None,
            grab_time=0,
            error_message=None,
        )

        result = self.producer.add(command, task_entity.model_dump())
        return Task(
                id=result,
                target=task_entity.target,
                command=task_entity.command,
                args=task_entity.args,
                status=task_entity.status,
                create_user=task_entity.create_user,
                update_user=task_entity.update_user,
            )

    def grab_new_tasks(self, command: str, args: dict[str, Any] = {}, create_user: str | None = None, num=500, hold_sec=3600) -> list[Task]:
        consumer = self._get_or_create_consumer(command)
        messages = consumer.read(num)

        tasks = []
        for message in messages:
            task_entity = TaskEntity(**message.fields)
            task = Task(
                id=message.id,
                rid=0,                   # 占位，避免校验失败
                target=task_entity.target,
                command=task_entity.command,
                args=task_entity.args,
                status=task_entity.status,
                create_user=task_entity.create_user,
                update_user=task_entity.update_user,
                grab_time=int(__import__("time").time() * 1000),  # 确保非 0，便于 update 校验
            )
            tasks.append(task)
        return tasks

    
    def update_task(
        self,
        task_id: str,
        grab_time: int,
        command: str,
        status: Literal["done", "error", "skipped"],
        error_message: str | None = None,
    ):
        """Update a task after processing."""
        self._check_writable()
        if not command:
            raise ValueError("command must be provided.")
        if not task_id:
            raise ValueError("task ID must be provided.")
        if not grab_time:
            raise ValueError("grab_time must be provided.")
        if status not in ("done", "error", "skipped"):
            raise ValueError("status must be one of 'done', 'error', or 'skipped'.")
        if status == "error" and not error_message:
            raise ValueError("error_message must be provided if status is 'error'.")

        consumer = self._get_or_create_consumer(command)
        consumer.ack([task_id])
        # TODO: persist task status

