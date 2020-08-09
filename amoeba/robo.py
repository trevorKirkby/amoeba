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


def validate(what, src, dst):
    if what not in _objects:
        raise ValueError(f"Invalid task object: '{what}'.")
    if src not in _objects[what]:
        raise ValueError(f"Invalid '{what}' source: '{src}'.")
    if dst not in _objects[what]:
        raise ValueError(f"Invalid '{what}' destination: '{dst}'.")
    return what, src, dst


def parse(task):
    parsed = _parser.match(task)
    if not parsed or len(parsed.groups()) != 3:
        raise ValueError(f"Invalid task: '{task}'.")
    return validate(parsed.groups())


def listen(callback, what=None):
    if isinstance(what, str):
        filter = lambda w,s,d: w == what
    elif isinstance(what, (tuple, list)):
        what = tuple(what)
        filter = lambda w,s,d: w in what
    else:
        filter = lambda w,s,d: True
    _listeners.append((callback, filter))


def do(what, src, dst):
    what, src, dst = validate(what, src, dst)
    for listener, filter in _listeners:
        if filter(what, src, dst):
            listener(what, src, dst)


class Logger:
    def __init__(self, prefix='', name=None):
        self.prefix = prefix
        self.out = open(name, "w") if name else sys.stdout
    def __call__(self, what, src, dst):
        print(f"{self.prefix}{what} from {src} to {dst}", file=self.out)
