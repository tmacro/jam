import argparse
import configparser
import logging
import os
import pathlib
import sys

from . import __version__ as jam_version
from .config import load_config
from .constant import MAX_LOG_LEVEL, STDIN, STDOUT
from .error import JamError
from .log import log
from .merge import recurse_update
from .reference import resolve_refs
from .util import has_yaml, path_type, safe_dump_json, safe_dump_yaml, safe_read


def get_args():
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(sys.argv[0]).name,
        description="A cli tool for merging JSON and YAML files.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity. Can be passed multiple times. Defaults to errors only.",
    )

    parser.add_argument(
        "--version", action="store_true", help="Print program version information."
    )

    parser.add_argument(
        "-i",
        "--input",
        action="append",
        type=path_type,
        help="Read input from path. Can be passed multiple times. Defaults to stdin.",
    )

    parser.add_argument(
        "-o",
        "--output",
        action="store",
        default=None,
        type=path_type,
        help="Write merged output to path. Defaults to stdout.",
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Force output in json format",
    )

    parser.add_argument(
        "-y",
        "--yaml",
        action="store_true",
        help="Force output in yaml format",
    )

    parser.add_argument("--stdin", action="store_true", help="Read input from stdin")

    args = parser.parse_args()

    if args.version:
        print(f"jam v{jam_version}")
        sys.exit(1)

    if args.verbose > MAX_LOG_LEVEL:
        args.verbose = MAX_LOG_LEVEL

    if args.stdin:
        args.input.append(STDIN)

    if not args.input:
        log.error("Must specify at least one input or pass --stdin.")
        return parser.parse_args(["--help"])

    return args


def cli():
    args = get_args()
    config = load_config(args)
    log.setLevel(config.loglvl)

    merged = None
    for path in config.input_paths:
        log.info(f"Merging document: {path.name}")
        doc = safe_read(path)
        if doc is None:
            log.error(f"Failed to read input file {path}")
            sys.exit(1)
        try:
            merged = recurse_update(merged, resolve_refs(path, doc))
        except JamError as e:
            log.exception('Unhandled Error')
            sys.exit(1)

    if args.output and args.output != "-":
        output_file = args.output
        log.info(f"Writing to {args.output}")
    else:
        output_file = STDOUT

    output_format = "json"
    if args.json:
        output_format = "json"
    elif args.yaml:
        output_format = "yaml"
    elif output_file.suffix == ".json":
        output_format = "json"
    elif output_file.suffix == ".yaml":
        output_format = "yaml"
    elif output_file.suffix == ".yml":
        output_format = "yaml"
    elif args.input[0].suffix == ".json":
        output_format = "json"
    elif args.input[0].suffix == ".yaml":
        output_format = "yaml"
    elif args.input[0].suffix == ".yml":
        output_format = "yaml"

    if output_format == "yaml" and not has_yaml:
        log.error("Output format set to yaml but PyYaml not installed.")
        sys.exit(1)

    if output_format == "yaml":
        safe_dump_yaml(output_file, merged)
    else:
        safe_dump_json(output_file, merged)
