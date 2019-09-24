import abc
import pdfkit
import json
import dict2xml

from jinja2 import FileSystemLoader, Environment


class Converter:
    '''Base class
    '''

    @abc.abstractmethod
    def convert(self, source, data=None):
        pass


class HTMLToPDF(Converter):
    '''Converts HTML content into PDF
    '''

    def __init__(self, temp_source):
        self.source = temp_source
        self.temp_loader = FileSystemLoader(temp_source)
        self.temp_env = Environment(loader=self.temp_loader)

    def render(self, temp_file, data):
        template = self.temp_env.get_template(temp_file)
        return template.render(**data)

    def convert(self, source, data=None):
        html_obj = self.render(source, data)
        return pdfkit.from_string(html_obj, False)


class JSONToXML(Converter):
    '''Convert Json into well-formed XML - No schema is predefined
    '''

    def convert(self, source, data=None):
        return dict2xml.dict2xml(json.loads(source))
