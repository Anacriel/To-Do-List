from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime


class DbTool:

    def __init__(self, db_name):
        self.engine = create_engine('sqlite:///' + db_name + '?check_same_thread=false')
        self.Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def close(self):
        self.session.close()

    Base = declarative_base()

    class Task(Base):
        __tablename__ = 'task'
        id = Column(Integer, primary_key=True)
        task = Column(String)
        deadline = Column(Date, default=datetime.today())
