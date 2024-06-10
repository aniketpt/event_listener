import json
import asyncio
from dataclasses import dataclass
from typing import Dict, Callable

from aiokafka import AIOKafkaConsumer
from pydantic import BaseModel



@dataclass
class TopicRegistration:
    models: Dict[str, BaseModel]
    action_fn: Callable[[BaseModel], None]


class EventListener:

    def __init__(self, bootstrap_servers: str, consumer_configurations: dict):
        self.bootstrap_servers = bootstrap_servers
        self.consumer_configurations = consumer_configurations
        self.registrations: Dict[str, TopicRegistration] = {}

    def topic(self, topic: str):

        def decorator(action_fn: Callable[[BaseModel], None]):

            def wrapper(message):
                models = self.registrations[topic].models
                kwargs = {arg_name: Model(**message) for arg_name, Model in models.items()}
                self.registrations[topic]["action_fn"](**kwargs)

            self.registrations[topic] = TopicRegistration(
                models=action_fn.__annotations__,
                action_fn=action_fn
            )
            return wrapper

        return decorator

    def create_consumer(self) -> AIOKafkaConsumer:
        loop = asyncio.get_running_loop()
        consumer = AIOKafkaConsumer(
            loop=loop,
            bootstrap_servers=self.bootstrap_servers,
            **self.consumer_configurations
        )
        consumer.subscribe(list(self.registrations.keys()))
        return consumer

    async def start_listening(self):
        self.consumer = self.create_consumer()
        await self.consumer.start()

        while True:
            try:
                async for message in self.consumer:
                    if not message.value:
                        continue
                    print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                         message.offset, message.key,
                                                         message.value))

                    message_value = json.loads(message.value.decode('utf-8'))
                    fn = self.registrations[message.topic].action_fn
                    models = self.registrations[message.topic].models
                    kwargs = {arg_name: Model(**message_value) for arg_name, Model in models.items()}
                    asyncio.create_task(fn(**kwargs))
            except Exception as exc:
                print(exc)
                await self.consumer.commit()
                continue
