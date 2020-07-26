import argparse
import pkg_resources
import os.path
import sys

import yaml

from amoeba.core import *


def main():
    # Initialize command-line argument parsing.
    parser = argparse.ArgumentParser(
        description="Don't panic.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    parser.add_argument('-c', '--config', type=str, default='amoeba.yaml', metavar='YAML', help='config file to use')
    args = parser.parse_args()

    # Load our YAML configuration file.
    if os.path.exists(args.config):
        # Use a fully specified file name.
        with open(args.config) as f:
            config = yaml.safe_load(f)
    elif pkg_resources.resource_exists(__name__, os.path.join('data', args.config)):
        # Use a file under our package's data directory.
        with pkg_resources.resource_stream(__name__, os.path.join('data', args.config)) as f:
            config = yaml.safe_load(f)
    else:
        print(f'Unable to locate the specified config file: {args.config}.')
        sys.exit(-1)

    world = World(0, 0)
    for color in config["cities"]:
        world.add_disease(Disease(color, config["constants"]["cubes_per_color"]))
        for name in config["cities"][color]:
            world.add_city(City(name, 0, color, world))
    for city1, city2 in config["edges"]:
        world.add_edge(city1, city2)

if __name__ == "__main__":
    main()
