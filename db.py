from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.types import LargeBinary, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from utils import create_salt, hash_password, check_password
Base = declarative_base()
Session = sessionmaker(autoflush=False)


class User(Base):
    """
    SQLalchemy модель к таблице пользователей
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)


class Pdf(Base):
    """
    SQLalchemy модель к таблице pdf файлов
    """
    __tablename__ = 'pdf'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    filename = Column(String(1024), nullable=False)
    pdf = Column(LargeBinary, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())


class Page(Base):
    """
    SQLalchemy модель к таблице отдельных страниц pdf файлов
    """
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_id = Column(Integer, ForeignKey("pdf.id"))
    page_num = Column(Integer, nullable=False)
    page = Column(LargeBinary, nullable=False)


class DBEngine(object):
    """
    Класс, обеспечивающий работу с БД
    """
    def __init__(self, path_to_db):
        self.engine = create_engine('sqlite:///%s' % path_to_db)
        Base.metadata.bind = self.engine
        Session.bind = self.engine

    def _get_session(self):
        """
        Внутренняя функция возвращает сессию
        """
        return Session()

    def create_db(self):
        """
        Создание таблиц БД
        """
        Base.metadata.create_all(self.engine)

    def add_user_to_db(self, login, password):
        """
        Добавление нового пользователя в таблицу пользователей
        """
        session = self._get_session()
        salt = create_salt()
        hashed_password = hash_password(salt, password)
        user = User(login=login, password=hashed_password)
        session.add(user)
        session.commit()

    def get_user_id(self, login, password):
        """
        Функция проверяет есть ли пользователь с такими логином и паролем в БД.
        В случае если пользователь найден возвращает его идентификатор
        """
        session = self._get_session()
        users = session.query(User).filter(User.login == login).all()
        session.rollback()

        if not users:
            return None

        user = users[0]

        if check_password(password, user.password):
            return user.id
        else:
            return None

    def is_exists_user_id(self, user_id):
        """
        Функция проверяет существует ли данный user_id в БД
        """
        session = self._get_session()
        exists = session.query(func.count(User.id)).filter(User.id == user_id).one()[0]
        session.rollback()
        exists = exists == 1

        return exists

    def get_pdf_list(self):
        """
        Возвращает список данных о pdf документах, хранящихся в БД
        """
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

    def get_page_list(self, pdf_id):
        """
        Возвращает список о страницах определенного pdf документа
        """
        session = self._get_session()
        page_list = session.query(
            Page.page,
            Page.page_num
        ).filter(
            Page.pdf_id == pdf_id
        ).order_by(
            Page.page_num.asc()
        ).all()

        session.rollback()
        return page_list

    def append_pdf(self, user_id, pdf, pages):
        """
        Добавление документа в БД
        """
        session = self._get_session()
        pdf = Pdf(user_id=user_id, filename=pdf.get_filename(), pdf=pdf.get_data())
        session.add(pdf)
        session.flush()

        for current_page in pages:
            page = Page(pdf_id=pdf.id, page=current_page.get_data(), page_num=current_page.get_page_num())
            session.add(page)

        session.commit()

    def get_pdf(self, pdf_id):
        """
        Получение pdf документа из БД
        """
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

    def get_pdf_filename(self, pdf_id):
        """
        Получение только имени pdf документа
        """
        session = self._get_session()

        try:
            pdf = session.query(
                Pdf.filename
            ).filter(
                Pdf.id == pdf_id
            ).one()
            filename = pdf.filename
        except NoResultFound as e:
            filename = None

        session.rollback()
        return filename

    def get_page(self, pdf_id, page_num):
        """
        Получение страницы pdf документа
        """
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
