import sys
from sqlalchemy import (
    Column, ForeignKey, Integer, String, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Genre(Base):
    __tablename__ = "genre"
    name = Column(String(20), nullable=False)
    id = Column(Integer, primary_key=True)


class Album(Base):
    __tablename__ = "album"
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    artist = Column(String(80), nullable=False)
    label = Column(String(80), nullable=False)
    released = Column(String(4))

    genre_name = Column(String(20), ForeignKey('genre.name'))
    genre = relationship(Genre)


class Song(Base):
    __tablename__ = "song"
    id = Column(Integer, primary_key=True)
    position = Column(String(4), nullable=False)
    title = Column(String(80), nullable=False)

    release_id = Column(Integer, ForeignKey('album.id'))
    album = relationship(Album)


engine = create_engine('sqlite:///vinyls.db')
Base.metadata.create_all(engine)
