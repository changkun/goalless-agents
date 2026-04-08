import assert from 'assert';

// Test formatTime
function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function progressBar(current, total, width = 30) {
  const filled = Math.round((current / total) * width);
  const empty = width - filled;
  return `[${'█'.repeat(filled)}${'░'.repeat(empty)}]`;
}

// Tests
console.log('Running tests...\n');

// formatTime tests
assert.strictEqual(formatTime(0), '00:00');
assert.strictEqual(formatTime(60), '01:00');
assert.strictEqual(formatTime(90), '01:30');
assert.strictEqual(formatTime(1500), '25:00');
assert.strictEqual(formatTime(3599), '59:59');
console.log('✓ formatTime');

// progressBar tests
assert.strictEqual(progressBar(0, 100, 10), '[░░░░░░░░░░]');
assert.strictEqual(progressBar(50, 100, 10), '[█████░░░░░]');
assert.strictEqual(progressBar(100, 100, 10), '[██████████]');
console.log('✓ progressBar');

console.log('\nAll tests passed!');
