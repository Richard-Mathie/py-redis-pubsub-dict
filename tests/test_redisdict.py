#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 11:40:23 2018

@author: richard
"""
from redis_pubsub_dict import RedisDict
from unittest import TestCase
import fakeredis


class BaseRedisTests(TestCase):
    def get_redis(self):
        return fakeredis.FakeStrictRedis()

    def get_dict(self):
        self.rd = RedisDict(self.r, 'test')

    def setUp(self):
        self.r = self.get_redis()
        self.get_dict()

    def test_init(self):
        pass

    def tearDown(self):
        # Clear data in fakeredis.
        self.r.flushall()


class RedisDictTests(BaseRedisTests):

    def test_set(self):
        rd = self.rd
        rd[1] = [1, 2, 3, 4]
        assert rd[1] == [1, 2, 3, 4]
        return rd

    def test_get(self):
        rd = self.rd
        alist = [1, 2, 3, 4]
        rd[1] = alist
        assert rd[1] == [1, 2, 3, 4]  # but it has the same value
        assert rd['1'] == [1, 2, 3, 4]  # and the key is always a string

    def test_keys(self):
        rd = self.rd
        rd[1] = 'hello world'
        assert list(rd.keys()) == ['1']  # Note keys can only be strings

    def test_dict(self):
        rd = self.test_set()
        assert dict(rd) == {'1': [1, 2, 3, 4]}

    def test_del(self):
        rd = self.test_set()
        del rd[1]
        assert dict(rd) == {}
