import sys
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.utils.general import eprint
from src.db.postgres_connection import get_postgres_connection_string_with_config_file


# create the db connection string based on the parameters present in the config file
# the location of the config file should be added relative to the main file!
if (connection_string := get_postgres_connection_string_with_config_file(config_file="config.conf")) is None:
    # if there are missing fields, stop everything.
    sys.exit(1)
else:
    DATABASE_URL = connection_string

# create the engine
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    eprint(f"Couldn't create databas engine: {e}")
    sys.exit(2)

# create a session maker
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create the base for models(tables)
Base = declarative_base()


@contextmanager
def session_scope():
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

