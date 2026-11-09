"""Reject credentials, data records and fitted artifacts from tracked source."""
import pathlib,re,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
failures=[]
for name in filter(None,paths):
    p=root/name
    if p.suffix.lower() in {'.parquet','.csv','.jsonl','.pkl','.pickle','.joblib','.zip','.whl','.pem','.key'} or name=='.env' or name=='config/operator.json':failures.append(name+': excluded artifact')
    if p.suffix.lower() in {'.png'}:continue
    text=p.read_text(encoding='utf8')
    if re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text):failures.append(name+': credential pattern')
    if re.search(r'(?im)^(?:COPY [^\n]+ FROM stdin;|INSERT INTO )',text) and p.suffix=='.sql':failures.append(name+': row payload in SQL')
if failures:raise SystemExit('Publication check failed: '+', '.join(failures))
print('Publication check passed: tracked source contains no excluded artifacts or credential patterns.')
