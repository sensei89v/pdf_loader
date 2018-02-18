from PyPDF2 import PdfFileReader, PdfFileWriter
import subprocess
import os
import io
from tempfile import mkstemp


class PngPage(object):
    """
    Класс оборачивающий работу с PNG страницами PDF файла
    """
    def __init__(self, data, page_num):
        self.data = data
        self.page_num = page_num

    def get_data(self):
        """
        Возвращает бинарное содержимое страницы
        """
        return self.data

    def get_page_num(self):
        """
        Возвращает номер страницы
        """
        return self.page_num


class PdfDoc(object):
    """
    Класс оборачивающий работу PDF файлом
    """
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def split(self):
        """
        Разделяет PDF файл на страницы
        """
        # TODO: переделать на использование средств Python
        result = []
        # Генерируем два вспомогательных файла
        pdf_temp_fd, pdf_temp_path = mkstemp(suffix=".pdf")
        png_temp_fd, png_temp_path = mkstemp(suffix=".png")
        # Открываем "читальщик" pdf
        original_pdf_bytes = io.BytesIO()
        original_pdf_bytes.write(self.data)
        original_pdf_bytes.seek(0)
        src_pdf = PdfFileReader(original_pdf_bytes)
        page_count = src_pdf.numPages

        for current_page in range(0, page_count):
            # Записываем постранично pdf
            dst_pdf = PdfFileWriter()
            dst_pdf.addPage(src_pdf.getPage(current_page))
            f_pdf_write = open(pdf_temp_path, 'wb')
            dst_pdf.write(f_pdf_write)
            f_pdf_write.close()
            # Конвертируем pdf в png
            subprocess.run(["convert", pdf_temp_path, png_temp_path])
            f_png_read = open(png_temp_path, 'rb')
            # Читаем полученный PNG файл
            png_data = f_png_read.read()
            f_png_read.close()
            page = PngPage(png_data, current_page + 1) # Чтобы у страниц нумерация была не с нуля
            result.append(page)

        # Удаляем временные файлы
        os.close(pdf_temp_fd)
        os.close(png_temp_fd)
        os.remove(pdf_temp_path)
        os.remove(png_temp_path)
        return result

    def get_data(self):
        """
        Возвращает бинарное содержимое файла
        """
        return self.data

    def get_filename(self):
        """
        Возвращает бинарное название файла
        """
        return self.filename
