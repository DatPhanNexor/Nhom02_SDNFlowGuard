import sqlite3
import hashlib

db_path = r'D:\Project\Nhom02_SDNFlowGuard\database\sdnflowguard.db'
with open(db_path, 'rb') as f:
    h = hashlib.sha256(f.read()).hexdigest()

print(f'DB Path: {db_path}')
print(f'DB SHA-256: {h}')
expected = '3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9'
print(f'Matches expected: {h == expected}')

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('PRAGMA integrity_check;')
print(f'Integrity check: {cur.fetchall()}')

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print(f'Tables ({len(tables)}): {tables}')
counts = {}
for t in tables:
    cur.execute(f'SELECT count(*) FROM {t};')
    counts[t] = cur.fetchone()[0]
print(f'Row counts: {counts}')
conn.close()
