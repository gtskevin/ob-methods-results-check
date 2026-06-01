#!/usr/bin/env python3
import json
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


def main():
    print(json.dumps(build_report(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
