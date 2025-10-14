# Everything about Bible servers
import os
import xml.etree.ElementTree as ET


class Bibleservers:
    def __init__(self):

        # Read the servers data from the xml file. As this is a package, we need to use the absolute path
        cwd = os.path.dirname(os.path.abspath(__file__))
        self._servers = self.parse_xml(os.path.join(cwd, 'servers.xml'))


    def parse_xml(self, xml_file):
        servers = []
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for server in root.findall('bibleserver'):
            server_dict = {}
            server_dict['name'] = server.find('name').text
            server_dict['url'] = server.find('url').text
            server_dict['chapterurl'] = server.find('chapterurl').text
            server_dict['status'] = server.find('status').text if server.find('status') is not None else 'active'
            server_dict['books'] = []
            for book in server.findall('books/book'):
                book_dict = {}
                book_dict['name_de'] = book.get('name_de')
                book_dict['name_en'] = book.get('name_en') if book.get('name_en') is not None else book.get('name_de')
                book_dict['name_extra'] = book.get('name_extra') if book.get('name_extra') is not None else book.get('name_de')
                book_dict['abbreviation'] = book.text
                server_dict['books'].append(book_dict)
            servers.append(server_dict)
        return servers

    def get_servers(self):
        return self._servers


    def get_server_by_name(self, n):
        name = n.lower()
        for srv in self._servers:
            if name == srv['name'].lower():
                return srv
        return None