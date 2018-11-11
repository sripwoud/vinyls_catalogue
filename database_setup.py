from sqlalchemy import (
    Column, ForeignKey, Integer, String, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Define app's User class."""

    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)

    @property
    def serialize(self):
        """Return object data in serializeable format."""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture
        }


class Genre(Base):
    """Genre class."""

    __tablename__ = "genre"
    name = Column(String(20), nullable=False)
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    album = relationship("Album", cascade="all, delete-orphan")
    song = relationship("Song", cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in serializeable format."""
        return {
            'name': self.name,
            'id': self.id
        }


class Album(Base):
    """Album (release) class."""

    __tablename__ = "album"
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    artist = Column(String(80), nullable=False)
    label = Column(String(80), nullable=False)
    released = Column(String(4), nullable=False)
    image = Column(String(300), nullable=False)

    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    song = relationship("Song", cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in serializeable format."""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'label': self.label,
            'released': self.released,
            'genre_id': self.genre_id,
        }


class Song(Base):
    """Song class."""

    __tablename__ = "song"
    id = Column(Integer, primary_key=True)
    position = Column(String(4), nullable=False)
    title = Column(String(80), nullable=False)

    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    release_id = Column(Integer, ForeignKey('album.id'))
    album = relationship(Album)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in serializeable format."""
        return {
            'id': self.id,
            'position': self.position,
            'title': self.title,
            'release_id': self.release_id,
        }


engine = create_engine('sqlite:///vinyls.db',
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
