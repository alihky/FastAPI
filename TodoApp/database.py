from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ضع رابط Neon الذي نسخته من الموقع بين علامات التنصيص
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_zltJaFK5YP8b@ep-flat-sea-b1ma9610.c-5.eu-central-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()