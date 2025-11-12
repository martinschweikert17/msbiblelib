# Everything about Bible versions
import os
import xml.etree.ElementTree as ET


class Versions:
    def __init__(self):

        # Read the versions data from the xml file. As this is a package, we need to use the absolute path
        cwd = os.path.dirname(os.path.abspath(__file__))
        self._versions = self.parse_xml(os.path.join(cwd, 'versions.xml'))


    def parse_xml(self, xml_file):
        versions = []
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for version in root.findall('version'):
            version_dict = {}
            version_dict['name'] = version.find('name').text
            version_dict['servername'] = version.find('servername').text
            version_dict['language'] = version.find('language').text
            version_dict['content'] = version.find('content').text
            version_dict['server'] = version.find('server').text
            version_dict['fullname'] = version.find('fullname').text
            extracontent_elem = version.find('extracontent')
            if extracontent_elem is not None:
                # PyCharm complains about the next line. Just ignore - it works
                version_dict['extracontent'] = extracontent_elem.text.split(',')
            else:
                version_dict['extracontent'] = None
            versions.append(version_dict)
        return versions


    def get_versions_filtered(self, vfilter, lfilter, sfilter):
        """

        :param vfilter: list of versions
        :param lfilter: list of languages
        :param sfilter: name of a Bible server
        :return:
        """

        # ToDo: validate version name

        version_filter = None
        language_filter = None
        server_filter = None


        # Anything to do?
        # For comparisons we need the arguments lower case
        if vfilter is None or vfilter == []:
            b_filter_by_version = False
        else:
            b_filter_by_version = True
            version_filter = [s.lower() for s in vfilter]

        if lfilter is None or lfilter == []:
            b_filter_by_language = False
        else:
            b_filter_by_language = True
            language_filter = [s.lower() for s in lfilter]

        if server_filter is None:
            b_filter_by_server = False
        else:
            b_filter_by_server = True
            server_filter = sfilter.lower()

        # No filters - return the whole list
        if b_filter_by_version == False and b_filter_by_language == False and b_filter_by_server == False:
            return self._versions

        a_selected_versions = []

        # It makes no sense to filter by both version and language - but like this the procedure is the same
        # for both filters
        # Iterate through the versions and select those that match the filters
        for v in self._versions:

            # If they want specific versions, no other filters need to be tested.
            # If a version is in their list, we take it
            if b_filter_by_version:

                if v['name'].lower() in version_filter:
                    a_selected_versions.append(v)

            # So they want to filter by language or by server (maybe both)
            else:
                # Initialize flags to determine if the current dictionary matches the filters
                language_match = True
                server_match = True

                # Check the language filter if enabled
                if b_filter_by_language:
                    language_match = v.get('language').lower() in language_filter

                # Check the server filter if enabled
                if b_filter_by_server:
                    server_match = v.get('server').lower() == server_filter

                # If both conditions are met, add the dictionary to a_selected_versions
                if language_match and server_match:
                    a_selected_versions.append(v)

        return a_selected_versions

    def get_versions(self):
        return self._versions

    def get_version_record(self, name):
        for version in self._versions:
            if version.get('name', '').lower() == name.lower():
                return version
        return None


    def get_version_language(self, name):
        for version in self._versions:
            if version.get('name', '').lower() == name.lower():
                return version.get('language')
        return None

    def get_version_content(self, name):
        for version in self._versions:
            if version.get('name', '').lower() == name.lower():
                return version.get('content')
        return None

    def get_version_extracontent(self, name):
        for version in self._versions:
            if version.get('name', '').lower() == name.lower():
                return version.get('extracontent')
        return None

    def get_version_server(self, name):
        for version in self._versions:
            if version.get('name', '').lower() == name.lower():
                return version.get('server')
        return None


    def get_hosting_server(self, ver):
        """

        :param ver: Bible version name
        :return: dictionary with information about the hosting server
        """
        # Search the version records for the given name
        for v in self._versions:
            if v['name'] == ver['name']:
                return v
        return None
