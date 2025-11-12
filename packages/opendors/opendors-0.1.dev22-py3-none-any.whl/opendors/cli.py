import glob
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
import re

from pydantic_core import ValidationError

from opendors.exceptions import OpendorsException
from opendors.model import (
    Corpus,
    SourceCodeRepository,
    ResearchSoftware,
    VCS,
)


def _raise(msg: str, err_len: int = 0):
    if getattr(sys, "tracebacklimit", 1000) < 1000:
        raise SystemExit(OpendorsException(msg, err_len))
    else:
        raise OpendorsException(msg, 0)


def export_schema(args):
    with open("schema.json", "w") as schema_file:
        if not args.compressed:
            json.dump(Corpus.model_json_schema(), schema_file, indent=4)
        else:
            json.dump(Corpus.model_json_schema(), schema_file)
    print("Exported schema to schema.json.")


def parse_lang_thresh(lang_thresh: str) -> tuple[str, float]:
    lang, delim, val = lang_thresh.rpartition("=")
    if lang == delim == "":  # Only language given
        return val, 0.0
    elif val == "":  # Trailing '=' without value
        _raise(f"Threshold value missing: {lang}=<value missing>.", 15)
    elif "=" in lang:
        _raise(
            f"Language name cannot contain reserved character '=': {lang}.", len(lang)
        )
    else:
        try:
            thresh = float(val)
        except ValueError:
            _raise(f"Threshold value must be integer or float: {lang}={val}.", len(val))
        return lang, thresh


def read_corpus(infile: str) -> Corpus:
    inpath = Path(infile)
    if not inpath.exists():
        _raise(f"Dataset file does not exist: {inpath}.")
    elif not inpath.is_file():
        _raise(f"Dataset file argument is a directory: {inpath}.")
    print(f"Reading data from {inpath}.")

    try:
        with open(inpath, "r") as fi:
            try:
                return Corpus.model_validate_json(fi.read())
            except ValidationError:
                _raise(f"Dataset file {inpath} is not a valid OpenDORS data file.")
    except FileNotFoundError:
        _raise(f"Dataset file does not exist: {inpath}.")


def lax_read_corpus(infile: str) -> Corpus | None:
    inpath = Path(infile)
    if not inpath.exists():
        _raise(f"Dataset file does not exist: {inpath}.")
    elif not inpath.is_file():
        _raise(f"Dataset file argument is a directory: {inpath}.")

    try:
        with open(inpath, "r") as fi:
            try:
                return Corpus.model_validate_json(fi.read())
            except ValidationError:
                return None
    except FileNotFoundError:
        return None


def _filter_by_language(
    corpus: Corpus, lang_thresh_dict: dict[str, float | int]
) -> [ResearchSoftware]:
    def check_repository(repository: SourceCodeRepository) -> bool:
        # Return early if there is no record of the latest version
        if repository.latest is None or repository.latest.languages is None:
            return False

        recorded_languages = repository.latest.languages

        # Create a dictionary of languages and their fractions
        rec_language_fractions = {
            language.language: language.fraction for language in recorded_languages
        }

        # Return early if not all required languages for filtering are recorded
        if not all(
            t_lang in rec_language_fractions.keys()
            for t_lang in lang_thresh_dict.keys()
        ):
            return False

        # Return if all recorded languages meet their thresholds (in %, not fraction)
        return all(
            rec_language_fractions.get(language, 0) * 100 >= min_fraction
            for language, min_fraction in lang_thresh_dict.items()
        )

    return [
        filtered_software
        for software in corpus.research_software
        if (
            filtered_software := _filter_software_repositories(
                software, check_repository
            )
        )
        is not None
    ]


def filter_corpus_by_language(corpus: Corpus, lang_thresh_dict: dict) -> Corpus:
    filtered_software = _filter_by_language(corpus, lang_thresh_dict)
    filtered_corpus = Corpus()
    filtered_corpus.research_software = filtered_software
    return filtered_corpus


def write_corpus(outfile: str, filtered_corpus: Corpus, compressed: bool) -> None:
    with open(outfile, "w") as fo:
        fo.write(filtered_corpus.model_dump_json(indent=4 if not compressed else 0))
        print(f"Wrote filtered dataset to {outfile}.")


def apply_language_filters(args: argparse.Namespace, corpus: Corpus) -> Corpus:
    lang_thresh_dict = {}
    if args.language is not None:
        print("Applying language filters.")
        for lang_thresh in args.language[0]:
            lang, thresh = parse_lang_thresh(lang_thresh)
            lang_thresh_dict[lang] = thresh
        total_perc = sum(lang_thresh_dict.values())
        if total_perc > 100.0:
            _raise(f"Total percentage cannot be > 100.0: {total_perc}.")
        return filter_corpus_by_language(corpus, lang_thresh_dict)
    else:
        return corpus


def _determine_date_filters(args: argparse.Namespace) -> (str, bool):
    if args.before is not None:
        return args.before, True
    else:
        return args.after, False


def _filter_software_repositories(
    software: ResearchSoftware, check_repository
) -> ResearchSoftware | None:
    filtered_repositories = [
        repository
        for repository in software.repositories
        if check_repository(repository)
    ]

    if len(filtered_repositories) == 0:
        return None

    # Return a new software with only the filtered repositories
    software.repositories = filtered_repositories
    return software


def _filter_by_date(corpus: Corpus, args):
    def check_repository(repository: SourceCodeRepository) -> bool:
        # Return early if there is no record of the latest version
        if repository.latest is None:
            return False

        before_date = (
            datetime.strptime(args.before, "%Y-%m-%d").timestamp()
            if args.before is not None
            else 953402210800
        )
        after_date = (
            datetime.strptime(args.after, "%Y-%m-%d").timestamp()
            if args.after is not None
            else 0
        )

        date = repository.latest.date.timestamp()

        return after_date < date < before_date

    return [
        filtered_software
        for software in corpus.research_software
        if (
            filtered_software := _filter_software_repositories(
                software, check_repository
            )
        )
        is not None
    ]


def filter_corpus_by_date(args: argparse.Namespace, corpus: Corpus) -> Corpus:
    filtered_software = _filter_by_date(corpus, args)
    filtered_corpus = Corpus()
    filtered_corpus.research_software = filtered_software
    return filtered_corpus


def apply_date_filters(args: argparse.Namespace, corpus: Corpus) -> Corpus:
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if any([args.before, args.after]) is not None:
        if (
            args.before is not None and re.match(date_pattern, args.before) is not None
        ) or (
            args.after is not None and re.match(date_pattern, args.after) is not None
        ):
            print("Applying date filters.")
            return filter_corpus_by_date(args, corpus)
        else:
            print(
                "Given date(s) do(es) not match pattern YYYY-MM-DD, not filtering by date."
            )
            return corpus
    else:
        return corpus


def apply_filters(args):
    corpus = read_corpus(args.infile)

    language_filtered_corpus = apply_language_filters(args, corpus)
    date_filtered_corpus = apply_date_filters(args, language_filtered_corpus)

    date_filtered_corpus.timestamp()
    print(
        "Number of software entries with repositories that matched the filter criteria: "
        f"{len(date_filtered_corpus.research_software)}."
    )
    if args.outfile is not None:
        write_corpus(args.outfile, date_filtered_corpus, args.compressed)
    else:
        if args.compressed:
            sys.stdout.flush()
            print(date_filtered_corpus.model_dump_json())
        else:
            sys.stdout.flush()
            print(date_filtered_corpus.model_dump_json(indent=4))


def print_csv(stats: dict[str, tuple[int, dict[str, int]]]) -> None:
    sys.stdout.flush()
    for sec, tup in stats.items():
        print(sec + "_total," + str(tup[0]))
        for k, v in tup[1].items():
            print(sec + "_" + k.replace(" ", "_") + "," + str(v))


def gather_stats(args):
    stats = {}
    corpus = read_corpus(args.infile)
    software = corpus.research_software
    stats["software"] = (len(software), {})
    repos = with_repos = without_repos = r_with_langs = r_without_langs = r_latest = (
        r_no_latest
    ) = git = svn = other = 0
    for s in software:
        _repos = len(s.repositories)
        repos += _repos
        if _repos == 0:
            without_repos += 1
        else:
            with_repos += 1
        for r in s.repositories:
            if r.vcs == VCS.git:
                git += 1
            elif r.vcs == VCS.svn:
                svn += 1
            else:
                other += 1
            if r.latest is not None:
                r_latest += 1
                if r.latest.languages is not None:
                    r_with_langs += 1
                else:
                    r_without_langs += 1
            else:
                r_no_latest += 1
    stats["software"][1]["with repositories"] = with_repos
    stats["repositories"] = (repos, {})
    stats["repositories"][1]["with latest version"] = r_latest
    stats["repositories"][1]["with language information"] = r_with_langs
    stats["vcs"] = (repos, {"git": git, "svn": svn, "other": other})
    try:
        assert r_with_langs + r_without_langs == r_latest
        assert r_latest + r_no_latest == repos
        assert git + svn + other == repos
    except AssertionError:
        print(
            "::: WARNING! Sanity check failed, some numbers don't add up when they should!"
        )

    if args.csv:
        _line_up = "\033[1A"
        _line_clear = "\x1b[2K"
        print(_line_up, end=_line_clear)
        print_csv(stats)
    else:
        print()
        for cat, tup in stats.items():
            print(f"{cat}: {tup[0]} (total)")
            for k, v in tup[1].items():
                print(" " * (len(cat) + 2) + str(v), k)
            print()


def merge(args):
    inpath = Path(args.infile_directory)
    if not inpath.exists() or not inpath.is_dir():
        _raise(f"{inpath} does not exist or is not a directory.")
    globs = glob.glob(str(inpath / "*.json"), recursive=False)
    if len(globs) == 0:
        _raise(f"No JSON files found in the given directory: {inpath}.")
    corpus = Corpus()
    for i, g in enumerate(globs):
        if i % 100 == 0:
            print(f"Processing file {i} / {len(globs)}.", end="\r")
        in_corpus = lax_read_corpus(g)
        if in_corpus is not None:
            for s in in_corpus.research_software:
                corpus.add_software(s)
    print(f"\nWriting merged corpus: {args.outfile}.")
    with open(args.outfile, "w") as fo:
        if args.compressed:
            fo.write(corpus.model_dump_json())
        else:
            fo.write(corpus.model_dump_json(indent=4))


class ODLParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help()
        sys.exit(2)


def parse_schema(subparsers):
    # Create parser for "schema" command
    parser_schema = subparsers.add_parser(
        "schema",
        help="Exports the JSON schema for the opendors model to 'schema.json'.",
    )
    parser_schema.set_defaults(func=export_schema)


def parse_filter(subparsers):
    # Create parser for "filter" command
    parser_filter = subparsers.add_parser(
        "filter",
        help="Filters a given dataset by programming language and/or before/after dates.",
    )
    parser_filter.add_argument(
        "-l",
        "--language",
        metavar="LANGUAGE=PERCENTAGE",
        help="Languages to filter, optional: percentage threshold above which to include record "
        "(example: '-l Rust Python=20 Java=23.42')",
        action="append",
        nargs="+",
    )
    parser_filter.add_argument(
        "-o",
        "--outfile",
        metavar="OUTFILE",
        help="File to write filtered dataset to, prints to stdout if not provided",
        required=False,
    )
    parser_filter.add_argument(
        "-i",
        "--infile",
        help="Dataset file (JSON) to filter from",
        metavar="INFILE",
        required=True,
    )
    parser_filter.add_argument(
        "-a",
        "--after",
        metavar="YYYY-MM-DD",
        help="Date, repositories with latest versions after which should be included in the dataset",
    )
    parser_filter.add_argument(
        "-b",
        "--before",
        metavar="YYYY-MM-DD",
        help="Date, repositories with latest versions before which should be included in the dataset",
    )
    parser_filter.set_defaults(func=apply_filters)


def parse_stats(subparsers):
    # Create parser for "stats" command
    parser_filter = subparsers.add_parser(
        "stats",
        help="Gather statistics on a given OpenDORS dataset.",
    )
    parser_filter.add_argument(
        "-i",
        "--infile",
        help="Dataset file (JSON) to analyze",
        metavar="INFILE",
        required=True,
    )
    parser_filter.add_argument(
        "--csv",
        help="Output as CSV",
        action="store_true",
        default=False,
    )
    parser_filter.set_defaults(func=gather_stats)


def parse_merge(subparsers):
    # Create parser for "merge" command
    parser_filter = subparsers.add_parser(
        "merge",
        help="Merge OpenDORS datasets into a single file.",
    )
    parser_filter.add_argument(
        "-d",
        "--infile-directory",
        help="Directory containing the OpenDORS dataset files (JSON) to merge",
        metavar="INDIR",
        required=True,
    )
    parser_filter.add_argument(
        "-o",
        "--outfile",
        help="Dataset file to write",
        metavar="OUTFILE",
        required=True,
    )
    parser_filter.set_defaults(func=merge)


def parse_args(sys_args: list[str]) -> (ODLParser, argparse.Namespace):
    # Create the "parent" parser
    parser = ODLParser(description="Utilities to work with OpenDORS datasets.")
    parser.add_argument(
        "-c",
        "--compressed",
        help="Export as unindented JSON",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print tracebacks on error",
        action="store_true",
        default=False,
    )

    subparsers = parser.add_subparsers(help="Available commands", required=True)

    parse_schema(subparsers)
    parse_filter(subparsers)
    parse_stats(subparsers)
    parse_merge(subparsers)

    args = parser.parse_args(sys_args)

    return parser, args


def run():
    """
    A simple CLI to interact with the opendors package and model.
    """
    parser, args = parse_args(sys.argv[1:])

    if not args.verbose:
        sys.tracebacklimit = 0

    if args.__contains__("func"):
        args.func(args)
    else:
        parser.print_help()
