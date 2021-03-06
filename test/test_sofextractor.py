import unittest
import rdflib
from rdflib import Namespace,URIRef, BNode, Literal,Graph, plugin
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from uuid import uuid4
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
from shinc.ocr.sofextractor import SOFImageExtractor, SOFList, NS, SOFPDFExtractor, SOFTextExtractor

class SOFExtractorTestCase(unittest.TestCase):

    def setUp(self):
        self.test_line_unbounded1 = """08:00 PILOT ON BOARD"""
        self.test_line_unbounded2 = """08:00PILOT ON BOARD"""
        self.test_line_unbounded3 = """08:00 PILOT ON BOARD"""
        self.test_line_unbounded4 = """0800 PILOT ON BOARD"""
        self.test_line_unbounded5 = """08.00 PILOT ON BOARD 20.10.05"""
        self.test_line_unbounded6 = """08.00 PILOT ON BOARD 20/10/05"""
        self.test_line_bounded1 = """08.00 12.00 PILOT ON BOARD 20/10/05"""

        textfile = open('./text/sof-test1.txt')
        self.softext = textfile.read()
        textfile.close()

        self.generator = SOFList('./sofs/sof-master.csv')
        self.generator.generate()
        

    def test_ocrextractor(self):
        extractor = SOFImageExtractor('./images/test_image.jpg','./tmpdata')
        result = extractor.extract()
        res = False
        for line in result:
            if "FINAL DRAFT SURVEY" in line:
                res = True
        assert res

    def test_sof_generator(self):
        
        #print(result.serialize(format="turtle").decode("utf-8"))
        assert self.generator.sofs.query("ASK {shc:AWAITING-TRUCKS rdfs:subClassOf shc:Event.}", initNs=NS)
        assert self.generator.sofs.query("ASK {shc:AWAITING-TRUCKS rdfs:subClassOf shc:BoundedEvent.}", initNs=NS)

    def test_pdfextractor(self):
        extractor = SOFPDFExtractor('./pdfs/test.pdf')
        result = extractor.extract()
        #for line in result:
            #print (line)

    def test_text_time_extractor(self):
        textextractor = SOFTextExtractor(self.softext,self.generator)
        textextractor.extract()
        assert len(textextractor.extractTime(self.test_line_unbounded1))
        print(":".join(textextractor.extractTime(self.test_line_unbounded1)))
        assert len(textextractor.extractTime(self.test_line_unbounded2))
        assert len(textextractor.extractTime(self.test_line_unbounded3))
        assert len(textextractor.extractTime(self.test_line_unbounded4))
        assert len(textextractor.extractTime(self.test_line_unbounded5))
        assert len(textextractor.extractTime(self.test_line_unbounded6))
        assert len(textextractor.extractTime(self.test_line_bounded1))
