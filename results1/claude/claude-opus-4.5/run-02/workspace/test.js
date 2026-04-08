import { extractLinks } from './lib/checker.js';
import assert from 'node:assert';

const tests = [
  {
    name: 'extracts http links',
    input: '[Example](https://example.com) and [Test](http://test.org)',
    expected: [
      { text: 'Example', url: 'https://example.com' },
      { text: 'Test', url: 'http://test.org' },
    ],
  },
  {
    name: 'ignores relative links',
    input: '[Local](./local.md) and [Anchor](#section)',
    expected: [],
  },
  {
    name: 'handles complex markdown',
    input: `
# Title
Some text with [a link](https://a.com).
- List [item](https://b.com)
    `,
    expected: [
      { text: 'a link', url: 'https://a.com' },
      { text: 'item', url: 'https://b.com' },
    ],
  },
];

let passed = 0;
let failed = 0;

for (const test of tests) {
  try {
    const result = await extractLinks(test.input);
    assert.deepStrictEqual(result, test.expected);
    console.log(`✓ ${test.name}`);
    passed++;
  } catch (err) {
    console.log(`✗ ${test.name}`);
    console.log(`  Expected: ${JSON.stringify(test.expected)}`);
    console.log(`  Got: ${JSON.stringify(err.actual)}`);
    failed++;
  }
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
