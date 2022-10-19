# -*- coding: utf-8 -*-
# Created By Shing At 2022/10/19

def func():
    for i in range(100):
        print(f'now i={i}')
        yield i


if __name__ == '__main__':
    for x in func():
        print('main', x)
