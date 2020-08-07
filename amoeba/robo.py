"""Support for low-level tasks that change the game state.
"""
import re
import collections
import sys


_parser = re.compile("^([\w \.]+) from ([\w \.]+) to ([\w \.]+)$")

_objects = collections.defaultdict(set)

_listeners = []


def enable(what, where):
    _objects[what].add(where)


def parse(task):
    parsed = _parser.match(task)
    if not parsed or len(parsed.groups()) != 3:
        raise ValueError(f"Invalid task: '{task}'.")
    what, src, dst = parsed.groups()
    if what not in _objects:
        raise ValueError(f"Invalid task object: '{what}'.")
    if src not in _objects[what]:
        raise ValueError(f"Invalid '{what}' source: '{src}'.")
    if dst not in _objects[what]:
        raise ValueError(f"Invalid '{what}' destination: '{dst}'.")
    return what, src, dst


def add_listener(callback, filter=None):
    _listeners.append((callback, filter))


def do(task):
    what, src, dst = parse(task)
    for listener, filter in _listeners:
        if filter is None or filter(what):
            listener(what, src, dst)


class Logger:
    def __init__(self, prefix='', name=None):
        self.prefix = prefix
        self.out = open(name, "w") if name else sys.stdout
    def __call__(self, what, src, dst):
        print(f"{self.prefix}{what} from {src} to {dst}", file=self.out)
