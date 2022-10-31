# -*- coding: utf-8 -*-
"""
This module manages the LRU cache. Cache size can be passed at creating
an instance of a class. Class’s get() method takes key and returns value
from cache or None if key doesn't exist. It's set() method takes key and
value and set them into a cache if they don't exist or places the key at
the end of cache flush queue.
"""
# pylint: disable=C0115, C0116
import argparse
import collections
import logging
import logging.config

LOG_FILE = "cache.log"
LOG_LEVEL_FILE = logging.INFO
LOG_LEVEL_STREAM = logging.DEBUG


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--stream',
        action='store_true',
        help="output log to console",
        required=False
        )
    return parser


log_conf = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s\t%(levelname)s\t%(message)s",
        },
        "processed": {
            "format": "|| %(asctime)s\t%(levelname)s\t%(name)s\t%(message)s",
        },
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "level": LOG_LEVEL_FILE,
            "filename": LOG_FILE,
            "formatter": "simple",

        },
        "stream_handler": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL_STREAM,
            "formatter": "processed",
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["file_handler"],
        },
        "total": {
            "level": "DEBUG",
            "handlers": ["file_handler", "stream_handler"],
        },
    },
}

logging.config.dictConfig(log_conf)

args_parser = create_parser()
args = args_parser.parse_args()

if args.stream:
    logger = logging.getLogger("total")
    logger.propagate = False
else:
    logger = logging.getLogger()


class LRUCache:
    """Manage the cache for a dict with cache size limitation."""

    def __init__(self, limit=42, data_cache=None, deq=None):
        """Initialize LRU Cache."""
        self.limit = limit
        self.data_cache = data_cache
        self.deq = deq

        if not self.data_cache:
            self.data_cache = {}

        if not self.deq:
            self.deq = collections.deque(self.data_cache.keys())

    def get(self, key):
        """Return value from LRU Cache by key."""
        if key not in self.data_cache:
            return None
        value = self.data_cache[key]
        logger.info(
            "get \"%s\" from cache", value
            )
        self.deq.remove(key)
        logger.debug("remove \"%s\" from deque", key)
        self.deq.append(key)
        logger.debug("add \"%s\" to deque", key)
        return value

    def set(self, key, value):
        """
        Take key and value and set them into LRU Cache
        if they don't exist.
        """
        if key in self.data_cache:
            self.deq.remove(key)
            logger.debug("remove \"%s\" from deque", key)
            self.deq.append(key)
            logger.debug("add \"%s\" to deque", key)
        elif key not in self.data_cache and len(self.deq) < self.limit:
            self.data_cache[key] = value
            self.deq.append(key)
            logger.debug("add \"%s\" to deque", key)
        else:
            rem = self.deq.popleft()
            del self.data_cache[rem]
            logger.warning("remove from cache: \"%s\"", rem)
            self.data_cache[key] = value
            logger.info(
                "add \"%s\": \"%s\" to cache", key, self.data_cache[key]
                )
            self.deq.append(key)
            logger.debug("add \"%s\" to deque", key)


def main():
    """Create and test LRU cache."""
    cache = LRUCache(2)

    cache.set("k1", "val1")
    cache.set("k2", "val2")

    cache.get("k3")
    cache.get("k2")
    cache.get("k1")

    cache.set("k3", "val3")

    cache.get("k3")
    cache.get("k2")
    cache.get("k1")


if __name__ == '__main__':
    main()
