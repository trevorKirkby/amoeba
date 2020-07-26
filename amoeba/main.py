import pkg_resources
import yaml
from amoeba.core import *


def main():
    stream = pkg_resources.resource_stream(__name__, 'data/amoeba.yaml')
    config = yaml.safe_load(stream)
    print(config)


if __name__ == "__main__":
    main()
