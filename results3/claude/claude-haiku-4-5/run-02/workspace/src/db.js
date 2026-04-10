import Database from 'better-sqlite3';
import path from 'path';
import os from 'os';

const dbPath = path.join(os.homedir(), '.noter', 'notes.db');

// Ensure directory exists
import fs from 'fs';
const dir = path.dirname(dbPath);
if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}

const db = new Database(dbPath);
db.pragma('journal_mode = WAL');

// Initialize schema
export function initDb() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      tags TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS note_tags (
      note_id INTEGER,
      tag TEXT,
      FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
      PRIMARY KEY(note_id, tag)
    );

    CREATE INDEX IF NOT EXISTS idx_tags ON note_tags(tag);
    CREATE INDEX IF NOT EXISTS idx_created ON notes(created_at);
  `);
}

export function addNote(title, content, tags = []) {
  const stmt = db.prepare(`
    INSERT INTO notes (title, content, tags)
    VALUES (?, ?, ?)
  `);
  const result = stmt.run(title, content, tags.join(','));

  // Add individual tags for search
  const tagStmt = db.prepare('INSERT OR IGNORE INTO note_tags (note_id, tag) VALUES (?, ?)');
  for (const tag of tags) {
    tagStmt.run(result.lastInsertRowid, tag.toLowerCase());
  }

  return result.lastInsertRowid;
}

export function getAllNotes() {
  return db.prepare(`
    SELECT id, title, content, tags, created_at, updated_at
    FROM notes
    ORDER BY created_at DESC
  `).all();
}

export function searchNotes(query) {
  const searchTerm = `%${query.toLowerCase()}%`;
  return db.prepare(`
    SELECT DISTINCT n.id, n.title, n.content, n.tags, n.created_at, n.updated_at
    FROM notes n
    LEFT JOIN note_tags nt ON n.id = nt.note_id
    WHERE LOWER(n.title) LIKE ?
       OR LOWER(n.content) LIKE ?
       OR LOWER(nt.tag) LIKE ?
    ORDER BY n.created_at DESC
  `).all(searchTerm, searchTerm, searchTerm);
}

export function getNoteById(id) {
  return db.prepare('SELECT * FROM notes WHERE id = ?').get(id);
}

export function deleteNote(id) {
  db.prepare('DELETE FROM notes WHERE id = ?').run(id);
}

export function updateNote(id, title, content, tags) {
  db.prepare(`
    UPDATE notes
    SET title = ?, content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
  `).run(title, content, tags.join(','), id);

  // Update tags
  db.prepare('DELETE FROM note_tags WHERE note_id = ?').run(id);
  const tagStmt = db.prepare('INSERT INTO note_tags (note_id, tag) VALUES (?, ?)');
  for (const tag of tags) {
    tagStmt.run(id, tag.toLowerCase());
  }
}

export function getNotesByTag(tag) {
  return db.prepare(`
    SELECT DISTINCT n.id, n.title, n.content, n.tags, n.created_at, n.updated_at
    FROM notes n
    JOIN note_tags nt ON n.id = nt.note_id
    WHERE nt.tag = ?
    ORDER BY n.created_at DESC
  `).all(tag.toLowerCase());
}

export function getAllTags() {
  return db.prepare('SELECT DISTINCT tag FROM note_tags ORDER BY tag').all().map(r => r.tag);
}

export default db;
