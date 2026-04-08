import { readdir, stat } from 'node:fs/promises';
import { join, relative } from 'node:path';

function matchPattern(path, pattern) {
  // Convert glob to regex
  const regex = new RegExp(
    '^' +
    pattern
      .replace(/\./g, '\\.')
      .replace(/\*\*/g, '{{GLOBSTAR}}')
      .replace(/\*/g, '[^/]*')
      .replace(/{{GLOBSTAR}}/g, '.*')
      .replace(/\?/g, '.') +
    '$'
  );
  return regex.test(path);
}

async function walkDir(dir, base = dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
        files.push(...await walkDir(fullPath, base));
      }
    } else {
      files.push(relative(base, fullPath));
    }
  }

  return files;
}

export async function glob(patterns) {
  const results = new Set();

  for (const pattern of patterns) {
    if (pattern.includes('*')) {
      const base = pattern.split('*')[0].replace(/\/$/, '') || '.';
      try {
        const files = await walkDir(base === '' ? '.' : base);
        for (const file of files) {
          const testPath = base === '.' ? file : join(base, file);
          if (matchPattern(testPath, pattern)) {
            results.add(testPath);
          }
        }
      } catch {
        // Directory doesn't exist, skip
      }
    } else {
      try {
        await stat(pattern);
        results.add(pattern);
      } catch {
        // File doesn't exist, skip
      }
    }
  }

  return [...results].sort();
}
