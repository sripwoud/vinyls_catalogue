from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Album, Song

engine = create_engine('sqlite:///vinyls.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

genres = session.query(Genre).all()
for genre in genres:
    print genre.name
