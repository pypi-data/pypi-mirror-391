import sys
import threading
import time
import xml.etree.ElementTree as ET
import requests
import zipfile
import lokalise
from io import BytesIO

from cli.entities.setting import Settings
from cli.utils.singleton import singleton


def show_loading_spinner(is_loading, message="Loading, please wait ..."):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    while is_loading.is_set():
        for char in spinner:
            sys.stdout.write(f'\r{char} {message}')
            time.sleep(0.1)
            sys.stdout.flush()
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    sys.stdout.flush()


@singleton
class Lokalise:

    def __init__(self, settings=Settings()):
        self.credentials = settings.get_lokalise_credentials()
        self.client = lokalise.Client(self.credentials['api_token'])

    def create_keys(self):
        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Adding keys to lokalise ..."))
        spinner_thread.start()

        xml_file = 'strings_aux.xml'
        try:
            keys = self.client.create_keys(self.credentials['project_id'], self.parse_xml_to_array(xml_file))
        finally:
            is_loading.clear()
            spinner_thread.join()
            self.delete_string_tag(xml_file)

        return keys

    @staticmethod
    def delete_string_tag(xml_file):
        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Deleting tags ..."))
        spinner_thread.start()

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for string in root.findall('string'):
                root.remove(string)
        finally:
            is_loading.clear()
            spinner_thread.join()

        tree.write(xml_file, encoding='utf-8', xml_declaration=True)

    @staticmethod
    def parse_xml_to_array(xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        array = []

        for string in root.findall('string'):
            key_name = string.get('name')
            translation = string.text

            item = {
                "key_name": key_name,
                "platforms": ["android", "web"],
                "translations": [
                    {
                        "language_iso": "en",
                        "translation": translation
                    }
                ],
                "filenames": {
                    "android": "%LANG_ISO%.xml"
                }
            }

            array.append(item)

        return array

    @staticmethod
    def get_lokalise_files(self):
        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Downloading files ..."))
        spinner_thread.start()

        try:
            client = lokalise.Client(self.credentials['api_token'])
            files = self.client.download_files_async(self.credentials['project_id'], {
                "format": "xml",
                "original_filenames": True,
                "replace_breaks": False,
                "export_empty_as": "skip"
            })

            while True:
                process_info = self.client.queued_process(
                    self.credentials['project_id'],
                    files.process_id
                )

                if process_info.status == "finished":
                    download_url = process_info.details["download_url"]
                    print(download_url)
                    if not download_url:
                        raise RuntimeError("Proceso finalizado pero sin 'download_url' en 'details'")
                    return download_url
        finally:
            is_loading.clear()
            spinner_thread.join()

    @staticmethod
    def get_bundle_url(files):
        url = files['bundle_url']
        return url

    @staticmethod
    def download_translations_files(url):
        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Downloading files ..."))
        spinner_thread.start()

        try:
            response = requests.get(url)
            response.raise_for_status()  #
        finally:
            is_loading.clear()
            spinner_thread.join()

        return response.content

    @staticmethod
    def extract_translation_files(zip_content):
        """Extract translation files to the project directory."""
        zip_file = zipfile.ZipFile(BytesIO(zip_content))
        translations = {
            "values/strings.xml": "values-en/strings.xml",
            "values-es/strings.xml": "values-es/strings.xml",
            "values-pt/strings.xml": "values-pt/strings.xml",
            "values-es-rAR/strings.xml": "values-es-rAR/strings.xml",
            "values-da/strings.xml": "values-da/strings.xml",
        }

        for zip_info in zip_file.infolist():
            if zip_info.filename in translations:
                zip_info.filename = translations[zip_info.filename]
                zip_file.extract(zip_info, 'core/common/src/main/res')
                print(f"Extracted: {zip_info.filename}")

    def generate_translations_files(self):
        bundle_url = self.get_lokalise_files(self)
        zip_content = self.download_translations_files(bundle_url)
        # extracting the zip file contents
        self.extract_translation_files(zip_content)

        is_loading = threading.Event()
        is_loading.set()

        spinner_thread = threading.Thread(target=show_loading_spinner, args=(is_loading, "Extracting the files ..."))
        spinner_thread.start()

        is_loading.clear()
        spinner_thread.join()
