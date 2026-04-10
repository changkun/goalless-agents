#!/usr/bin/env python3
"""Tests for brain CLI"""

import json
import os
import tempfile
import unittest
from pathlib import Path

# Set up test brain directory before importing
TEST_DIR = tempfile.mkdtemp(prefix='brain_test_')
os.environ['BRAIN_DIR'] = TEST_DIR

import brain


class TestBrain(unittest.TestCase):
    def setUp(self):
        """Set up fresh brain directory for each test"""
        # Reset index for test isolation
        brain_dir = brain.get_brain_dir()
        index_file = brain_dir / 'index.json'
        if index_file.exists():
            index_file.write_text(json.dumps({'notes': {}, 'tags': {}}, indent=2))
        # Clear notes directory
        notes_dir = brain_dir / 'notes'
        if notes_dir.exists():
            for f in notes_dir.glob('*.md'):
                f.unlink()
        brain.ensure_brain_dir()

    def test_ensure_brain_dir(self):
        """Test that brain directory is created properly"""
        brain_dir = brain.get_brain_dir()
        self.assertTrue(brain_dir.exists())
        self.assertTrue((brain_dir / 'notes').exists())
        self.assertTrue((brain_dir / 'daily').exists())
        self.assertTrue((brain_dir / 'index.json').exists())

    def test_generate_id(self):
        """Test ID generation"""
        id1 = brain.generate_id("test content")
        id2 = brain.generate_id("test content")
        self.assertEqual(len(id1), 8)
        self.assertNotEqual(id1, id2)  # Should be different due to timestamp

    def test_parse_frontmatter(self):
        """Test frontmatter parsing"""
        content = """---
title: Test Note
tags: work, ideas
---

This is the body"""

        metadata, body = brain.parse_frontmatter(content)
        self.assertEqual(metadata['title'], 'Test Note')
        self.assertEqual(metadata['tags'], ['work', 'ideas'])
        self.assertEqual(body, 'This is the body')

    def test_parse_frontmatter_no_frontmatter(self):
        """Test parsing content without frontmatter"""
        content = "Just regular content"
        metadata, body = brain.parse_frontmatter(content)
        self.assertEqual(metadata, {})
        self.assertEqual(body, content)

    def test_create_frontmatter(self):
        """Test frontmatter creation"""
        fm = brain.create_frontmatter("Test Title", ["tag1", "tag2"])
        self.assertIn("title: Test Title", fm)
        self.assertIn("tags: tag1, tag2", fm)
        self.assertIn("created:", fm)

    def test_load_save_index(self):
        """Test index load/save"""
        index = brain.load_index()
        index['notes']['test123'] = {'title': 'Test'}
        brain.save_index(index)

        loaded = brain.load_index()
        self.assertEqual(loaded['notes']['test123']['title'], 'Test')

    def test_cmd_new(self):
        """Test creating a new note"""
        class Args:
            title = ['Test', 'Note']
            tags = 'work,ideas'
            content = ['Some', 'content']
            edit = False

        result = brain.cmd_new(Args())
        self.assertEqual(result, 0)

        # Verify note was created
        index = brain.load_index()
        self.assertEqual(len(index['notes']), 1)

        note_id = list(index['notes'].keys())[0]
        self.assertEqual(index['notes'][note_id]['title'], 'Test Note')
        self.assertEqual(index['notes'][note_id]['tags'], ['work', 'ideas'])

    def test_cmd_list(self):
        """Test listing notes"""
        # Create a test note first
        class NewArgs:
            title = ['Test', 'Note']
            tags = 'work'
            content = ['content']
            edit = False

        brain.cmd_new(NewArgs())

        class ListArgs:
            tag = None
            limit = 20

        result = brain.cmd_list(ListArgs())
        self.assertEqual(result, 0)

    def test_cmd_tags(self):
        """Test listing tags"""
        # Create note with tags
        class Args:
            title = ['Tagged', 'Note']
            tags = 'python,learning'
            content = ['content']
            edit = False

        brain.cmd_new(Args())

        result = brain.cmd_tags(type('Args', (), {})())
        self.assertEqual(result, 0)

    def test_cmd_search(self):
        """Test searching notes"""
        # Create a note with specific content
        class Args:
            title = ['Searchable', 'Note']
            tags = None
            content = ['findme', 'unique', 'content']
            edit = False

        brain.cmd_new(Args())

        class SearchArgs:
            query = ['findme']

        result = brain.cmd_search(SearchArgs())
        self.assertEqual(result, 0)


class TestFrontmatter(unittest.TestCase):
    def test_complex_frontmatter(self):
        """Test parsing complex frontmatter"""
        content = """---
title: Complex Note
created: 2024-01-15T10:30:00
tags: work, project-x, urgent
author: test
---

# Heading

Body content here."""

        metadata, body = brain.parse_frontmatter(content)
        self.assertEqual(metadata['title'], 'Complex Note')
        self.assertEqual(len(metadata['tags']), 3)
        self.assertIn('urgent', metadata['tags'])
        self.assertTrue(body.startswith('# Heading'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
