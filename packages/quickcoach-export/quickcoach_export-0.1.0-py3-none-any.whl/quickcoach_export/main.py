#!/usr/bin/env python3
"""CLI entry point for quickcoach-export."""

import argparse

from quickcoach_export.quickcoach_scrape import run_export, sanitize_filename


def main() -> None:
    """Parse arguments and run the QuickCoach export."""
    ap = argparse.ArgumentParser(
        description="Export ALL QuickCoach exercise history to CSV. "
        "Outputs quickcoach-{slug}.csv and quickcoach-pivot-{slug}.csv"
    )
    ap.add_argument(
        "--base",
        default="https://app.quickcoach.fit",
        help="Base URL (default: https://app.quickcoach.fit)",
    )
    ap.add_argument(
        "--slug",
        required=True,
        help="Client path, e.g. 'pt/fitcojoseph123'. Output files will be named based on this.",
    )
    ap.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="Delay between history calls (seconds)",
    )
    ap.add_argument(
        "--headful",
        action="store_true",
        help="Run with visible Chrome window (useful to confirm selectors).",
    )
    ap.add_argument(
        "--skip-pivot",
        action="store_true",
        help="Skip generating the pivoted CSV (only output the regular long-format CSV).",
    )
    args = ap.parse_args()

    base = args.base.rstrip("/")
    slug = args.slug.strip("/")
    client_url = f"{base}/{slug}/"

    # Generate output filenames from slug
    sanitized_slug = sanitize_filename(slug)
    output_csv = f"quickcoach-{sanitized_slug}.csv"
    pivoted_csv = f"quickcoach-pivot-{sanitized_slug}.csv"

    run_export(
        client_url=client_url,
        output_csv=output_csv,
        pivoted_csv=pivoted_csv,
        delay=args.delay,
        headful=args.headful,
        skip_pivot=args.skip_pivot,
    )


if __name__ == "__main__":
    main()
