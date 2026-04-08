#!/usr/bin/env python3
"""
Unit tests for SmartCommit
"""

import unittest
from smartcommit import CommitAnalyzer


class TestCommitAnalyzer(unittest.TestCase):
    """Test cases for CommitAnalyzer"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CommitAnalyzer()

    def test_determine_type_feature(self):
        """Test feature detection"""
        self.analyzer.diff_content = "+def new_function():\n+    pass"
        self.analyzer.stats = {
            'files': ['api.py'],
            'insertions': 50,
            'deletions': 5
        }
        commit_type = self.analyzer._determine_type()
        self.assertEqual(commit_type, 'feat')

    def test_determine_type_fix(self):
        """Test bug fix detection"""
        self.analyzer.diff_content = "-old_buggy_code()\n+fixed_code() # fix memory leak"
        self.analyzer.stats = {
            'files': ['cache.py'],
            'insertions': 10,
            'deletions': 10
        }
        commit_type = self.analyzer._determine_type()
        self.assertEqual(commit_type, 'fix')

    def test_determine_type_test(self):
        """Test detection for test files"""
        self.analyzer.diff_content = "test content"
        self.analyzer.stats = {
            'files': ['test_api.py'],
            'insertions': 30,
            'deletions': 0
        }
        commit_type = self.analyzer._determine_type()
        self.assertEqual(commit_type, 'test')

    def test_determine_type_docs(self):
        """Test documentation detection"""
        self.analyzer.diff_content = "# Documentation update"
        self.analyzer.stats = {
            'files': ['README.md'],
            'insertions': 20,
            'deletions': 5
        }
        commit_type = self.analyzer._determine_type()
        self.assertEqual(commit_type, 'docs')

    def test_determine_type_refactor(self):
        """Test refactor detection"""
        self.analyzer.diff_content = "code restructure"
        self.analyzer.stats = {
            'files': ['utils.py'],
            'insertions': 20,
            'deletions': 40
        }
        commit_type = self.analyzer._determine_type()
        self.assertEqual(commit_type, 'refactor')

    def test_determine_scope_single_file(self):
        """Test scope detection for single file"""
        self.analyzer.stats = {'files': ['src/api.py']}
        scope = self.analyzer._determine_scope()
        self.assertEqual(scope, 'api')

    def test_determine_scope_multiple_files(self):
        """Test scope detection for multiple files"""
        self.analyzer.stats = {
            'files': ['src/auth/login.py', 'src/auth/logout.py']
        }
        scope = self.analyzer._determine_scope()
        self.assertEqual(scope, 'auth')

    def test_determine_scope_no_common_dir(self):
        """Test scope detection with no common directory"""
        self.analyzer.stats = {
            'files': ['api.py', 'utils.py', 'models.py']
        }
        scope = self.analyzer._determine_scope()
        self.assertIsNone(scope)

    def test_format_commit_message_with_scope(self):
        """Test commit message formatting with scope"""
        message = self.analyzer.format_commit_message(
            'feat', 'auth', 'add user login',
            ['Add login endpoint', 'Add JWT validation']
        )
        self.assertIn('feat(auth): add user login', message)
        self.assertIn('- Add login endpoint', message)
        self.assertIn('- Add JWT validation', message)

    def test_format_commit_message_without_scope(self):
        """Test commit message formatting without scope"""
        message = self.analyzer.format_commit_message(
            'docs', None, 'update README',
            ['Add installation instructions']
        )
        self.assertIn('docs: update README', message)
        self.assertIn('- Add installation instructions', message)

    def test_generate_description_single_file_feature(self):
        """Test description generation for single file feature"""
        self.analyzer.stats = {'files': ['api.py']}
        desc = self.analyzer._generate_description('feat')
        self.assertEqual(desc, 'add api implementation')

    def test_generate_description_multiple_files(self):
        """Test description generation for multiple files"""
        self.analyzer.stats = {'files': ['a.py', 'b.py', 'c.py']}
        desc = self.analyzer._generate_description('refactor')
        self.assertIn('3 modules', desc)

    def test_extract_details(self):
        """Test detail extraction"""
        self.analyzer.stats = {
            'files': ['api.py', 'utils.py'],
            'files_changed': 2,
            'insertions': 50,
            'deletions': 20
        }
        details = self.analyzer._extract_details()
        self.assertIn('Modify api.py', details)
        self.assertIn('Modify utils.py', details)
        self.assertIn('Add 50 lines', details)
        self.assertIn('Remove 20 lines', details)


class TestCommitTypes(unittest.TestCase):
    """Test commit type constants"""

    def test_commit_types_exist(self):
        """Test that all expected commit types are defined"""
        expected_types = ['feat', 'fix', 'docs', 'style', 'refactor',
                         'perf', 'test', 'build', 'ci', 'chore']
        for commit_type in expected_types:
            self.assertIn(commit_type, CommitAnalyzer.COMMIT_TYPES)

    def test_commit_types_have_descriptions(self):
        """Test that all commit types have descriptions"""
        for commit_type, description in CommitAnalyzer.COMMIT_TYPES.items():
            self.assertIsInstance(description, str)
            self.assertTrue(len(description) > 0)


if __name__ == '__main__':
    unittest.main()
