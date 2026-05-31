from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:gulomjon2003@localhost/delivery_db")

engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()