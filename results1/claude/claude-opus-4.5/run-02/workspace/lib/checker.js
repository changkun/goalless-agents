import { readFile } from 'node:fs/promises';

const LINK_REGEX = /\[([^\]]*)\]\(([^)]+)\)/g;
const URL_REGEX = /^https?:\/\//;

export async function extractLinks(content) {
  const links = [];
  let match;
  while ((match = LINK_REGEX.exec(content)) !== null) {
    const [, text, url] = match;
    if (URL_REGEX.test(url)) {
      links.push({ text, url });
    }
  }
  return links;
}

async function checkUrl(url, timeout) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
      headers: { 'User-Agent': 'mdcheck/1.0' },
      redirect: 'follow',
    });
    clearTimeout(id);
    return { url, ok: res.ok, status: res.status };
  } catch (err) {
    clearTimeout(id);
    if (err.name === 'AbortError') {
      return { url, ok: false, status: 'timeout' };
    }
    // Some servers reject HEAD, try GET
    try {
      const res = await fetch(url, {
        method: 'GET',
        signal: AbortSignal.timeout(timeout),
        headers: { 'User-Agent': 'mdcheck/1.0' },
        redirect: 'follow',
      });
      return { url, ok: res.ok, status: res.status };
    } catch {
      return { url, ok: false, status: err.code || 'error' };
    }
  }
}

async function pool(items, fn, concurrency) {
  const results = [];
  const executing = new Set();

  for (const item of items) {
    const p = fn(item).then(r => {
      executing.delete(p);
      return r;
    });
    executing.add(p);
    results.push(p);

    if (executing.size >= concurrency) {
      await Promise.race(executing);
    }
  }

  return Promise.all(results);
}

export async function checkFiles(files, opts) {
  let totalBroken = 0;

  for (const file of files) {
    const content = await readFile(file, 'utf-8');
    const links = await extractLinks(content);

    if (links.length === 0) {
      if (opts.verbose) {
        console.log(`\n${file}: no links found`);
      }
      continue;
    }

    console.log(`\n${file} (${links.length} links)`);

    const uniqueUrls = [...new Set(links.map(l => l.url))];
    const results = await pool(
      uniqueUrls,
      url => checkUrl(url, opts.timeout),
      opts.concurrent
    );

    const statusMap = new Map(results.map(r => [r.url, r]));

    for (const link of links) {
      const result = statusMap.get(link.url);
      if (!result.ok) {
        totalBroken++;
        console.log(`  ✗ [${result.status}] ${link.url}`);
      } else if (opts.verbose) {
        console.log(`  ✓ [${result.status}] ${link.url}`);
      }
    }
  }

  console.log(`\n${totalBroken === 0 ? '✓ All links valid' : `✗ ${totalBroken} broken link(s)`}`);
  return totalBroken > 0 ? 1 : 0;
}
