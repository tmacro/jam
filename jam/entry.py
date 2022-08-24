import argparse
import configparser
import logging
import os
import pathlib
import sys
from functools import partial

from . import __version__ as jam_version
from .config import load_config
from .constant import MAX_LOG_LEVEL, STDIN, STDOUT
from .error import (
    JamError,
    ReferenceNotExistError,
    ReferenceResolutionError,
    ReferenceTypeMismatch,
    InvalidReferencedFile,
)
from .log import log
from .merge import recurse_update
from .reference import resolve_refs
from .util import has_yaml, path_type, safe_dump_json, safe_dump_yaml, safe_read

path_type_w_stdin = partial(path_type, allow_stdin=True)


def get_args():
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(sys.argv[0]).name,
        description="A cli for merging JSON and YAML files.",
        add_help=False,
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    parser.add_argument(
        "--version", action="store_true", help="Print program version information."
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity. Can be passed multiple times.",
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

    parser.add_argument(
        "--array-strategy",
        action="store",
        choices=["replace", "extend", "merge"],
        default="replace",
        help='Set merge strategy for arrays. One of "replace", "extend", or "merge". Defaults to "replace"',
    )

    parser.add_argument(
        "input",
        nargs="+",
        type=path_type_w_stdin,
        default=[],
        help="Read input from one or more paths.",
    )

    parser.add_argument(
        "-o",
        "--output",
        action="store",
        default="/dev/stdout",
        type=path_type,
        help="Write merged output to this path.",
    )

    args = parser.parse_args()

    if args.version:
        print(f"jam v{jam_version}")
        sys.exit(1)

    if args.verbose > MAX_LOG_LEVEL:
        args.verbose = MAX_LOG_LEVEL

    if not args.input:
        log.error("Must specify at least one input or pass --stdin.")
        return parser.parse_args(["--help"])

    return args


def cli():
    args = get_args()
    config = load_config(args)
    log.setLevel(config.loglvl)

    if config.output_format == "yaml" and not has_yaml:
        log.error("Output format set to yaml but PyYaml not installed.")
        sys.exit(1)

    merged = None
    for path in config.input_paths:
        log.info(f"Merging document: {path.name}")
        doc = safe_read(path)
        if doc is None:
            log.error(f"Failed to read input file {path}")
            sys.exit(1)

        try:
            merged = recurse_update(
                merged, resolve_refs(path, doc), array_strat=config.array_strategy
            )
        except ReferenceResolutionError as e:
            log.error("Encountered infinite loop resolving reference.")
            log.error(f"  referenced path: {e.ref_path}")
            log.error(f"  in: {e.parent_path}")
            exit(126)
        except ReferenceNotExistError as e:
            log.error(f"Referenced path does not exist: {e.ref_path}")
            if e.resolved_to:
                log.error(f"  resolved to: {e.resolved_to}")
            log.error(f"  in: {e.parent_path}")
            exit(127)
        except InvalidReferencedFile as e:
            log.error(f"Error reading referenced path {e.ref_path}!")
            if e.resolved_to:
                log.error(f"  resolved to: {e.resolved_to}")
            log.error(f"  in: {e.parent_path}")
            exit(128)
        except Exception:
            log.exception("Unhandled Error")
            exit(1)

    if config.output_format == "yaml":
        safe_dump_yaml(config.output_path, merged)
    else:
        safe_dump_json(config.output_path, merged)
