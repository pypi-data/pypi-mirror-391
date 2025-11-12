#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List, Dict, Set

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


"""
QuickCoach data scraper.

Extracts workout history from QuickCoach's React/MUI web application.

The scraper works by:
1. Opening the QuickCoach client page with Selenium to render JavaScript
2. Discovering plan URLs by clicking on plan cards in the rendered DOM
3. For each plan, extracting exercises using JavaScript DOM queries
4. Clicking "Last:" links to open history modals
5. Parsing exercise history from modal text content
6. Writing results to long-format and pivoted CSV files
"""


@dataclass
class ExerciseRow:
    plan_title: str
    exercise_name: str
    date: str
    result: str


# ----------------- helpers -----------------


def parse_date_to_iso(date_str: str) -> str:
    """
    Convert date from format like 'Nov 6th 2025' to '2025-11-06'.
    Returns empty string if parsing fails.
    """
    if not date_str:
        return ""

    try:
        # Remove ordinal suffixes (st, nd, rd, th)
        date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)

        # Parse the date
        from datetime import datetime

        dt = datetime.strptime(date_str, "%b %d %Y")

        # Return in YYYY-MM-DD format
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""


def unique(seq: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def sanitize_filename(slug: str) -> str:
    """
    Sanitize a slug to be safe for use in filenames.
    Replace invalid filename characters with underscores.
    """
    # Invalid characters in filenames: / \ : * ? " < > | and spaces
    invalid_chars = r'[/\\:*?"<>|\s]'
    return re.sub(invalid_chars, "_", slug)


def parse_exercises_from_plan(driver) -> List[Dict[str, str]]:
    """
    Extract exercises from the rendered plan page using JavaScript.
    QuickCoach uses React/MUI, so we need to parse the rendered DOM, not raw HTML.

    Returns exercises with their associated "Last:" link indices. This ensures
    each exercise is correctly matched to its history link, especially in supersets.
    """
    extract_script = """
    const exercises = [];
    const allDivs = document.querySelectorAll('div');

    allDivs.forEach(div => {
        const text = div.innerText || '';

        // Look for divs containing both "Reps:" and "Last:"
        if (text.includes('Reps:') && text.includes('Last:') && text.length < 300) {
            // Extract exercise name (text before "Reps:")
            const lines = text.split('\\n');
            let name = '';
            let reps = '';
            let last = '';

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();

                if (line === 'Reps:' && i > 0) {
                    // The line before "Reps:" is likely the exercise name
                    name = lines[i - 1].trim();
                }
                else if (line === 'Reps:' && i + 1 < lines.length) {
                    // The line after "Reps:" is the rep scheme
                    reps = lines[i + 1].trim();
                }
                else if (line === 'Last:' && i + 1 < lines.length) {
                    // The line after "Last:" is the last result
                    last = lines[i + 1].trim();
                }
            }

            // Find the "Last:" link within this div's subtree
            // For supersets, we need to be more careful about which link belongs to which exercise
            let lastLinkIndex = -1;
            const lastSpans = div.querySelectorAll('span.MuiTypography-link');

            // Try to find the link whose surrounding text contains this exercise name
            // and is the smallest/most specific container
            let bestMatch = null;
            let bestMatchSize = Infinity;

            for (let span of lastSpans) {
                if (span.innerText === 'Last:') {
                    // Walk up the DOM tree to find a container that mentions this exercise
                    let currentParent = span.parentElement;
                    let foundAtLevel = -1;

                    for (let level = 0; level < 10 && currentParent; level++) {
                        const parentText = currentParent.innerText || '';

                        // Check if this container has our exercise name
                        if (parentText.includes(name)) {
                            const textSize = parentText.length;

                            // Prefer smaller containers (more specific match)
                            if (textSize < bestMatchSize) {
                                bestMatchSize = textSize;
                                bestMatch = span;
                                foundAtLevel = level;
                            }
                            break;
                        }

                        currentParent = currentParent.parentElement;
                    }
                }
            }

            if (bestMatch) {
                // Find the global index of this span among all "Last:" links
                const allLastLinks = document.querySelectorAll('span.MuiTypography-link');
                for (let i = 0; i < allLastLinks.length; i++) {
                    if (allLastLinks[i] === bestMatch && allLastLinks[i].innerText === 'Last:') {
                        lastLinkIndex = i;
                        break;
                    }
                }
            }

            // Only add if we have a name and found a link
            if (name && name !== 'Reps:' && name !== 'Last:' && lastLinkIndex >= 0) {
                exercises.push({
                    name: name,
                    reps: reps,
                    last: last,
                    lastLinkIndex: lastLinkIndex
                });
            }
        }
    });

    // Deduplicate by name (take the first occurrence of each)
    const seen = new Set();
    const unique = [];
    for (const ex of exercises) {
        if (!seen.has(ex.name)) {
            seen.add(ex.name);
            unique.push(ex);
        }
    }

    return unique;
    """

    exercises = driver.execute_script(extract_script)

    # Convert to the expected format
    blocks = []
    for ex in exercises:
        blocks.append(
            {
                "exercise_name": ex["name"],
                "last": ex["last"],
                "last_link_index": ex["lastLinkIndex"],
            }
        )

    return blocks


def extract_history_from_modal(driver) -> List[dict]:
    """
    Extract exercise history from the "Past Performance" modal.
    Returns a list of history entries with date, status, and result.
    """
    time.sleep(1.5)  # Wait for modal to load

    # Check if modal is present
    modal_present = driver.execute_script(
        "return document.querySelector('[role=\"dialog\"]') !== null;"
    )
    if not modal_present:
        print("        [DEBUG] No modal found with [role='dialog']")
        return []

    extract_script = """
    const entries = [];
    const modal = document.querySelector('[role="dialog"]');

    if (!modal) {
        return [];
    }

    const text = modal.innerText || '';
    const lines = text.split('\\n').map(l => l.trim()).filter(l => l); // Remove empty lines

    let i = 0;
    while (i < lines.length) {
        const line = lines[i];

        // Skip header lines
        if (line === 'Past Performance' || line === 'Hide empty') {
            i++;
            continue;
        }

        // Check if this is a status line (Current/Completed)
        if (line === 'Current' || line === 'Completed') {
            // Pattern: [Plan name] [Status] [Date] [Result:] [Result value]
            // We're at Status, so plan name is i-1
            if (i >= 1 && i + 3 < lines.length) {
                const planName = lines[i - 1];
                const status = line;
                const date = lines[i + 1];
                const resultLabel = lines[i + 2];
                const result = lines[i + 3];

                if (resultLabel === 'Result:') {
                    entries.push({
                        planName: planName,
                        status: status,
                        date: date,
                        result: result
                    });

                    i += 4; // Skip to next entry
                    continue;
                }
            }
        }
        i++;
    }

    return entries;
    """

    try:
        history = driver.execute_script(extract_script)
        return history
    except Exception as e:
        print(f"        Error extracting modal history: {e}")
        return []


def close_modal(driver):
    """Close the Past Performance modal by clicking the backdrop"""
    try:
        # Click on the backdrop to close the modal
        driver.execute_script("""
            const backdrop = document.querySelector('.MuiBackdrop-root');
            if (backdrop) {
                backdrop.click();
            }
        """)
        time.sleep(0.8)

        # Verify modal is closed
        modal_closed = driver.execute_script(
            "return document.querySelector('[role=\"dialog\"]') === null;"
        )
        if not modal_closed:
            # Try Escape key as fallback
            driver.execute_script("""
                const event = new KeyboardEvent('keydown', { key: 'Escape', keyCode: 27 });
                document.dispatchEvent(event);
            """)
            time.sleep(0.5)
    except Exception as e:
        print(f"        [DEBUG] Error closing modal: {e}")


def discover_plan_urls(driver, base: str) -> List[str]:
    """
    QuickCoach uses React with MUI components. Plan cards are MuiStack-root divs
    that navigate via JavaScript when clicked (not traditional <a> tags).
    We need to:
    1. Find all plan names from the page text
    2. Click on each plan card to navigate and capture the URL
    3. Return to the main page and repeat for all plans
    """
    urls: List[str] = []
    main_url = driver.current_url

    # Give JS time to render
    time.sleep(2.0)

    # Use JavaScript to extract all plan names from the page
    extract_plan_names_script = """
    const planNames = new Set();
    const allDivs = document.querySelectorAll('div.MuiStack-root');

    allDivs.forEach(div => {
        const text = div.innerText || '';
        // Look for divs with plan names - they typically have name + date
        // and are relatively small (20-100 chars)
        if (text.includes('plan') && text.length > 20 && text.length < 150) {
            // Extract just the plan name (first line, typically)
            const lines = text.split('\\n');
            if (lines.length > 0 && lines[0].toLowerCase().includes('plan')) {
                planNames.add(lines[0].trim());
            }
        }
    });

    return Array.from(planNames);
    """

    plan_names = driver.execute_script(extract_plan_names_script)
    print(f"Found {len(plan_names)} plan(s): {plan_names}")

    # For each plan name, click on it to get the URL
    for plan_name in plan_names:
        try:
            # Navigate back to main page if not already there
            if driver.current_url != main_url:
                driver.get(main_url)
                time.sleep(2.0)

            # Click on the plan card using JavaScript
            click_script = f"""
            const allDivs = document.querySelectorAll('div.MuiStack-root');
            for (let div of allDivs) {{
                const text = div.innerText || '';
                // Match the plan name
                if (text.includes('{plan_name}') && text.length > 20 && text.length < 150) {{
                    div.click();
                    return true;
                }}
            }}
            return false;
            """

            clicked = driver.execute_script(click_script)
            if clicked:
                # Wait for navigation
                time.sleep(2.0)
                plan_url = driver.current_url

                if "/plan/" in plan_url:
                    urls.append(plan_url)
                    print(f"  ✓ {plan_name} → {plan_url}")
                else:
                    print(f"  ✗ {plan_name} - navigation failed")
            else:
                print(f"  ✗ {plan_name} - click failed")

        except Exception as e:
            print(f"  ✗ {plan_name} - error: {e}")

    return unique(urls)


def generate_pivoted_csv(input_csv: str, output_csv: str) -> None:
    """
    Generate a pivoted (wide format) CSV from the regular (long format) CSV.
    Exercises become rows, dates become columns.
    """
    # Data structure: { exercise_name: { date: result } }
    exercise_data: Dict[str, Dict[str, str]] = defaultdict(dict)
    all_dates: Set[str] = set()

    # Read input CSV
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exercise_name = row["exercise_name"]
            date = row["date"]
            result = row["result"]

            # Skip rows without dates
            if not date:
                continue

            exercise_data[exercise_name][date] = result
            all_dates.add(date)

    # Sort dates chronologically (most recent first)
    sorted_dates = sorted(all_dates, reverse=True)

    # Sort exercises alphabetically
    sorted_exercises = sorted(exercise_data.keys())

    # Write output CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header: exercise_name, date1, date2, ...
        writer.writerow(["exercise_name"] + sorted_dates)

        # Write data rows
        for exercise in sorted_exercises:
            row = [exercise]
            for date in sorted_dates:
                # Get result for this exercise on this date (empty if not present)
                result = exercise_data[exercise].get(date, "")
                row.append(result)
            writer.writerow(row)

    print(f"Wrote pivoted CSV -> {output_csv}")
    print(f"  Exercises: {len(sorted_exercises)}")
    print(f"  Dates: {len(sorted_dates)}")


# ----------------- scraping orchestration -----------------


def run_export(
    client_url: str,
    output_csv: str,
    pivoted_csv: str,
    delay: float = 0.15,
    headful: bool = False,
    skip_pivot: bool = False,
) -> None:
    """
    Run the QuickCoach export scraper.

    Args:
        client_url: Full URL to the QuickCoach client page
        output_csv: Path to output CSV file
        pivoted_csv: Path to pivoted CSV file
        delay: Delay between history calls in seconds
        headful: Show browser window if True
        skip_pivot: Skip generating pivoted CSV if True
    """
    chrome_opts = Options()
    if not headful:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_opts)

    try:
        print(f"Opening {client_url}")
        driver.get(client_url)

        # Wait for React app to render - look for MuiStack components
        try:
            WebDriverWait(driver, 15).until(
                lambda d: (
                    "Previous Plans" in d.page_source
                    or bool(d.find_elements(By.CSS_SELECTOR, "div.MuiStack-root"))
                )
            )
        except TimeoutException:
            print(
                "Timed out waiting for plans to load. Is the URL correct and showing your plans?",
                file=sys.stderr,
            )
            return

        # Extract base URL from client_url for plan discovery
        base = client_url.rstrip("/").rsplit("/", 1)[0]

        plan_urls = discover_plan_urls(driver, base)
        if not plan_urls:
            print(
                "No plan URLs found. The script looks for MuiStack-root divs containing plan names. "
                "If you're seeing plans in the browser but they're not being detected, "
                "the page structure may have changed. Try running with --headful to debug.",
                file=sys.stderr,
            )
            return

        print(f"Discovered {len(plan_urls)} plan URL(s).")

        rows: List[ExerciseRow] = []

        for i, plan_url in enumerate(plan_urls, 1):
            print(f"[{i}/{len(plan_urls)}] Loading plan page: {plan_url}")
            driver.get(plan_url)
            time.sleep(2.0)  # let page render

            # Extract data from rendered page
            plan_title = (
                driver.execute_script("return document.body.innerText.split('\\n')[0]")
                or "Plan"
            )

            exercises = parse_exercises_from_plan(driver)

            if not exercises:
                print(
                    f"  !! No exercises found in {plan_title}",
                    file=sys.stderr,
                )
            else:
                print(f"  Found {len(exercises)} exercise(s) in {plan_title}")

            for idx, ex in enumerate(exercises):
                name = ex["exercise_name"]
                last = ex["last"]
                last_link_index = ex["last_link_index"]

                # Try to click on the correct "Last:" link using the index we found during parsing
                try:
                    # Click the specific "Last:" link that corresponds to this exercise
                    click_last_script = f"""
                    const spans = document.querySelectorAll('span.MuiTypography-link');
                    let count = 0;
                    for (let span of spans) {{
                        if (span.innerText === 'Last:') {{
                            if (count === {last_link_index}) {{
                                span.click();
                                return true;
                            }}
                            count++;
                        }}
                    }}
                    return false;
                    """

                    clicked = driver.execute_script(click_last_script)

                    if clicked:
                        # Extract history from modal
                        hist_items = extract_history_from_modal(driver)

                        if hist_items:
                            print(f"    {name}: {len(hist_items)} history entries")

                            for h in hist_items:
                                rows.append(
                                    ExerciseRow(
                                        plan_title=h.get("planName", plan_title),
                                        exercise_name=name,
                                        date=parse_date_to_iso(h.get("date", "")),
                                        result=h.get("result", ""),
                                    )
                                )
                        else:
                            # No history found, just add the current "Last:" value
                            rows.append(
                                ExerciseRow(
                                    plan_title=plan_title,
                                    exercise_name=name,
                                    date="",
                                    result=last,
                                )
                            )

                        # Close modal
                        close_modal(driver)
                    else:
                        # Click failed, just add the current "Last:" value
                        rows.append(
                            ExerciseRow(
                                plan_title=plan_title,
                                exercise_name=name,
                                date="",
                                result=last,
                            )
                        )

                except Exception as e:
                    print(f"    Error getting history for {name}: {e}")
                    # Fallback: add the current "Last:" value
                    rows.append(
                        ExerciseRow(
                            plan_title=plan_title,
                            exercise_name=name,
                            date="",
                            result=last,
                        )
                    )

                if delay:
                    time.sleep(delay)

        # Write CSV
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "plan_title",
                    "exercise_name",
                    "date",
                    "result",
                ]
            )
            for r in rows:
                w.writerow(
                    [
                        r.plan_title,
                        r.exercise_name,
                        r.date,
                        r.result,
                    ]
                )

        print(f"Wrote {len(rows)} rows -> {output_csv}")

        # Generate pivoted CSV unless --skip-pivot was specified
        if not skip_pivot:
            try:
                generate_pivoted_csv(output_csv, pivoted_csv)
            except Exception as e:
                print(f"Warning: Could not generate pivoted CSV: {e}", file=sys.stderr)

    finally:
        driver.quit()
