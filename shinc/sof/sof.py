try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import subprocess
import os
import time
import csv
from uuid import uuid4

class SOFOCRExtractor:

    def __init__(self, tmppath='/tmp'):
        self.tmppath = tmppath


    def ocr(self, image):
        fn = self.tmppath + "/" + str(uuid4())
        cp = subprocess.run(["tesseract", "{}".format(image), "{}".format(fn)], check=True)
        if cp.returncode != 0:
            del environ[response_key]
            raise SOFException("Error running ocr " + image + " " + fn)
        else:
            time_to_wait = 5
            time_counter = 0
            while not os.path.exists(fn + ".txt"):
                time.sleep(1)
                time_counter += 1
                if time_counter > time_to_wait:break
            if os.path.exists(fn + ".txt"):
                result_file = open(fn + ".txt", 'r')
                result = result_file.read()
                result_file.close()
                os.remove(fn + ".txt")
            else:
                raise SOFException("Error writing OCR " + image + " " + fn + ".txt")
        return result

    def process_ocr_line(self, n):
        return n.strip()

    def extract(self, image):
        return list(map(self.process_ocr_line, self.ocr(image).split("\n")))


class SOFClassExtractor:

    def __init__(self):
        pass

    def extract(input, output):




class SOFEvent():
    pass

class SOF():
    pass

class SOFException(Exception):
    pass