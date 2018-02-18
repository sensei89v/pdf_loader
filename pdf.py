from PyPDF2 import PdfFileReader, PdfFileWriter
import subprocess
import os
import io
from tempfile import mkstemp

class PngPage(object):
    def __init__(self, data, page_num):
        self.data = data
        self.page_num = page_num

    def get_data(self):
        return self.data

    def get_page_num(self):
        return self.page_num


class PdfDoc(object):
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def split(self):
        result = []
        pdf_temp_fd, pdf_temp_path = mkstemp(suffix=".pdf")
        png_temp_fd, png_temp_path = mkstemp(suffix=".png")

        original_pdf_bytes = io.BytesIO()
        original_pdf_bytes.write(self.data)
        original_pdf_bytes.seek(0)
        src_pdf = PdfFileReader(original_pdf_bytes)
        page_count = src_pdf.numPages

        for current_page in range(0, page_count):
            dst_pdf = PdfFileWriter()
            dst_pdf.addPage(src_pdf.getPage(current_page))
            f_pdf_write = open(pdf_temp_path, 'wb')
            dst_pdf.write(f_pdf_write)
            f_pdf_write.close()
            subprocess.run(["convert", pdf_temp_path, png_temp_path])
            #print(process.communicate())

            f_png_read = open(png_temp_path, 'rb')
            png_data = f_png_read.read()
            f_png_read.close()
            page = PngPage(png_data, current_page)
            result.append(page)

        os.close(pdf_temp_fd)
        os.close(png_temp_fd)
        os.remove(pdf_temp_path)
        os.remove(png_temp_path)
        return result

    def get_data(self):
        return self.data

    def get_filename(self):
        return self.filename
