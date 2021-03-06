try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import subprocess
import os
import time
import PyPDF2
import csv
import re
import pdfplumber
import datetime
from rdflib import Namespace,URIRef, BNode, Literal,Graph, plugin
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from uuid import uuid4
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD

SHC = Namespace("http://data.shinc.co.uk/")
NS = { 'foaf': FOAF, 'rdfs' : RDFS, "owl" : OWL, 'xsd' : XSD, 'rdf' : RDF, 'shc' : SHC}

class SOFImageExtractor:

    def __init__(self, image, tmppath='/tmp'):
        self.tmppath = tmppath
        self.image = image


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

    def processOcrLine(self, n):
        return n.strip()

    def extract(self):
        return list(map(self.processOcrLine, self.ocr(self.image).split("\n")))

class SOFTextExtractor:

    DATEPATTERNS = [

        {
            "name": 'dd/mm/yyyy',
            "regex": '^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$',
            "delimiter": '/'
        },

        {
            "name": 'dd.mm.yyyy',
            "regex": '^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$',
            "delimiter": '/'
        },

        {
            "name": 'dd-mm-yyyy',
            "regex": '^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$',
            "delimiter": '-'
        }        

    ]

    TIMEPATTERNS = [

        {
            "name": 'hh:mm',
            "regex": '([01]\d|2[0-3]):?([0-5]\d)',
            "delimiter": ':'
        },  

        {
            "name": 'hh.mm',
            "regex": '([01]\d|2[0-3])[.]?([0-5]\d)',
            "delimiter": '.'
        },  

        {
            "name": 'hhmm',
            "regex": '([01]\d|2[0-3])([0-5]\d)',
            "delimiter": ''
        }  

    ]
        

    def __init__(self, soflist, summarylist,  timepatterns=None, datepatterns=None):
        self.soflist = soflist
        self.summarylist = summarylist
        if timepatterns:
            self.timepatterns = timepatterns
        else:
            self.timepatterns = SOFTextExtractor.TIMEPATTERNS
        if datepatterns:
            self.datepatterns = datepatterns
        else:
            self.datepatterns = SOFTextExtractor.DATEPATTERNS
        pass

    def extract(self, text, starttext=None, endtext=None, startdate=None, enddate=None, datemask="dd-mm-yyyy", timemask="hh.mm", timezone="UTC"):
        sofs = []
        summary_sofs = []
        date_count = startdate
        time_count = starttime
        if starttext:
            started = False
        else:
            started = True
        for line in text:
            if started and self.textContainsSof(line):
                sof= extractLine(text, date_count, time_count, datemask, timemask, timezone)
                date_count = sof.startdate
                time_count = sof.starttime
                sofs.append(sof)
            elif started and self.extractDate(line):
                date_count = self.extractDate()[0]
            else:
                if startetext in line:
                    started = True
        return sofs
                    

                

    def extractLine(self, text, date_count, time_count, datemask, timemask, timezone):
        softype = self.textContainsSof(text)
        id = SHC + uuid4()
        sof = SOFEvent(id, softype.id, softype.description)
        times = self.extractTime(text, timemask, timezone)
        timepattern = next((x for x in self.timepatterns if x.name == timemask), None)
        datepattern = next((y for y in self.datepatterns if y.name == datemask), None)
        if times:
            time_from = parseTime(times[0], timepattern.delimiter)
            time_to = None
            if softype.bounded:
                time_to = parseTime(times[1], timepattern.delimiter)
        dates = self.extractDate(text, datemask)
        if dates:
            date_from = dates[0]
            date_to = None
            if len(dates) > 1:
                date_to = dates[1]
        if times and not dates and time_to < time_from:
            date_to = date_to + datetime.timedelta(days=1)
        return sof

    def textContainsSof(self, text):
        res = False
        for sof in self.soflist.softypes:
            if sof.description in text:
                res = sof
        return res

    def extractTime(self, text, timemask):
        res = None
        timepattern = next((x for x in self.timepatterns if x.name == timemask), None)
        if timepattern:
            for pattern in timepattern.regex:
                print ("looking for " + pattern  + " in " + text)
                times = re.search(pattern, text)
                if times:
                    print ("found time")
                    res = []
                    res.append( times.group(0))
        return res

    def parseTime(self, timestring, delimiter):
        return time(int(timestring.split(delimiter)[0]), int(timestring.split(delimiter)[1]),0)

    def parseDate(self, datestring, delimiter):
        return date(int(datestring.split(delimiter)[2]), int(datestring.split(delimiter)[1]), int(datestring.split(delimiter)[0]))

    def extractDate(self, text, datemask):
        res = None
        datepattern = next((y for y in self.datepatterns if y.name == datemask), None)
        if datepattern:
            for pattern in datepattern.regex:
                dates = re.search(pattern,text)
                if dates:
                    res = []
                    res.append( dates.group(0))
            return res

    def generateDatetime(self, dateobj, timeobj, timezone):
        return datetime(year=dateobj.year, month=dateobj.month, day=dateobj.day,hour=timeobj.hour,minute=timeobj.minute)







class SOFPDFExtractor:
    def __init__(self, pdf):
        self.pdf = pdf

    def createListFromPdf(self, pdf):
        content = []
        with pdfplumber.open(pdf) as pdf:
            for page in pdf.pages:
                content += page.extract_text().split("\n")
        
        return content

    def extract(self):
        return self.createListFromPdf(self.pdf)



class SOFEvent:
    def __init__(self, id, timezone="UTC", type=None, description=None, time_from=None, time_to=None, date_from=None, date_to=None):
        self.id = id
        self.startdatetime = date_from
        self.description = description
        self.enddatetime = time_to
        

class SOF:
    def __init__(self, id, sofs=None):
        self.id = id
        self.sofs = sofs

class SOFType:
    def __init__(self,id, description, bounded=False, notation=False, stoppage=False, display=False):
        self.id = id
        self.description = description
        self.bounded = bounded
        self.notation = notation
        self.stoppage = stoppage
        self.display = display

class SOFList:
    def __init__(self, file):
        self.file = file
        self.sofs = None
        self.softypes = []

    def generate(self):
        return self.createListFromFile(self.file)

    def createListFromFile(self, file):
        self.sofs = Graph()
        f = open(file, "r")
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                name = row[0]
                uri = URIRef(SHC + name.replace(" ","-"))
                softype = SOFType(SHC + name.replace(" ","-"), name)
                self.sofs.add((uri, RDFS.label, Literal(name, lang="en")))
                self.sofs.add((uri, RDFS.subClassOf, SHC.Event))
                if row[1] == "1":
                    self.sofs.add((uri, RDFS.subClassOf, SHC.BoundedEvent))
                    softype.bounded = True
                if row[4] == "1":
                    self.sofs.add((uri, RDFS.subClassOf, SHC.DisplayableEvent))  
                    softype.notation = True
                self.softypes.append(softype)  
        f.close()
        return self.sofs

    def getUriFromDescription(self, text):
        rows = self.sofs.query("SELECT ?type WHERE {?type rdfs:label '" + text + "' } ", initNs=NS)
        return str(rows[0])


class SOFException(Exception):
    pass
