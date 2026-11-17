PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    industry TEXT NOT NULL DEFAULT 'Unknown',
    project_type TEXT NOT NULL DEFAULT 'Unknown',
    engineering_discipline TEXT NOT NULL DEFAULT 'Unknown',
    proposal_year INTEGER CHECK(proposal_year IS NULL OR proposal_year BETWEEN 1900 AND 2100),
    client_name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    uploaded_at TEXT NOT NULL,
    file_location TEXT NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    extracted_text TEXT NOT NULL,
    extraction_warning TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS segments (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    location TEXT NOT NULL,
    text TEXT NOT NULL,
    UNIQUE(document_id, sequence)
);
CREATE INDEX IF NOT EXISTS document_filters ON documents(industry, proposal_year, engineering_discipline, project_type);
CREATE INDEX IF NOT EXISTS segments_document ON segments(document_id);
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title, description, extracted_text,
    content='documents', content_rowid='id', tokenize='unicode61'
);
CREATE VIRTUAL TABLE IF NOT EXISTS segments_fts USING fts5(
    text, content='segments', content_rowid='id', tokenize='unicode61'
);
CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
    INSERT INTO documents_fts(rowid,title,description,extracted_text) VALUES(new.id,new.title,new.description,new.extracted_text);
END;
CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
    INSERT INTO documents_fts(documents_fts,rowid,title,description,extracted_text) VALUES('delete',old.id,old.title,old.description,old.extracted_text);
END;
CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
    INSERT INTO documents_fts(documents_fts,rowid,title,description,extracted_text) VALUES('delete',old.id,old.title,old.description,old.extracted_text);
    INSERT INTO documents_fts(rowid,title,description,extracted_text) VALUES(new.id,new.title,new.description,new.extracted_text);
END;
CREATE TRIGGER IF NOT EXISTS segments_ai AFTER INSERT ON segments BEGIN
    INSERT INTO segments_fts(rowid,text) VALUES(new.id,new.text);
END;
CREATE TRIGGER IF NOT EXISTS segments_ad AFTER DELETE ON segments BEGIN
    INSERT INTO segments_fts(segments_fts,rowid,text) VALUES('delete',old.id,old.text);
END;
CREATE TRIGGER IF NOT EXISTS segments_au AFTER UPDATE ON segments BEGIN
    INSERT INTO segments_fts(segments_fts,rowid,text) VALUES('delete',old.id,old.text);
    INSERT INTO segments_fts(rowid,text) VALUES(new.id,new.text);
END;
