#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 17:11:48 2018

@author: richard
"""
from threading import Lock
from msgpack import loads, dumps
from redis import StrictRedis
from pylru import WriteThroughCacheManager


class RedisDict(object):
    def __init__(self, redis=None, prefix='redisDict'):
        if redis is None:
            redis = StrictRedis()
        self.redis = redis
        self.prefix = prefix
        self.prefixer = '{}/{{}}'.format(prefix).format

    # Returns the number of redis keys
    def size(self, size=None):
        return sum(1 for k in self._keys())

    def clear(self):
        for k in self:
            del self[k]

    def __contains__(self, key):
        return self.redis.exists(self.prefixer(key))

    def __getitem__(self, key):
        buf = self.redis.get(self.prefixer(key))
        if buf is not None:
            return loads(buf)
        else:
            raise KeyError

    def get(self, key, default=None):
        """Get an item - return default (None) if not present"""
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self.redis.set(self.prefixer(key), dumps(value))

    def __delitem__(self, key):
        self.redis.delete(self.prefixer(key))

    def __iter__(self):
        return self.keys()

    def _keys(self):
        match = self.prefixer('*')
        return self.redis.scan_iter(match=match)

    def keys(self):
        prefix = self.prefixer('')
        return (k.strip(prefix) for k in self._keys())

    def values(self):
        return (self[k] for k in self.keys())

    def items(self):
        return ((k, self[k]) for k in self.keys())


class PubSubRedisDict(RedisDict):
    def __init__(self, *args, **kwargs):
        super(PubSubRedisDict, self).__init__(*args, **kwargs)
        self.subscriber = None
        self.pubsub = self.redis.pubsub()

    def subscribe(self, **callbacks):
        """Register callbacks to deal with update and delete events
        """
        self.callback = callbacks

        if self.subscriber is None:

            ps = self.pubsub
            handelers = {self.prefixer(action): self._handel_factory(callback)
                         for action, callback in callbacks.items()}
            ps.subscribe(**handelers)
            self.subscriber = ps.run_in_thread(sleep_time=0.01, daemon=True)

    def _handel_factory(self, callback):
        def handeler(mesg):
            callback(mesg['data'])
        return handeler

    def publish(self, action, key):
        self.redis.publish(self.prefixer(action), key)

    def __setitem__(self, key, value):
        self.redis.set(self.prefixer(key), dumps(value))
        self.publish('update', key)

    def __delitem__(self, key):
        self.redis.delete(self.prefixer(key))
        # publish the delete so it is removed else where
        self.publish('delete', key)

    def close(self):
        if hasattr(self, 'pubsub'):
            self.subscriber.stop()
            self.subscriber.join()
            self.pubsub.close()


NoneKey = object()


class PubSubCacheManager(WriteThroughCacheManager):

    def __init__(self, store, cache):
        self.store = store

        self.mutex = Lock()
        self.cache = cache

        if hasattr(store, 'pubsub'):
            store.subscribe(update=self._update_key, delete=self._delete_key)

    def _update_key(self, key):
        with self.mutex:
            if key in self.cache:
                self.cache[key] = self.store[key]

    def _delete_key(self, key):
        with self.mutex:
            if key in self.cache:
                del self.cache[key]

    def __contains__(self, key):
        # Check the cache first. If it is there we can return quickly.
        # if you want just local keys chack cache
        if str(key) in self.cache:
            return True

        # Not in the cache. Might be in the underlying store.
        return key in self.store

    def __getitem__(self, key):
        # First we try the cache. If successful we just return the value. If
        # not we catch KeyError and ignore it since that just means the key
        # was not in the cache.
        skey = str(key)
        with self.mutex:
            try:
                cache = self.cache[skey]
            except KeyError:
                pass
            else:
                if cache is NoneKey:
                    raise KeyError
                return cache

            # It wasn't in the cache. Look it up in the store, add the entry to
            # the cache, and return the value.
            try:
                value = self.store[key]
                self.cache[skey] = value
                return value
            except KeyError:
                self.cache[skey] = NoneKey
                raise KeyError

    def __setitem__(self, key, value):
        # Add the key/value pair to the cache and store.
        with self.mutex:
            self.cache[str(key)] = value
            self.store[key] = value

    def __delitem__(self, key):
        # Write-through behavior cache and store should be consistent. Delete
        # it from the store.
        del self.store[key]
        try:
            # Ok, delete from the store was successful. It might also be in
            # the cache, try and delete it. If not we catch the KeyError and
            # ignore it.
            del self.cache[str(key)]
        except KeyError:
            pass

    def close(self):
        self.store.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()