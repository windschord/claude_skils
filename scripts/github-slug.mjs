#!/usr/bin/env node
// github-slug.mjs - Generate GitHub-compatible heading anchors
// Usage: echo "heading text" | node scripts/github-slug.mjs
// Or:   node scripts/github-slug.mjs "heading text"
// Uses github-slugger for exact GitHub anchor compatibility
import GithubSlugger from 'github-slugger';

const slugger = new GithubSlugger();
const args = process.argv.slice(2);

if (args.length > 0) {
  // Process command-line arguments
  for (const heading of args) {
    process.stdout.write(slugger.slug(heading) + '\n');
  }
} else {
  // Process stdin line by line
  let data = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => { data += chunk; });
  process.stdin.on('end', () => {
    const lines = data.split('\n').filter(l => l.length > 0);
    for (const line of lines) {
      process.stdout.write(slugger.slug(line) + '\n');
    }
  });
}
