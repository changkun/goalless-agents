"""
Main application entry point
Demonstrates various complexity patterns
"""
import sys
from typing import List, Optional


class DataProcessor:
    """Process and analyze data streams"""

    def __init__(self, config: dict):
        self.config = config
        self.processed_count = 0

    def process_item(self, item: dict) -> Optional[dict]:
        """Process a single item with validation"""
        # Validate item structure
        if not item or not isinstance(item, dict):
            return None

        result = {}

        # Complex conditional logic
        if 'type' in item:
            if item['type'] == 'user':
                result = self._process_user(item)
            elif item['type'] == 'event':
                result = self._process_event(item)
            elif item['type'] == 'transaction':
                result = self._process_transaction(item)
            else:
                result = {'error': 'Unknown type'}

        # Additional validation
        if 'timestamp' in item and item['timestamp'] > 0:
            result['processed_at'] = item['timestamp']

        self.processed_count += 1
        return result

    def _process_user(self, item: dict) -> dict:
        """Process user-type items"""
        user = {
            'id': item.get('id'),
            'name': item.get('name', 'Anonymous')
        }

        # Validate and enrich
        if 'email' in item and '@' in item['email']:
            user['email'] = item['email'].lower()

        if 'age' in item and item['age'] >= 18:
            user['adult'] = True

        return user

    def _process_event(self, item: dict) -> dict:
        """Process event-type items"""
        event = {
            'name': item.get('event_name'),
            'category': item.get('category', 'general')
        }

        # Complex event scoring
        score = 0
        if item.get('priority') == 'high':
            score += 10
        if item.get('user_count', 0) > 100:
            score += 5
        if item.get('duration', 0) > 3600:
            score += 3

        event['score'] = score
        return event

    def _process_transaction(self, item: dict) -> dict:
        """Process transaction-type items"""
        txn = {'id': item.get('id')}

        # Calculate fees
        amount = item.get('amount', 0)
        if amount > 1000:
            txn['fee'] = amount * 0.02
        elif amount > 100:
            txn['fee'] = amount * 0.03
        else:
            txn['fee'] = amount * 0.05

        return txn

    def batch_process(self, items: List[dict]) -> List[dict]:
        """Process multiple items"""
        results = []

        for item in items:
            processed = self.process_item(item)
            if processed:
                results.append(processed)

        return results


def main():
    """Main entry point"""
    config = {'debug': True, 'max_items': 1000}
    processor = DataProcessor(config)

    # Sample data
    items = [
        {'type': 'user', 'id': 1, 'name': 'Alice', 'age': 25},
        {'type': 'event', 'event_name': 'login', 'priority': 'high'},
        {'type': 'transaction', 'id': 'txn-123', 'amount': 500},
    ]

    results = processor.batch_process(items)
    print(f"Processed {len(results)} items")

    return 0


if __name__ == '__main__':
    sys.exit(main())
