# encoding: utf-8
from lxml import etree
import requests
from StringIO import StringIO
import xmltodict

class LinkInfo(object):
    def __init__(self, file, url):
        """
        :param file: string
        :param url: string
        :return:
        """
        # File
        self.file = file
        # URL
        self.url = url

    def to_xml_element(self):
        """
        :return: etree.Element
        """
        root = etree.Element('Source')
        root.attrib['File'] = self.file
        root.attrib['URL'] = self.url
        return root


class PermissionsInfo(object):
    def __init__(self, allow_copy_to_clipboard, allow_print, deny_print_message=u'You do not have permission to print'):
        """
        :param allow_copy_to_clipboard: bool
        :param allow_print: bool
        :param deny_print_message: String
        :return:
        """
        # AllowCopyToClipboard
        self.allow_copy_to_clipboard = allow_copy_to_clipboard
        # AllowPrint
        self.allow_print = allow_print
        # DenyPrintMessage
        self.deny_print_message = deny_print_message

    def to_xml_element(self):
        """
        :return: etree.Element
        """
        root = etree.Element('Permissions')
        allow_copy_to_clipboard_element = etree.SubElement(root, 'AllowCopyToClipboard')
        allow_copy_to_clipboard_element.text = unicode(self.allow_copy_to_clipboard).lower()


        allow_print_element = etree.SubElement(root, 'AllowPrint')
        allow_print_element.text = unicode(self.allow_print).lower()

        deny_print_message_element = etree.SubElement(root, 'DenyPrintMessage')
        deny_print_message_element.text = unicode(self.deny_print_message).lower()

        return root

class DownloadInfo(object):
    def __init__(self, format, size, url, deny_message=u'Access denied'):
        """
        :param deny_message: string
        :param format: string
        :param size: long
        :param url: string
        :return:
        """
        # DenyMessage
        self.deny_message = deny_message
        # Format
        self.format = format
        # Size
        self.size = size
        # URL
        self.url = url

    def to_xml_element(self):
        """
        :return: etree.Element
        """
        root = etree.Element('Download')
        root.attrib['DenyMessage'] = self.deny_message
        root.attrib['Format'] = self.format
        root.attrib['Size'] = unicode(self.size)
        root.attrib['URL'] = self.url
        return root


class DocumentInfo(object):
    def __init__(self, link_info, file_url, key_url, print_url, permissions_info, token1, token2, provider_key1, downloads=list()):
        """
        :param link_info: LinkInfo object
        :param file_url: string
        :param key_url: string
        :param print_url: string
        :param permissions_info: PermissionsInfo object
        :param token1: string
        :param token2: string
        :param provider_key1: string
        :param downloads: DownloadInfo objects list
        :return:
        """
        # Version
        self.version = '1.0'
        # Source
        self.link_info = link_info
        # FileURL
        self.file_url = file_url
        # KeyURL
        self.key_url = key_url
        # PrintURL
        self.print_url = print_url
        # Permissions
        self.permissions_info = permissions_info
        # Token1
        self.token1 = token1
        # Token2
        self.token2 = token2
        # ProviderKey1
        self.provider_key1 = provider_key1
        # Download
        self.downloads = downloads


    def to_xml_element(self):
        root = etree.Element('Document')

        root.append(self.link_info.to_xml_element())

        file_url_element = etree.SubElement(root, 'FileURL')
        file_url_element.text = self.file_url

        key_url_element = etree.SubElement(root, 'KeyURL')
        key_url_element.text = self.key_url

        print_url_element = etree.SubElement(root, 'PrintURL')
        print_url_element.text = self.print_url

        root.append(self.permissions_info.to_xml_element())

        token1_element = etree.SubElement(root, 'Token1')
        token1_element.text = self.token1

        token2_element = etree.SubElement(root, 'Token2')
        token2_element.text = self.token2

        provider_key1_element = etree.SubElement(root, 'ProviderKey1')
        provider_key1_element.text = self.provider_key1

        downloads_element = etree.SubElement(root, 'Downloads')
        for download in self.downloads:
            downloads_element.append(download.to_xml_element())

        return root

class RBooksWebServiceClient(object):

    def __init__(self, url, documents_directory, code, extension='.edoc'):
        self.__url = url
        if not self.__url.endswith('/'):
            self.__url += '/'

        self.__documents_directory = documents_directory
        self.__code = code + extension


    def get_document_file_info(self):
        """
        Raw xml file info
        :return: string
        """
        path = "file.ashx"
        responce = requests.get(self.__url + path, params={
            'dir': self.__documents_directory,
            'code': self.__code
        })

        responce.raise_for_status()
        return responce.content


    def get_document_key(self, dh, sign):
        path = "key.ashx"
        responce = requests.post(self.__url + path, params={
            'dir': self.__documents_directory,
            'code': self.__code,
            'dh': dh,
            'sign': sign
        })

        responce.raise_for_status()
        return responce.content


    def get_document_picture(self, width=200, height=200):
        pass


    def get_documents_list(self):
        pass


    def get_public_key1_string(self):
        path = "key1.ashx"
        responce = requests.get(self.__url + path)

        responce.raise_for_status()
        return responce.content


    def sign_data(self, data_doc):
        path = "sign.ashx"
        responce = requests.post(self.__url + path, data=data_doc)
        responce.raise_for_status()
        return responce.content


    def get_document_part(self, part, encrypted=True):
        path = "part.ashx"
        # url = "%s%s/?dir=%s&code=%s&part=%s&enc=%s" % (
        #      self.__url,
        #      path,
        #      self.__documents_directory,
        #      self.__code,
        #      part,
        #      unicode(encrypted).lower()
        # )
        # return url
        responce = requests.get(
            self.__url + path,
            params={
                'dir': self.__documents_directory,
                'code': self.__code,
                'part': part,
                'enc': unicode(encrypted).lower()
            }
        )
        responce.raise_for_status()
        return responce.content


    def get_document_part_stream(self, part, encrypted=True):
        path = "part.ashx"
        responce = requests.get(
            self.__url + path,
            params={
                'dir': self.__documents_directory,
                'code': self.__code,
                'part': part,
                'enc': unicode(encrypted).lower()
            },
            stream=True
        )
        responce.raise_for_status()
        return responce.iter_lines()

