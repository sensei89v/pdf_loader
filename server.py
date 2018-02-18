import os
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from tornado.template import Loader

from pdf import PdfDoc
from db import DBEngine


class BaseHandler(RequestHandler):
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


class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")


class LoginHandler(BaseHandler):
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


class PdfHandler(BaseHandler):
    PAGE = 'pdf.html'
    UPLOAD_KEY = 'fileupload'

    class PdfListItem(object):
        def __init__(self, row):
            self.login = row.login
            self.filename = row.filename
            self.timestamp = row.timestamp
            self.pdf_link = "/pdf/%s" % row.id
            self.png_table_link = '/page/%s' % row.id

    def get(self):
        self.get_user_or_redirect()
        pdf_list = self.db_engine.get_pdf_list()
        pdf_list = list(map(lambda x: self.PdfListItem(x), pdf_list))
        self.write(self.get_page(self.PAGE, pdf_list=pdf_list))

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
        self.redirect("/pdf")


class PageHandler(BaseHandler):
    PAGE = 'page.html'

    class PageListItem(object):
        def __init__(self, row, pdf_id, basename):
            self.page_link = "/page/%s/%s" % (pdf_id, row.page_num)
            self.filename = '%s_%s.png' % (basename, row.page_num)

    def get(self, pdf_id):
        self.get_user_or_redirect()
        filename = self.db_engine.get_pdf_filename(pdf_id)

        if filename is None:
            pass

        basename = os.path.basename(filename)
        page_list = self.db_engine.get_page_list(pdf_id)
        page_list = list(map(lambda x: self.PageListItem(x, pdf_id, basename), page_list))
        self.write(self.get_page(self.PAGE, page_list=page_list, filename=filename))


class PdfDownloadHandler(BaseHandler):
    def get(self, pdf_id):
        self.get_user_or_redirect()
        # TODO: обработка ошибок
        pdf = self.db_engine.get_pdf(pdf_id)

        if pdf is None:
            pass

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + pdf.filename)
        self.write(pdf.pdf)


class PageDownloadHandler(BaseHandler):
    def get(self, pdf_id, page_num):
        self.get_user_or_redirect()
        # TODO: обработка ошибок
        page = self.db_engine.get_page(pdf_id, page_num)

        if page is None:
            pass

        filename = "%s_%s.png" % (page.filename, page_num)
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + filename)
        self.write(page.page)


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
            (r"/pdf/(?P<pdf_id>\w+)", PdfDownloadHandler, init_db_args),
            (r"/page/(?P<pdf_id>\w+)", PageHandler, init_db_args),
            (r"/page/(?P<pdf_id>\w+)/(?P<page_id>\w+)", PageDownloadHandler, init_db_args),
            (r"/.*", MainHandler, init_db_args)
        ])
        self.http_server = HTTPServer(application)

    def run(self):
        self.http_server.listen(self.port)
        IOLoop.current().start()


