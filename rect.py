# -*- coding:UTF-8 -*-
# Created by admin at 2020/1/19

import math


class Rect:
    '''
    矩形对象
    '''

    def __init__(self, top, left, width, height):
        '''
        注意，坐标系原点，在图纸左上角
        :param top:     左上顶点纵坐标
        :param left:    左上顶点横坐标
        :param width:   矩形宽度
        :param height:  矩形高度
        '''
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.right = self.left + width
        self.bottom = self.top + height

    def __eq__(self, other):
        return self.left == other.left \
               and self.top == other.top \
               and self.width == other.width \
               and self.height == other.height

    def isOverLay(self, another_rect):
        return self.left + self.width > another_rect.left \
               and another_rect.left + another_rect.width > self.left \
               and self.top + self.height > another_rect.top \
               and another_rect.top + another_rect.height > self.top

    def distance(self, another_rect):
        '''
        两个矩形，在坐标系中的间距
        '''
        if self.isOverLay(another_rect):
            return 0
        detal1 = abs(self.left + self.width - another_rect.left)
        detal2 = abs(self.left - (another_rect.left + another_rect.width))
        detal3 = abs(self.top + self.height - another_rect.top)
        detal4 = abs(self.top - (another_rect.top + another_rect.height))
        return min(detal1, detal2, detal3, detal4)

    def contains(self, another_rect):
        return all((
            another_rect.left >= self.left,
            another_rect.right <= self.right,
            another_rect.top >= self.top,
            another_rect.bottom <= self.bottom
        ))

    def resize(self, width_ratio, height_ratio):
        return Rect(
            self.top * height_ratio,
            self.left * width_ratio,
            self.width * width_ratio,
            self.height * height_ratio
        )

    def middle_point(self):
        return self.left + self.width/2, self.top + self.height/2

    def area(self):
        return self.width * self.height

    def jsondict(self):
        return {
            'x': self.left,
            'y': self.top,
            'width': self.width,
            'height': self.height
        }

if __name__ == '__main__':

    rect1 = Rect(165.7977600097656, 193.2004241943359, 1323.91748046875, 706.9754638671875)
    rect2 = Rect(150.6619567871094, 630.4056396484375, 106.03271484375, 319.8325805664062)
    print('dis:', rect1.distance(rect2))
