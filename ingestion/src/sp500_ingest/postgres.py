"""Environment-only PostgreSQL connection; credentials are never serialized."""
import os
from dotenv import find_dotenv,load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def engine():
    load_dotenv(find_dotenv(usecwd=True))
    required=['PGHOST','PGDATABASE','PGUSER','PGPASSWORD']
    missing=[key for key in required if not os.environ.get(key)]
    if missing:raise ValueError('Missing PostgreSQL configuration: '+', '.join(missing))
    url=URL.create('postgresql+psycopg2',username=os.environ['PGUSER'],password=os.environ['PGPASSWORD'],host=os.environ['PGHOST'],port=int(os.getenv('PGPORT','5432')),database=os.environ['PGDATABASE'])
    return create_engine(url,pool_pre_ping=True)
