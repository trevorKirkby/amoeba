import pkg_resources
import yaml
from amoeba.core import *


def main():
    stream = pkg_resources.resource_stream(__name__, 'data/amoeba.yaml')
    config = yaml.safe_load(stream)

    diseases = {}
    world = World([2,2,2,3,3,4,4], 2, 8, 6)
    for color in config["cities"]:
        world.add_disease(Disease(color, config["constants"]["cubes_per_color"]))
        for name in config["cities"][color]:
            world.add_city(City(name, 0, color, world))
    for city1, city2 in config["edges"]:
        world.add_edge(city1, city2)

if __name__ == "__main__":
    main()
