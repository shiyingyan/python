# -*- coding: utf-8 -*-
# Created By Shing At 2022/3/14

from kafka import KafkaProducer

if __name__ == '__main__':
    p = KafkaProducer()
    while True:
        for i in range(100):
            p.send('hh', bytes(f'index {i}', encoding='utf8'))
