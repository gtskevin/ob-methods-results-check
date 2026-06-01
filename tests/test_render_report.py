import importlib.util
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "render_report.py"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-report.md"
SPEC = importlib.util.spec_from_file_location("render_report", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RenderReportTests(unittest.TestCase):
    def make_symlink_or_skip(self, link, target):
        try:
            link.symlink_to(target)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"symlinks unsupported: {exc}")

    def test_render_markdown_supports_report_syntax_and_unicode(self):
        rendered = MODULE.render_markdown(FIXTURE.read_text(encoding="utf-8"))

        self.assertIn("<h1>Audit &lt;Draft&gt;</h1>", rendered)
        self.assertIn("<h2>Findings</h2>", rendered)
        self.assertIn("<ol><li>First issue</li><li>Second issue</li></ol>", rendered)
        self.assertIn("<ul><li><code>P0</code>: core conclusion</li>", rendered)
        self.assertIn("<table>", rendered)
        self.assertIn("<blockquote>", rendered)
        self.assertIn("<strong>状态：</strong> 待评审", rendered)
        self.assertIn('class="glossary"', rendered)

    def test_render_markdown_escapes_raw_html(self):
        rendered = MODULE.render_markdown('<script>alert("raw")</script>')

        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertNotIn("<script>", rendered)

    def test_render_markdown_escapes_code_fence_html(self):
        rendered = MODULE.render_markdown('```html\n<script>alert("code")</script>\n```')

        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertNotIn("<script>", rendered)

    def test_render_inline_activates_https_link(self):
        rendered = MODULE.render_inline("[Agent Skills](https://agentskills.io/specification)")

        self.assertEqual(
            rendered,
            '<a href="https://agentskills.io/specification">Agent Skills</a>',
        )

    def test_render_inline_activates_https_link_with_encoded_separator(self):
        rendered = MODULE.render_inline("[report](https://example.com/a%2Fb)")

        self.assertEqual(
            rendered,
            '<a href="https://example.com/a%2Fb">report</a>',
        )

    def test_render_inline_activates_http_link_and_escapes_query(self):
        rendered = MODULE.render_inline("[report](http://example.com/report?a=1&b=2)")

        self.assertEqual(
            rendered,
            '<a href="http://example.com/report?a=1&amp;b=2">report</a>',
        )

    def test_render_inline_activates_allowed_local_links(self):
        for target in ("#finding", "/tmp/report.html", "./report.html", "../report.html"):
            with self.subTest(target=target):
                rendered = MODULE.render_inline(f"[report]({target})")
                self.assertEqual(rendered, f'<a href="{target}">report</a>')

    def test_render_inline_rejects_local_links_with_encoded_or_backslash_separators(self):
        for target in (
            r"/\example.com/share",
            "/%2fexample.com/share",
            "./%5Cexample.com/share",
            "../%2F/example.com/share",
        ):
            with self.subTest(target=target):
                rendered = MODULE.render_inline(f"[unsafe]({target})")
                self.assertNotIn("<a ", rendered)
                self.assertNotIn("href=", rendered)

    def test_render_inline_leaves_unsafe_links_inert(self):
        for target in (
            'javascript:alert("not executable")',
            "data:text/html,unsafe",
            "file:///tmp/report.html",
            "//example.com/share",
        ):
            with self.subTest(target=target):
                rendered = MODULE.render_inline(f"[unsafe]({target})")
                self.assertNotIn("<a ", rendered)
                self.assertNotIn("href=", rendered)
                self.assertIn("[unsafe]", rendered)

    def test_render_inline_restores_many_placeholders(self):
        rendered = MODULE.render_inline(" ".join(f"`item-{index}`" for index in range(2000)))

        self.assertEqual(rendered.count("<code>"), 2000)
        self.assertIn("<code>item-1999</code>", rendered)

    def test_render_inline_handles_long_crafted_token_like_text(self):
        crafted = "\x00MDTOKEN" + "_" * 20000 + '<script>alert("raw")</script>'

        started = time.monotonic()
        rendered = MODULE.render_inline(crafted)
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 1.0)
        self.assertNotIn("\x00", rendered)
        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertNotIn("<script>", rendered)

    def test_render_markdown_limits_quote_nesting_depth(self):
        rendered = MODULE.render_markdown(
            "> " * 1200 + '<script>alert("deep quote")</script>'
        )

        self.assertLessEqual(rendered.count("<blockquote>"), MODULE.MAX_QUOTE_DEPTH)
        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertNotIn("<script>", rendered)

    def test_choose_output_path_avoids_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            requested = Path(tmp) / "report.html"
            requested.write_text("existing", encoding="utf-8")

            chosen = MODULE.choose_output_path(
                requested,
                overwrite=False,
                timestamp="20260601-120000",
            )

            self.assertEqual(chosen.name, "report-20260601-120000.html")

    def test_choose_output_path_uses_version_suffix_when_timestamp_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            requested = Path(tmp) / "report.html"
            requested.write_text("existing", encoding="utf-8")
            (Path(tmp) / "report-20260601-120000.html").write_text(
                "existing",
                encoding="utf-8",
            )

            chosen = MODULE.choose_output_path(
                requested,
                overwrite=False,
                timestamp="20260601-120000",
            )

            self.assertEqual(chosen.name, "report-20260601-120000-2.html")

    def test_choose_output_path_allows_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            requested = Path(tmp) / "report.html"
            requested.write_text("existing", encoding="utf-8")

            self.assertEqual(
                MODULE.choose_output_path(requested, overwrite=True),
                requested,
            )

    def test_choose_output_path_bounds_hostile_collisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            requested = Path(tmp) / "report.html"
            attempts = 0

            def always_exists(_path):
                nonlocal attempts
                attempts += 1
                if attempts > 110:
                    raise AssertionError("output path search was not bounded")
                return True

            with patch.object(MODULE.os.path, "lexists", side_effect=always_exists):
                with self.assertRaisesRegex(FileExistsError, "after .* attempts"):
                    MODULE.choose_output_path(requested, overwrite=False)

    def test_open_failure_preserves_generated_html_and_returns_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            with patch.object(
                MODULE.webbrowser,
                "open",
                side_effect=RuntimeError("no browser"),
            ):
                result = MODULE.write_html(
                    FIXTURE,
                    output,
                    overwrite=False,
                    open_browser=True,
                )

            self.assertEqual(result, output)
            self.assertTrue(output.exists())
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))

    def test_open_false_preserves_generated_html_and_returns_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            with patch.object(MODULE.webbrowser, "open", return_value=False):
                result = MODULE.write_html(
                    FIXTURE,
                    output,
                    overwrite=False,
                    open_browser=True,
                )

            self.assertEqual(result, output)
            self.assertTrue(output.exists())
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))

    def test_write_html_retries_if_destination_appears_before_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            original_choose_output_path = MODULE.choose_output_path
            raced = False

            def choose_output_path_with_race(*args, **kwargs):
                nonlocal raced
                destination = original_choose_output_path(*args, **kwargs)
                if not raced:
                    destination.write_text("raced", encoding="utf-8")
                    raced = True
                return destination

            with patch.object(
                MODULE,
                "choose_output_path",
                side_effect=choose_output_path_with_race,
            ):
                result = MODULE.write_html(FIXTURE, output, overwrite=False)

            self.assertEqual(output.read_text(encoding="utf-8"), "raced")
            self.assertNotEqual(result, output)
            self.assertIn("<!doctype html>", result.read_text(encoding="utf-8"))

    def test_write_html_bounds_retries_if_destinations_keep_appearing(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            output.write_text("raced", encoding="utf-8")
            attempts = 0

            def choose_existing_output(*_args, **_kwargs):
                nonlocal attempts
                attempts += 1
                if attempts > 110:
                    raise AssertionError("exclusive creation retry loop was not bounded")
                return output

            with patch.object(
                MODULE,
                "choose_output_path",
                side_effect=choose_existing_output,
            ):
                with self.assertRaisesRegex(FileExistsError, "after .* attempts"):
                    MODULE.write_html(FIXTURE, output, overwrite=False)

    def test_write_html_refuses_dangling_symlink_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "missing-target.html"
            output = Path(tmp) / "report.html"
            self.make_symlink_or_skip(output, target)

            with self.assertRaisesRegex(FileExistsError, "symlink"):
                MODULE.write_html(FIXTURE, output, overwrite=False)

            self.assertFalse(target.exists())

    def test_write_html_overwrite_replaces_symlink_without_touching_victim(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "victim.html"
            target.write_text("victim content", encoding="utf-8")
            output = Path(tmp) / "report.html"
            self.make_symlink_or_skip(output, target)

            result = MODULE.write_html(FIXTURE, output, overwrite=True)

            self.assertEqual(result, output)
            self.assertEqual(target.read_text(encoding="utf-8"), "victim content")
            self.assertFalse(output.is_symlink())
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8"))

    def test_write_html_overwrite_cleans_temp_file_if_replace_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"

            with patch.object(MODULE.os, "replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    MODULE.write_html(FIXTURE, output, overwrite=True)

            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_write_html_creates_standalone_reading_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "report.html"

            result = MODULE.write_html(FIXTURE, output)
            document = result.read_text(encoding="utf-8")

            self.assertIn("<!doctype html>", document)
            self.assertIn("<style>", document)
            self.assertIn("<h1>Audit &lt;Draft&gt;</h1>", document)
            self.assertNotIn("<script>alert", document)

    def test_cli_generates_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.html"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(FIXTURE), "--output", str(output)],
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertTrue(output.exists())
            self.assertIn(str(output), result.stdout)

    def test_missing_source_returns_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "/missing/report.md"],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Markdown source not found", result.stderr)

    def test_malformed_utf8_source_returns_concise_cli_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "malformed.md"
            source.write_bytes(b"# malformed\n\xff")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Markdown source is not valid UTF-8", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
