#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:17:16 2018

@author: richard
"""
from pylru import lrucache
from redis.client import PubSub
from fakeredis import FakePubSub

from redis_pubsub_dict import PubSubRedisDict, PubSubCacheManager
from test_redisdict import BaseRedisTests, RedisDictTests
from time import sleep


def patch_pubsub_run_in_thread():
    def wait(self):
        while not self._q.empty():
            sleep(1)

    FakePubSub.run_in_thread = object.__getattribute__(PubSub, 'run_in_thread')
    FakePubSub.wait = wait


patch_pubsub_run_in_thread()


class PubSubCacheTests(RedisDictTests):
    def get_dict(self):
        cache = lrucache(10)
        store = PubSubRedisDict(self.r, 'pubsub')

        self.rd = PubSubCacheManager(store, cache)

    def tearDown(self):
        # Clear data in fakeredis.
        super(PubSubCacheTests, self).tearDown()
        self.rd.close()


class PubSub2CacheTests(BaseRedisTests):
    N = 2
    N_cache = 10

    def get_dict(self):
        self.rd = []
        for i in range(self.N):
            cache = lrucache(self.N_cache)
            store = PubSubRedisDict(self.r, 'pubsub')
            rd = PubSubCacheManager(store, cache)
            self.rd.append(rd)

    def spam_set(self, cache, obj=None):
        if obj is None:
            for i in range(20):
                cache[i] = i
        else:
            for i in range(20):
                cache[i] = obj

    def wait_till_empty(self):
        for i in range(2):
            sleep(0.1)
            for rd in self.rd:
                rd.store.pubsub.wait()

    def test_set(self):
        self.spam_set(self.rd[0])
        # should have cached the last N keys cached
        assert len(self.rd[0].cache) == self.N_cache

    def test_set_2(self):
        # set cache to monitor first
        self.spam_set(self.rd[1], "hello world")
        self.spam_set(self.rd[0], "set test")
        self.wait_till_empty()

        cache = dict(self.rd[1].cache.items())
        expect = dict(self.rd[0].cache.items())
        # check that the cache propergates accross the two opbects
        assert cache == expect
        assert dict(self.rd[0].store.items()) == dict(self.rd[1].store.items())

    def tearDown(self):
        # Clear data in fakeredis.
        self.wait_till_empty()
        for rd in self.rd:
            sleep(0.2)
            rd.store.pubsub.wait()
            rd.close()
        super(PubSub2CacheTests, self).tearDown()
