import os
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.template import Loader

from pdf import PdfDoc
from db import DBEngine


class DBHandler(RequestHandler):
    def initialize(self, db_engine, template_loader):
        self.db_engine = db_engine
        self.template_loader = template_loader

    def get_page(self, page, **kwargs):
        return self.template_loader.load(page).generate(**kwargs)

    def get_user(self):
        return self.get_cookie('user_id', None)

    def get_user_or_redirect(self):
        user_id = self.get_user()

        if user_id is None:
            self.redirect("/login")
        else:
            return user_id


class MainHandler(DBHandler):
    def get(self):
        self.write("Hello, world")


class LoginHandler(DBHandler):
    PAGE = 'login.html'

    def get(self):
        if self.get_user() is None:
            self.write(self.get_page(self.PAGE))
        else:
            self.redirect('/pdf')

    def post(self):
        login = self.get_argument('login', None)
        password = self.get_argument('password', None)

        if login is None or password is None:
            pass

        user_id = self.db_engine.get_user(login, password)

        if user_id is not None:
            self.set_cookie('user_id', str(user_id), path='/')

        self.redirect('/pdf')

class LogoutHandler(RequestHandler):
    def get(self):
        self.clear_cookie('user_id')
        self.redirect('/login')


class PdfHandler(DBHandler):
    PAGE = 'pdf.html'
    UPLOAD_KEY = 'fileupload'

    def get(self):
        self.get_user_or_redirect()
        self.write(self.get_page(self.PAGE))

    def post(self):
        user_id = self.get_user_or_redirect()
        if self.UPLOAD_KEY not in self.request.files:
            pass

        upload_files = self.request.files[self.UPLOAD_KEY]

        if len(upload_files) != 1:
            pass

        upload_file = upload_files[0]
        pdf = PdfDoc(upload_file.filename, upload_file.body)
        self.db_engine.append_pdf(user_id, pdf)
        self.write("done")

class PageHandler(DBHandler):
    PAGE = 'page.html'

    def get(self):
        self.get_user_or_redirect()
        self.write(self.get_page(self.PAGE))


class Server(object):
    def __init__(self, port, dbname, template_dir):
        self.db_engine = DBEngine(dbname)
        self.port = port

        init_db_args = {
            'db_engine': self.db_engine,
            'template_loader': Loader(template_dir)
        }
        application = Application([
            (r"/login", LoginHandler, init_db_args),
            (r"/logout", LogoutHandler),
            (r"/pdf", PdfHandler, init_db_args),
            (r"/page/(?P<pdf_id>\w+)", PageHandler),
            (r"/.*", MainHandler, init_db_args)
        ])
        self.http_server = HTTPServer(application)

    def run(self):
        self.http_server.listen(self.port)
        IOLoop.current().start()


