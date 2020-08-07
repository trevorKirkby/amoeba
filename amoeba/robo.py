"""Support for low-level tasks that change the game state.
"""
import re
import collections

_parser = re.compile("^([\w\s]+) from ([\w\s]+) to ([\w\s]+)$")

_objects = collections.defaultdict(set)

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
