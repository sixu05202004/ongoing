# -*- coding: utf-8 -*-
"""
    celery.backends.redis
    ~~~~~~~~~~~~~~~~~~~~~

    Redis result store backend.

"""
from __future__ import absolute_import

from functools import partial

from kombu.utils import cached_property, retry_over_time
from kombu.utils.url import _parse_url

from celery import states
from celery.canvas import maybe_signature
from celery.exceptions import ChordError, ImproperlyConfigured
from celery.five import string_t
from celery.utils import deprecated_property
from celery.utils.functional import dictfilter
from celery.utils.log import get_logger
from celery.utils.timeutils import humanize_seconds

from .base import KeyValueStoreBackend

try:
    import redis
    from redis.exceptions import ConnectionError
    from kombu.transport.redis import get_redis_error_classes
except ImportError:                 # pragma: no cover
    redis = None                    # noqa
    ConnectionError = None          # noqa
    get_redis_error_classes = None  # noqa

__all__ = ['RedisBackend']

REDIS_MISSING = """\
You need to install the redis library in order to use \
the Redis result store backend."""

E_LOST = """\
Connection to Redis lost: Retry (%s/%s) %s.\
"""

logger = get_logger(__name__)
error = logger.error


class RedisBackend(KeyValueStoreBackend):
    """Redis task result store."""

    #: redis-py client module.
    redis = redis

    #: Maximium number of connections in the pool.
    max_connections = None

    supports_autoexpire = True
    supports_native_join = True

    def __init__(self, host=None, port=None, db=None, password=None,
                 max_connections=None, url=None,
                 connection_pool=None, **kwargs):
        super(RedisBackend, self).__init__(expires_type=int, **kwargs)
        _get = self.app.conf.get
        if self.redis is None:
            raise ImproperlyConfigured(REDIS_MISSING)

        if host and '://' in host:
            url = host
            host = None

        self.max_connections = (
            max_connections or
            _get('redis_max_connections') or
            self.max_connections
        )
        self._ConnectionPool = connection_pool

        self.connparams = {
            'host': _get('redis_host') or 'localhost',
            'port': _get('redis_port') or 6379,
            'db': _get('redis_db') or 0,
            'password': _get('redis_password'),
            'socket_timeout': _get('redis_socket_timeout'),
            'max_connections': self.max_connections,
        }
        if url:
            self.connparams = self._params_from_url(url, self.connparams)
        self.url = url

        self.connection_errors, self.channel_errors = (
            get_redis_error_classes() if get_redis_error_classes
            else ((), ()))

    def _params_from_url(self, url, defaults):
        scheme, host, port, user, password, path, query = _parse_url(url)
        connparams = dict(
            defaults, **dictfilter({
                'host': host, 'port': port, 'password': password,
                'db': query.pop('virtual_host', None)})
        )

        if scheme == 'socket':
            # use 'path' as path to the socket… in this case
            # the database number should be given in 'query'
            connparams.update({
                'connection_class': self.redis.UnixDomainSocketConnection,
                'path': '/' + path,
            })
            # host+port are invalid options when using this connection type.
            connparams.pop('host', None)
            connparams.pop('port', None)
        else:
            connparams['db'] = path

        # db may be string and start with / like in kombu.
        db = connparams.get('db') or 0
        db = db.strip('/') if isinstance(db, string_t) else db
        connparams['db'] = int(db)

        # Query parameters override other parameters
        connparams.update(query)
        return connparams

    def get(self, key):
        return self.client.get(key)

    def mget(self, keys):
        return self.client.mget(keys)

    def ensure(self, fun, args, **policy):
        retry_policy = dict(self.retry_policy, **policy)
        max_retries = retry_policy.get('max_retries')
        return retry_over_time(
            fun, self.connection_errors, args, {},
            partial(self.on_connection_error, max_retries),
            **retry_policy
        )

    def on_connection_error(self, max_retries, exc, intervals, retries):
        tts = next(intervals)
        error(E_LOST, retries, max_retries or 'Inf',
              humanize_seconds(tts, 'in '))
        return tts

    def set(self, key, value, **retry_policy):
        return self.ensure(self._set, (key, value), **retry_policy)

    def _set(self, key, value):
        with self.client.pipeline() as pipe:
            if self.expires:
                pipe.setex(key, self.expires, value)
            else:
                pipe.set(key, value)
            pipe.publish(key, value)
            pipe.execute()

    def delete(self, key):
        self.client.delete(key)

    def incr(self, key):
        return self.client.incr(key)

    def expire(self, key, value):
        return self.client.expire(key, value)

    def add_to_chord(self, group_id, result):
        self.client.incr(self.get_key_for_group(group_id, '.t'), 1)

    def _unpack_chord_result(self, tup, decode,
                             EXCEPTION_STATES=states.EXCEPTION_STATES,
                             PROPAGATE_STATES=states.PROPAGATE_STATES):
        _, tid, state, retval = decode(tup)
        if state in EXCEPTION_STATES:
            retval = self.exception_to_python(retval)
        if state in PROPAGATE_STATES:
            raise ChordError('Dependency {0} raised {1!r}'.format(tid, retval))
        return retval

    def apply_chord(self, header, partial_args, group_id, body,
                    result=None, options={}, **kwargs):
        # avoids saving the group in the redis db.
        options['task_id'] = group_id
        return header(*partial_args, **options or {})

    def on_chord_part_return(self, request, state, result, propagate=None):
        app = self.app
        tid, gid = request.id, request.group
        if not gid or not tid:
            return

        client = self.client
        jkey = self.get_key_for_group(gid, '.j')
        tkey = self.get_key_for_group(gid, '.t')
        result = self.encode_result(result, state)
        with client.pipeline() as pipe:
            _, readycount, totaldiff, _, _ = pipe                           \
                .rpush(jkey, self.encode([1, tid, state, result]))          \
                .llen(jkey)                                                 \
                .get(tkey)                                                  \
                .expire(jkey, 86400)                                        \
                .expire(tkey, 86400)                                        \
                .execute()

        totaldiff = int(totaldiff or 0)

        try:
            callback = maybe_signature(request.chord, app=app)
            total = callback['chord_size'] + totaldiff
            if readycount == total:
                decode, unpack = self.decode, self._unpack_chord_result
                with client.pipeline() as pipe:
                    resl, _, _ = pipe               \
                        .lrange(jkey, 0, total)     \
                        .delete(jkey)               \
                        .delete(tkey)               \
                        .execute()
                try:
                    callback.delay([unpack(tup, decode) for tup in resl])
                except Exception as exc:
                    error('Chord callback for %r raised: %r',
                          request.group, exc, exc_info=1)
                    return self.chord_error_from_stack(
                        callback,
                        ChordError('Callback error: {0!r}'.format(exc)),
                    )
        except ChordError as exc:
            error('Chord %r raised: %r', request.group, exc, exc_info=1)
            return self.chord_error_from_stack(callback, exc)
        except Exception as exc:
            error('Chord %r raised: %r', request.group, exc, exc_info=1)
            return self.chord_error_from_stack(
                callback,
                ChordError('Join error: {0!r}'.format(exc)),
            )

    def _create_client(self, socket_timeout=None, socket_connect_timeout=None,
                       **params):
        return self.redis.StrictRedis(
            connection_pool=self.ConnectionPool(
                socket_timeout=socket_timeout and float(socket_timeout),
                socket_connect_timeout=socket_connect_timeout and float(
                    socket_connect_timeout),
                **params),
        )

    @property
    def ConnectionPool(self):
        if self._ConnectionPool is None:
            self._ConnectionPool = self.redis.ConnectionPool
        return self._ConnectionPool

    @cached_property
    def client(self):
        return self._create_client(**self.connparams)

    def __reduce__(self, args=(), kwargs={}):
        return super(RedisBackend, self).__reduce__(
            (self.url,), {'expires': self.expires},
        )

    @deprecated_property(4.0, 5.0)
    def host(self):
        return self.connparams['host']

    @deprecated_property(4.0, 5.0)
    def port(self):
        return self.connparams['port']

    @deprecated_property(4.0, 5.0)
    def db(self):
        return self.connparams['db']

    @deprecated_property(4.0, 5.0)
    def password(self):
        return self.connparams['password']
