#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import subprocess
import shutil
import sys


def detect_tool(name):
    path = shutil.which(name)
    return {"available": path is not None, "path": path}


def detect_html_open():
    if sys.platform.startswith("win"):
        return {
            "available": True,
            "strategy": "os.startfile",
            "command": None,
            "path": None,
            "argv_prefix": [],
        }

    candidates = [("open", [])] if sys.platform == "darwin" else [
        ("xdg-open", []),
        ("gio", ["open"]),
    ]
    for name, args in candidates:
        path = shutil.which(name)
        if path:
            return {
                "available": True,
                "strategy": "argv",
                "command": name,
                "path": path,
                "argv_prefix": [path, *args],
            }

    return {
        "available": False,
        "strategy": None,
        "command": None,
        "path": None,
        "argv_prefix": [],
    }


def build_report():
    return {
        "python": {
            "available": True,
            "executable": sys.executable,
            "version": sys.version.split()[0],
        },
        "pdf_text_extraction": detect_tool("pdftotext"),
        "pdf_page_rendering": detect_tool("pdftoppm"),
        "html_open": detect_html_open(),
    }


def check_release():
    # A process deadline also bounds slow DNS and stalled response bodies.
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().with_name("check_updates.py"))],
            capture_output=True, text=True, timeout=5, check=True,
        )
        report = json.loads(result.stdout)
        if not isinstance(report, dict) or report.get("status") not in {
            "up_to_date", "update_available", "local_ahead", "unavailable", "skipped"
        }:
            raise ValueError("Invalid update report")
        return report
    except (OSError, subprocess.SubprocessError, ValueError):
        return {"status": "unavailable", "reason": "checker_failed_or_timed_out"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-updates", action="store_true",
                        help="Read-only GitHub release check; bounded and non-blocking on failure")
    args = parser.parse_args()
    report = build_report()
    if args.check_updates:
        report["update_check"] = check_release()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
