#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 15:46:37 2018

@author: richard
"""

from redis_lru_dict import (RedisDict,
                            PubSubRedisDict,
                            PubSubCacheManager)

if __name__ == 'main':
    from rediscluster import StrictRedisCluster

    from pylru import lrucache

    startup_nodes = [{"host": "redis", "port": "6379"}]

    rc = StrictRedisCluster(startup_nodes=startup_nodes)

    lru = lrucache(10)

    reddict = RedisDict(rc, 'alarms')
    redpubsub = PubSubRedisDict(rc, 'alarms')
    redcache = PubSubCacheManager(redpubsub, lru)
    print 'finnish'
