Redis PubSub Dict
=================

A python class for using redis, or other key value stores, as a
dictionary and caching the values locally for read heavy workloads.

Usage
-----

The idea is that Deleting or Updating keys in an instance of
``PubSubRedisDict`` or ``PubSubCacheManager`` will update the matching
cached keys in all instances of ``PubSubCacheManager``.
``PubSubCacheManager`` will therefor maintain a cache of recently used
keys using an ``lru`` or just a straight up ``dict()``. This will reduce
the round trip latency and network overhead for any reads of the cached
keys.

``RedisDict`` and ``RedisDict`` should work with instances of
``redis.StrictRedis`` or ``rediscluster.StrictRedisCluster``. Use the
``prefix`` for managing redis key namespaces.

RedisDict
~~~~~~~~~

Just like a normal dictionary, but networked. Initialisation wont take a
dictionary or iterable for now as it need connection and namespace
information.

\`\`\` rc = StrictRedisCluster(startup\_nodes=[{"host": "redis", "port":
"6379"}]) reddict = RedisDict(rc, 'namespace')

# you can set reddict[1] = 1 reddict[2] = [1,2,3] reddict['hello'] =
'world' reddict[('complex',1)] = {'I': {'Am': {'Quite': ['a', 'complex',
{'object': {} }]}}}

# get somewhere else reddict[1] reddict['1'] # note its the same as
reddict[1] reddict[('complex',1)] reddict["('complex', 1)"] # the key is
str(('complex',1))

# delete del reddict[1] # .. ect \`\`\`

PubSubRedisDict
~~~~~~~~~~~~~~~

Like ``RedisDict`` but will publish key update and delete events to a
``<namespace>/[update|delete]`` channel.

``redpubsub = PubSubRedisDict(rc, 'namespace')   # ect as before``

PubSubCacheManager
~~~~~~~~~~~~~~~~~~

Like ``pylry.WriteThroughCacheManager`` but updates cache keys from
store when it receives a message from the
``<namespace>/[update|delete]`` channel.
``cache = pylru.lrucache(10) # maybe more than 10   redstore = PubSubRedisDict(rc, 'namespace')   redcache = PubSubCacheManager(redstore, cache)   # ect as before   # see the cache   print dict(redcache.cache)``

Limitations
-----------

-  all keys are strings.
-  ``msgpack`` is used to marshal objects to redis, so ``msgpack``
   object limitations apply. Though you can monkey patch the modules
   ``loads`` and ``dumps`` method if you like.
-  publish will publish to all consuming dictionary instances, there is
   no partitioning, so writes and updates are expensive. You could come
   up with a partitioning strategy to improve this.
-  The published items eventually end up in the watched cash. There may
   be a
