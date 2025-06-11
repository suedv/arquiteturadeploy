from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

URL_BANCO_DADOS = os.getenv(
    "URL_BANCO_DADOS",
    "postgresql://postgres:postgres@localhost:5432/aplicacao_distribuida"
)

motor = create_engine(URL_BANCO_DADOS)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

Base = declarative_base()

def obter_db():
    db = SessaoLocal()
    try:
        yield db
    finally:
        db.close() 