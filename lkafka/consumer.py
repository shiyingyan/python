# -*- coding: utf-8 -*-
# Created By Shing At 2022/3/14
import time

from kafka import KafkaConsumer

if __name__ == '__main__':
    c = KafkaConsumer('hh')

    while True:
        for msg in c:
            print(msg)
        time.sleep(1)
