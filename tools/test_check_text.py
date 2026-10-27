import tempfile
import unittest
from pathlib import Path

import check_text

EN_DASH, EM_DASH = chr(0x2013), chr(0x2014)


class CheckTextTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.root = Path(self._dir.name)
        self.write("README.md", "# Product\n\nWhat it is.\n")
        self.write("AGENTS.md", "# Product\n" + "line\n" * 9)
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.write("docs/README.md", "# Docs\n")

    def tearDown(self):
        self._dir.cleanup()

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(text.encode("utf-8"))

    def rules(self):
        return [f.rule for f in check_text.check(self.root)]

    def test_clean_repo_passes(self):
        self.assertEqual(check_text.check(self.root), [])
        self.assertEqual(check_text.main([str(self.root)]), 0)

    def test_unlisted_markdown_fails(self):
        self.write("NOTES.md", "# Notes\n")
        self.assertEqual(self.rules(), ["files"])
        self.assertEqual(check_text.main([str(self.root)]), 1)

    def test_docs_notes_and_adr_fail(self):
        self.write("docs/notes/x.md", "# X\n")
        self.write("docs/adr/0001-x.md", "# X\n")
        self.assertEqual(self.rules(), ["files", "files"])

    def test_allowed_docs_pass(self):
        self.write("docs/user/install.md", "# Install\n")
        self.write("docs/internals/overview.md", "# Overview\n")
        self.write("docs/operations/release.md", "# Release\n")
        self.write("CHANGELOG.md", "# Changelog\n")
        self.write(".agents/skills/x/SKILL.md", "# Skill\n")
        self.write(".github/pull_request_template.md", "## Problem\n")
        self.assertEqual(self.rules(), [])

    def test_organization_profile_allowed(self):
        self.write("profile/README.md", "# Org\n")
        self.assertEqual(self.rules(), [])

    def test_claude_md_must_be_import(self):
        self.write("CLAUDE.md", "@AGENTS.md\nAlso do this.\n")
        self.assertEqual(self.rules(), ["claude-md"])

    def test_claude_md_crlf_passes(self):
        self.write("CLAUDE.md", "@AGENTS.md\r\n")
        self.assertEqual(self.rules(), [])

    def test_agents_md_over_200_lines_fails(self):
        self.write("AGENTS.md", "line\n" * 201)
        self.assertEqual(self.rules(), ["length"])

    def test_page_over_400_lines_fails(self):
        self.write("docs/user/long.md", "line\n" * 401)
        self.assertEqual(self.rules(), ["length"])

    def test_em_dash_fails(self):
        self.write("src/A.java", "class A {\n    // one " + EM_DASH + " two\n}\n")
        findings = check_text.check(self.root)
        self.assertEqual([(f.rule, f.path, f.line) for f in findings], [("dash", "src/A.java", 2)])

    def test_en_dash_fails(self):
        self.write("src/A.java", "// 1" + EN_DASH + "2\n")
        self.assertEqual(self.rules(), ["dash"])

    def test_dash_inside_code_block_fails(self):
        self.write("docs/user/a.md", "# A\n\n```\nx " + EM_DASH + " y\n```\n")
        self.assertEqual(self.rules(), ["dash"])

    def test_date_in_comment_fails(self):
        self.write("src/A.java", "// fixed on 2026-09-22\nclass A {}\n")
        self.write("build.gradle.kts", "# 2026-09-22 note\n")
        self.assertEqual(self.rules(), ["date", "date"])

    def test_date_in_code_string_passes(self):
        self.write("src/A.java", 'class A { String v = "2026-09-22"; }\n')
        self.assertEqual(self.rules(), [])

    def test_date_in_doc_prose_fails(self):
        self.write("docs/user/a.md", "Changed on 2026-09-22.\n")
        self.assertEqual(self.rules(), ["date"])

    def test_decision_id_fails(self):
        self.write("docs/internals/a.md", "See ADR-0012 and D123.\n")
        self.assertEqual(self.rules(), ["decision-id", "decision-id"])

    def test_broken_relative_link_fails(self):
        self.write("README.md", "[x](docs/missing.md)\n")
        self.assertEqual(self.rules(), ["link"])

    def test_good_link_and_url_pass(self):
        self.write("README.md", "[a](docs/README.md) [b](https://example.com) [c](#top) [d](docs/README.md#x)\n")
        self.assertEqual(self.rules(), [])

    def test_vendor_markdown_ignored(self):
        self.write("vendor/lib/README.md", "x " + EM_DASH + " y\n")
        self.assertEqual(self.rules(), [])

    def test_changelog_text_ignored(self):
        self.write("CHANGELOG.md", "## 0.0.1 (2026-10-27)\n")
        self.assertEqual(self.rules(), [])

    def test_binary_file_ignored(self):
        (self.root / "icon.png").write_bytes(b"\x89PNG\x00\xe2\x80\x94")
        self.assertEqual(self.rules(), [])


if __name__ == "__main__":
    unittest.main()
