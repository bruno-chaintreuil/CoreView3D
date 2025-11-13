#!/usr/bin/env node
import fs from "fs";
import path from "path";

const SKIP_DIRS = new Set(["node_modules", "dist", "build", ".git", ".next", ".cache"]);

function* walk(dir) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP_DIRS.has(f.name)) continue;
    const full = path.join(dir, f.name);
    if (f.isDirectory()) yield* walk(full);
    else if (f.name.endsWith(".ts") || f.name.endsWith(".tsx")) yield full;
  }
}

function analyzeFile(filePath) {
  try {
    const code = fs.readFileSync(filePath, "utf8");
    const info = { path: filePath, imports: [], exports: [], classes: [], functions: [], components: [] };

    const lines = code.split(/\r?\n/);
    for (const line of lines) {
      let l = line.trim();
      if (l.startsWith("import ")) info.imports.push(l);
      else if (l.startsWith("export ")) info.exports.push(l);
      else if (l.startsWith("class ")) {
        const m = l.match(/^class\s+(\w+)/);
        if (m) info.classes.push(m[1]);
      } else if (l.startsWith("function ")) {
        const m = l.match(/^function\s+(\w+)/);
        if (m) info.functions.push(m[1]);
      } else {
        // simple heuristique composant React
        const m = l.match(/^const\s+(\w+)\s*=\s*(\([^\)]*\)|[^\s]*)\s*=>/);
        if (m) info.components.push(m[1]);
      }
    }

    return info;
  } catch (err) {
    return { path: filePath, error: "read_error" };
  }
}

function summarizeRepo(rootDir) {
  const all = [];
  for (const file of walk(rootDir)) {
    const info = analyzeFile(file);
    if (info) all.push(info);
  }
  return { root: path.resolve(rootDir), files: all.length, summary: all };
}

// CLI
const dir = process.argv[2] || ".";
const result = summarizeRepo(dir);
console.log(JSON.stringify(result, null, 2));
