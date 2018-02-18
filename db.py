import sqlite3
from sqlalchemy import create_engine, Column, MetaData, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.types import LargeBinary, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Session = sessionmaker(autoflush=False)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

class Pdf(Base):
    __tablename__ = 'pdf'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    filename = Column(String(1024), nullable=False)
    pdf = Column(LargeBinary, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())

class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    pdf_id = Column(Integer, ForeignKey("pdf.id"), primary_key=True)
    page_num = Column(Integer, nullable=False)
    page = Column(LargeBinary, nullable=False)

class DBEngine(object):
    def __init__(self, path_to_db):
        self.engine = create_engine('sqlite:///%s' % path_to_db)
        Base.metadata.bind = self.engine
        Session.bind = self.engine

    def _get_session(self):
        return Session()

    def create_db(self):
        Table('user', Base.metadata,
            Column('id', Integer, primary_key=True, nullable=False),
            Column('login', String(128)),
            Column('password', String(128))
        )

        #Table('pdf', metadata,
        #    Column('id', Integer, primary_key=True, nullable=False),
        #    Column('user_id', Integer, ForeignKey("user.id"), nullable=False),
        #    Column('data', LargeBinary(), nullable=False)
        #)
        #
        #Table('page', metadata,
        #    Column('id', Integer, primary_key=True, nullable=False),
        #    Column('pdf_id', Integer, ForeignKey("pdf.id"), nullable=False),
        #    Column('pagenum', Integer, nullable=False),
        #    Column('data', LargeBinary(), nullable=False)
        #)
        #
        Base.metadata.create_all(self.engine)

    def add_user_to_db(self, login, password):
        session = self._get_session()
        user = User(login=login, password=password)
        session.add(user)
        session.commit()

    def get_user(self, login, password):
        session = self._get_session()
        users = session.query(User).filter(User.login == login).all()
        session.rollback()

        if not users:
            return None

        user = users[0]
        if user.password == password:
            return user.id
        else:
            return None

    def get_list_pdf(self):
        session = self._get_session()
        pdf_list = session.query(
            Pdf.id,
            Pdf.filename,
            Pdf.timestamp,
            User.login
        ).filter(
            User.id == Pdf.user_id
        ).order_by(
            Pdf.timestamp.asc()
        ).all()

        session.rollback()
        return pdf_list

    def append_pdf(self, user_id, pdf):
        session = self._get_session()
        pdf = Pdf(user_id=user_id, filename=pdf.get_filename(), pdf=pdf.get_data())
        session.add(pdf)
        session.commit()

    def get_pdf(self, pdf_id):
        session = self._get_session()

        try:
            pdf = session.query(
                Pdf.pdf,
                Pdf.filename
            ).filter(
                Pdf.id == pdf_id
            ).one()
        except NoResultFound as e:
            pdf = None

        session.rollback()
        return pdf

    def get_page(self, pdf_id, page_num):
        session = self._get_session()

        try:
            page = session.query(
                Pdf.filename,
                Page.page
            ).filter(
                Pdf.id == pdf_id,
                Page.pdf_id == pdf_id,
                Page.page_num == page_num
            ).one()
        except NoResultFound as e:
            page = None

        session.rollback()
        return page
