import argparse
import json
from xml.etree.ElementTree import parse

from xmljson import badgerfish as bf


def process_file(args):
    input_filename = args.input
    output_filename = args.output
    data = bf.data(parse(input_filename).getroot())
    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    args = parser.parse_args()
    process_file(args)
