"""
Unit tests for DataProcessor
"""
import unittest
from src.main import DataProcessor


class TestDataProcessor(unittest.TestCase):
    """Test suite for DataProcessor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {'debug': True}
        self.processor = DataProcessor(self.config)

    def test_process_user(self):
        """Test user item processing"""
        item = {
            'type': 'user',
            'id': 1,
            'name': 'Alice',
            'email': 'ALICE@EXAMPLE.COM',
            'age': 25
        }

        result = self.processor.process_item(item)

        self.assertIsNotNone(result)
        self.assertEqual(result['email'], 'alice@example.com')
        self.assertTrue(result['adult'])

    def test_process_event(self):
        """Test event item processing"""
        item = {
            'type': 'event',
            'event_name': 'signup',
            'priority': 'high',
            'user_count': 150
        }

        result = self.processor.process_item(item)

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'signup')
        self.assertGreater(result['score'], 10)

    def test_invalid_item(self):
        """Test handling of invalid items"""
        invalid_items = [None, {}, {'invalid': 'data'}]

        for item in invalid_items:
            result = self.processor.process_item(item)
            # Should handle gracefully

    def test_batch_processing(self):
        """Test batch processing"""
        items = [
            {'type': 'user', 'id': 1, 'name': 'Alice'},
            {'type': 'user', 'id': 2, 'name': 'Bob'},
            {'type': 'event', 'event_name': 'login'}
        ]

        results = self.processor.batch_process(items)
        self.assertEqual(len(results), 3)


if __name__ == '__main__':
    unittest.main()
