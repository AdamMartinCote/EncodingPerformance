#!/usr/bin/env python
import sys
import argparse
import importlib
import algo.predictive
import algo.bytepair as bp
import json

from PIL import Image
import numpy as np


AVAILABLE_ALGOS = ["predictive", "pairs"]
DEFAULT_OUTPUT_NAME = "output.jpg"

op = {
    "input" : None,
    "output": DEFAULT_OUTPUT_NAME,
    "algo"  : None,
}

def parse(op):
    parser = argparse.ArgumentParser(
        description='Encode image files using different algorythms')

    parser.add_argument("-i", "--input",
                        dest='input',
                        required=True,
                        help="source image file",)

    parser.add_argument("-o", "--output",
                        dest='output',
                        help="destination filename",)

    parser.add_argument("-a", "--algo",
                        dest='algo',
                        help="Select encoding algorythms",)

    parser.add_argument("-d", "--decode",
                        dest='decode',
                        help="",)

    parser.add_argument("-s", "--show",
                        action="store_true",
                        help="open resulting file",)

    # FIXME: make incompatible with pairs
    parser.add_argument("-p", "--prediction-formula",
                        dest='prediction_formula',
                        help="",)

    args = parser.parse_args()

    if args.show:
        op['show'] = True

    if not args.algo in AVAILABLE_ALGOS:
        print(
            "Unknown algorythm\n\n"
            "Available algorythms are:")
        for a in AVAILABLE_ALGOS:
            print(" - " + a)
        sys.exit(1)
    else:
        op["algo"] = args.algo

    op["input"] = args.input

    if args.prediction_formula:
        op["pred"]  = args.prediction_formula

    if args.output:
        op["output"] = args.output

def run_bytepair(op) -> None:
    print(json.dumps(bp.bytepair_get_results(op["input"]), sort_keys=True))


def run_predictive(op) -> None:
    """ Open file and call algorithm
    """

    try:
        img = Image.open(op['input'])
    except Exception as e:
        print(e)
        sys.exit(1)

    algo.predictive.run(op)


if __name__ == "__main__":
    parse(op)
    if op["input"] and op["output"] and op["algo"]:
        if op["algo"] == "pairs":
            run_bytepair(op)
        elif op["algo"] == "predictive":
            run_predictive(op)
