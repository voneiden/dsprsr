import argparse
import json
import re

from parsers.ATtiny814 import ATtiny814Parser

def process_file(args):
    input_filename = args.input
    input_atdf_filename = args.atdf
    output_filename = args.output
    with open(input_filename, 'r') as f:
        data = json.load(f)

    with open(input_atdf_filename, 'r') as f:
        atdf = json.load(f)
    parser = ATtiny814Parser(atdf, data)
    parser.process()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input')
    arg_parser.add_argument('atdf')
    arg_parser.add_argument('output')
    args = arg_parser.parse_args()
    process_file(args)
