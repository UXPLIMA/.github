import unittest

from check_title import problems


class CheckTitleTest(unittest.TestCase):
    def test_scoped_title_passes(self):
        self.assertEqual(problems("feat(key): add limits", ["key"]), [])

    def test_breaking_title_passes(self):
        self.assertEqual(problems("fix(storage)!: drop the old table", ["storage"]), [])

    def test_missing_scope_fails(self):
        self.assertEqual(problems("feat: add limits", ["key"]), ["missing scope; use one of: key"])

    def test_unknown_scope_fails(self):
        self.assertEqual(problems("feat(menu): add limits", ["key"]), ["unknown scope 'menu'; use one of: key"])

    def test_unknown_type_fails(self):
        self.assertEqual(problems("feature(key): add limits", ["key"]), ["unknown type 'feature'"])

    def test_upper_case_summary_fails(self):
        self.assertEqual(problems("feat(key): Add limits", ["key"]), ["summary starts with a capital letter"])

    def test_long_title_fails(self):
        title = "feat(key): " + "a" * 62
        self.assertEqual(problems(title, ["key"]), ["73 characters, limit 72"])

    def test_malformed_title_fails(self):
        self.assertEqual(problems("add limits", ["key"]), ["not 'type(scope): summary'"])


if __name__ == "__main__":
    unittest.main()
