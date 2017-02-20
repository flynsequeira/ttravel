from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
 
Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  gender = Column(String(6), nullable=False)
  dob = Column(DateTime(), nullable=False)
  profession = Column(String(250), nullable=False)
  #Type of travel companion
  ttype = Column(String(20000), nullable=False)
  password = Column(String(50), nullable=False)
  mobile=Column(String(50))
  picture = Column(String(250))

class BlogPost(Base):
    __tablename__ = 'post'
   
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(50000), nullable=False)
    time=Column(DateTime())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    filename = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'title'         : self.title,
           'description'	:self.description,
           'id'           : self.id,
       }




engine = create_engine('sqlite:///travellerdata.db')
 

Base.metadata.create_all(engine)