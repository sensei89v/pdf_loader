
class PdfPage(object):
    def __init__(self, data, page_num):
        self.data = data
        self.page_num

    def save_to_db(self):
        raise ENotImplemented

    @classmethod
    def load_from_db(cls, id):
        pass

class PdfDoc(object):
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

    def split(self):
        raise ENotImplemented

    def get_data(self):
        return self.data

    def get_filename(self):
        return self.filename
    @classmethod
    def load_from_db(cls, id):
        pass


if __name__ == "__main__":
    import sys
    import io
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from wand.image import Image

    if len(sys.argv) != 3:
        print("usage with file")
        sys.exit(1)

    filename = sys.argv[1]
    dirname = sys.argv[1]
    f = open(filename, "rb")
    src_pdf = PdfFileReader(f)
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(src_pdf.getPage(0))
    f1 = open("/home/sensei/ttt.pdf", "wb")
    dst_pdf.write(f1)
    f1.close()

    #f2 = open("/home/sensei/ttt.pdf", "rb")
    img = Image(filename = "/home/sensei/ttt.pdf")
    img.convert("png")
    #
    #pdf_bytes = io.BytesIO()
    #dst_pdf.write(pdf_bytes)
    #pdf_bytes.seek(0)
    #
    #img = Image(file = pdf_bytes)
    #img.convert("png")

    #for i in range(0, src_pdf.numPages):
    #    # Get the first page of the PDF #
    #    dst_pdf = PdfFileWriter()
    #    dst_pdf.addPage(src_pdf.getPage(0))
    #
    #    # Create BytesIO #
    #    pdf_bytes = io.BytesIO()
    #    dst_pdf.write(pdf_bytes)
    #    pdf_bytes.seek(0)
    #
    #    file_name = "%s/%i.png" % (dirname, i)
    #    img = Image.open(pdf_bytes)
    #    img.save(file_name, 'PNG')
    #    pdf_bytes.flush()


#src_pdf = PyPDF2.PdfFileReader(file(src_filename, "rb"))
#
## What follows is a lookup table of page numbers within sample_log.pdf and the corresponding filenames.
#pages = [{"pagenum": 22,  "filename": "samplelog_jrs0019_p1"},
#         {"pagenum": 23,  "filename": "samplelog_jrs0019_p2"},
#         {"pagenum": 124, "filename": "samplelog_jrs0075_p3_2011-02-05_18-55"},]
#
## Convert each page to a png image.
#for page in pages:
#    big_filename = page["filename"] + ".png"
#    small_filename = page["filename"] + "_small" + ".png"
#
#img = pdf_page_to_png(src_pdf, pagenum = page["pagenum"], resolution = 300)
#
