# -*- coding: utf-8 -*-
# Created By Shing At 2022/3/11
import asyncio
import threading
import time

import kafka

topic = 'demo'


def produce_msg():
    # lkafka.
    pass


async def consume_msg():
    consumer = kafka
    while True:
        time.sleep(1000)


if __name__ == '__main__':
    p = threading.Thread(target=produce_msg)
    p.start()

    asyncio.run(consume_msg())
