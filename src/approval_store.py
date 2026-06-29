import sqlite3
from datetime import datetime

DB_PATH = "approvals.db"

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS approval_queue (                   
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             supplier_id TEXT,
             legal_name TEXT,
             risk_score INTEGER,
             reason TEXT,
             status TEXT,
             reviewer TEXT,
             created_at TEXT,
             resolved_at TEXT
         )
    """)
    connection.commit()
    connection.close()
    
def submit_for_approval(supplier_id, legal_name. risk_score, reason):
    init_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO approval_queue (supplier_id, legal_name, risk_score, reason, status, created_at)
        VALUES (?, ?, ?, ?, 'PENDING', ?)
    """, (supplier_id, legal_name, risk_score, reason, datetime.now().isoformat()))
    connection.commit()
    connection.close()
    return approval_id

def get_pending_approvals():
    init_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, supplier_id, legal_name, risk_score, reason, created_at 
        FROM approval_queue WHERE status = 'PENDING' ORDER BY created_at ASC
    """)
    pending_approvals = cursor.fetchall()
    connection.close()
    return pending_approvals

def resolve_approval(approval_id, approved, reviewer="procurement_manager"):
    init_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    new_status = "APPROVED" if approved else "REJECTED"
    cursor.execute("""
        UPDATE approval_queue
        SET status = ?, reviewer = ?, resolved_at = ?
        WHERE id = ?
    """, (new_status, reviewer, datetime.now().isoformat(), approval_id))
    connection.commit()
    connection.close()