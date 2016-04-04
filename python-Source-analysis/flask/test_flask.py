#!/usr/bin/env python
# -*- coding: utf-8 -*-

test = lambda x: x


@test
class test_a(object):

    def __init__(self):
        self.a = 10
        self.b = 10

    def __str__(self):
        return "test_a"

if __name__ == '__main__':
    b = test_a()
    print b.a
