from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Album, Song

engine = create_engine('sqlite:///vinyls.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# test
hiphop = Genre(name="Hip Hop")
session.add(hiphop)
session.commit()

album1 = Album(genre=hiphop,
               title="Album 1",
               artist="Blabla",
               label="cool",
               released="2018")
session.add(album1)
session.commit()

song1 = Song(album=album1,
             title="Song 1",
             position="1")
session.add(song1)
session.commit()

# test
print session.query(Genre).one().name
print session.query(Album).one().title
print session.query(Song).one().title
