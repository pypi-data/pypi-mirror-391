#!/usr/bin/env python3
"""Render episode cards for a JSONL split."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import matplotlib

# Force a non-interactive backend so the script runs in headless environments.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  # pylint: disable=wrong-import-position

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cellarc.visualization import show_episode_card
from scripts.plots._episode_utils import (
    filter_records,
    load_jsonl,
    load_meta_lookup,
    merge_metadata,
    select_records,
)


def render_cards(
    records: Iterable[dict],
    *,
    output_dir: Path,
    prefix: str,
    rng: random.Random,
    tau_max: Optional[int] = None,
    show_metadata: bool = False,
    metadata_fields: Optional[Sequence[str]] = None,
) -> None:
    """Render and save episode cards."""

    metadata_flag = show_metadata or bool(metadata_fields)
    output_dir.mkdir(parents=True, exist_ok=True)
    for idx, record in enumerate(records):
        fig = show_episode_card(
            record,
            rng_seed=rng.randint(0, 2**31 - 1),
            tau_max=tau_max,
            show_metadata=metadata_flag,
            metadata_fields=metadata_fields,
        )
        fingerprint = (
            record.get("meta", {}).get("fingerprint")
            or record.get("fingerprint")
            or "record"
        )
        suffix = str(fingerprint)[:10]
        filename = f"{prefix}_{idx:02d}_{suffix}.png"
        fig.savefig(output_dir / filename, dpi=200)
        plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the JSONL split file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write the episode card images to.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of records to sample (default: 20).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed used for sampling (default: 0).",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="Filename prefix (defaults to input stem).",
    )
    parser.add_argument(
        "--meta",
        type=Path,
        default=None,
        help="Optional path to companion metadata JSONL file.",
    )
    parser.add_argument(
        "--split",
        dest="splits",
        nargs="+",
        default=None,
        help="Filter to episodes whose split matches any of the provided names.",
    )
    parser.add_argument(
        "--family",
        dest="families",
        nargs="+",
        default=None,
        help="Filter to CA families (case-insensitive).",
    )
    parser.add_argument(
        "--alphabet-size",
        dest="alphabet_sizes",
        type=int,
        nargs="+",
        default=None,
        help="Filter to automata with the given alphabet sizes.",
    )
    parser.add_argument(
        "--lambda-min",
        "--lambda-threshold",
        dest="lambda_min",
        type=float,
        default=None,
        help="Minimum lambda value (inclusive).",
    )
    parser.add_argument(
        "--lambda-max",
        dest="lambda_max",
        type=float,
        default=None,
        help="Maximum lambda value (inclusive).",
    )
    parser.add_argument(
        "--tau-max",
        type=int,
        default=None,
        help="Maximum rollout depth passed to the renderer.",
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Render a metadata footer below each card.",
    )
    parser.add_argument(
        "--metadata-fields",
        nargs="+",
        default=None,
        help="Explicit list of metadata keys to display in the footer.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    records = load_jsonl(args.input)
    if not records:
        raise ValueError(f"No records found in {args.input}")

    meta_path = args.meta
    if meta_path is None:
        candidate = args.input.with_name(f"{args.input.stem}_meta.jsonl")
        if candidate.exists():
            meta_path = candidate
    if meta_path is not None:
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")
        meta_lookup = load_meta_lookup(meta_path)
        merge_metadata(records, meta_lookup)

    default_split = args.input.stem
    for record in records:
        record.setdefault("split", default_split)
        meta = record.get("meta")
        if isinstance(meta, dict):
            meta.setdefault("split", default_split)

    filtered = filter_records(
        records,
        splits=args.splits,
        families=args.families,
        alphabet_sizes=args.alphabet_sizes,
        lambda_min=args.lambda_min,
        lambda_max=args.lambda_max,
    )
    if not filtered:
        raise ValueError("No records matched the provided filters.")
    if len(filtered) < len(records):
        print(f"[plot_episode_cards] Filtered {len(filtered)} / {len(records)} episodes.", flush=True)

    selected = list(select_records(filtered, args.count, rng))
    prefix = args.prefix or args.input.stem
    render_cards(
        selected,
        output_dir=args.output_dir,
        prefix=prefix,
        rng=rng,
        tau_max=args.tau_max,
        show_metadata=args.include_metadata,
        metadata_fields=args.metadata_fields,
    )


if __name__ == "__main__":
    main()
