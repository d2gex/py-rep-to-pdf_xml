import multiprocessing
import json
import uuid

from os.path import join
from src.data_converter import HTMLToPDF, JSONToXML


class ReportGenerator:

    def __init__(self, reports_folder, temps_folder, data):
        self.reports_folder = reports_folder
        self.temps_folder = temps_folder
        self.raw_obj = data
        self.json_obj = json.dumps(data)
        self._filename = join(reports_folder, str(uuid.uuid4()).replace('-', ''))

    @property
    def filename(self):
        return self._filename

    def to_pdf(self, temp_file):
        '''It generates a PDF report and store it on the filesystem
        '''
        html_pdf = HTMLToPDF(self.temps_folder)
        pdf = html_pdf.convert(temp_file, self.raw_obj)
        filename = f"{self._filename}.pdf"
        with open(join(self.reports_folder, filename), 'wb') as fh:
            fh.write(pdf)

    def to_xml(self):
        '''It generates an XML report and store it on the filesystem
        '''
        jxml = JSONToXML()
        xml = jxml.convert(self.json_obj)
        filename = f"{self._filename}.xml"
        with open(join(self.reports_folder, filename), 'w') as fh:
            fh.write(xml)

    def run(self, temp_file):
        '''Create a child process to generate a PDF report while the parent process generates the XML one.
        Both reports are saved to the filesystem
        '''
        child_process = multiprocessing.Process(target=self.to_pdf, args=(temp_file,))
        child_process.start()
        self.to_xml()
        child_process.join()
