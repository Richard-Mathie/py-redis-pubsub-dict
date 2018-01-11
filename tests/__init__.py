#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 15:46:37 2018

@author: richard
"""

from pylru import lrucache
from rediscluster import StrictRedisCluster

from redis_pubsub_dict import (RedisDict,
                               PubSubRedisDict,
                               PubSubCacheManager)

def test_setup():
    from time import sleep

    startup_nodes = [{"host": "redis", "port": "6379"}]

    rc = StrictRedisCluster(startup_nodes=startup_nodes)

    lru = lrucache(10)

    reddict = RedisDict(rc, 'alarms')
    redpubsub = PubSubRedisDict(rc, 'alarms')
    redcache = PubSubCacheManager(redpubsub, lru)
    redcache.close()
