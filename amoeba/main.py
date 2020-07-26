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
    parser.add_argument('-n', '--num-players', type=int, metavar='N', help='number of players')
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

    # Initialize the world.
    world = World(config)

    # Start the game.
    world.start(args.num_players)

if __name__ == "__main__":
    main()
