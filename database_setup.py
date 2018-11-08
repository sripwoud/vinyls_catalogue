import sys
from sqlalchemy import (
    Column, ForeignKey, Integer, String, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(300))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
            'email': self.email
            'picture': self.picture
        }


class Genre(Base):
    __tablename__ = "genre"
    name = Column(String(20), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class Album(Base):
    __tablename__ = "album"
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    artist = Column(String(80), nullable=False)
    label = Column(String(80), nullable=False)
    released = Column(String(4), nullable=False)
    image = Column(String(300), nullable=False)

    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'label': self.label,
            'released': self.released,
            'genre_id': self.genre_id,
        }


class Song(Base):
    __tablename__ = "song"
    id = Column(Integer, primary_key=True)
    position = Column(String(4), nullable=False)
    title = Column(String(80), nullable=False)

    release_id = Column(Integer, ForeignKey('album.id'))
    album = relationship(Album)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'position': self.position,
            'title': self.title,
            'release_id': self.release_id,
        }


engine = create_engine('sqlite:///vinyls.db',
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
