from .remarkable_structures import basic_file_ext_content_file_name, \
    basic_file_ext_content, \
    default_page_data, \
    default_pdf_data
from .utils import construct_zip_payload
from requests import Session
from uuid import uuid4
from os.path import isfile, basename
import logging
import coloredlogs


class ReMarkableCloud:
    _document_storage_host = 'document-storage-production-dot-remarkable-production.appspot.com'
    _webapp_host = 'webapp-production-dot-remarkable-production.appspot.com'
    schema = 'https'
    endpoints = {
        'document_storage': {
            'update-status': 'document-storage/json/2/upload/update-status',
            'upload-request': 'document-storage/json/2/upload/request',
        },
        'webapp': {
            'new-user-token': 'token/json/2/user/new'
        }
    }

    def __init__(self, device_token: str, user_token: str = None):
        self.logger = logging.getLogger(__name__)
        coloredlogs.install('INFO', logger=self.logger)
        self.session = Session()
        self.device_token = device_token
        self.user_token = user_token
        self.basic_headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'accept': '*/*',
            'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
            'origin': 'chrome-extension://bfhkfdnddlhfippjbflipboognpdpoeh',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
        }
        self.session.headers = self.basic_headers

    @property
    def storage_server(self):
        return self._document_storage_host

    @storage_server.setter
    def storage_server(self, server: str):
        self._document_storage_host = server

    @property
    def storage_baseurl(self):
        return f'{self.schema}://{self.storage_server}'

    @property
    def webapp_server(self):
        return self._webapp_host

    @webapp_server.setter
    def webapp_server(self, server: str):
        self._webapp_host = server

    @property
    def webapp_baseurl(self):
        return f'{self.schema}://{self.webapp_server}'

    def obtain_user_token(self):
        headers = {
            'Accept': '*/*',
            'Accept-encoding': 'gzip, deflate, br',
            'Accept-language': 'en-GB,en;q=0.9,es-ES;q=0.8,es;q=0.7,en-US;q=0.6',
            'Authorization': f'Bearer {self.device_token}'
        }
        self.session.headers = headers
        response = self.session.post(f"{self.webapp_baseurl}/{self.endpoints['webapp']['new-user-token']}")
        if response.status_code == 200:
            self.user_token = response.text
            return True
        else:
            self.logger.critical('Unable to retrieve new user token with provided device token.')
            return False

    def del_authorization_header(self):
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
            return True
        return False

    def set_device_token_header(self):
        self.session.headers['Authorization'] = f'Bearer {self.device_token}'

    def set_user_token_header(self):
        self.session.headers['Authorization'] = f'Bearer {self.user_token}'

    def upload_file(self, file_path, file_uuid=None, override_file_name: str = None):
        if not isfile(file_path):
            self.logger.critical(f'File «{file_path}» not found')
            return False
        if not file_uuid:
            file_uuid = str(uuid4())
        blob_url = None
        url = f"{self.storage_baseurl}/{self.endpoints['document_storage']['upload-request']}"
        data = [{'ID': file_uuid, 'Version': 1}]
        if not self.user_token:
            if not self.obtain_user_token():
                return False
        self.set_user_token_header()

        self.logger.info(f"[{file_uuid}] {file_path}")

        upload_request = self.session.put(url, json=data)

        # One retry if we get a 401 due to invalid user token
        if upload_request.status_code == 401:
            if self.obtain_user_token():
                upload_request = self.session.put(url, json=data)
        if upload_request.status_code == 200:
            response = upload_request.json()
            if type(response) == list and len(response) == 1:
                response = response[0]
            if 'Success' in response:
                self.logger.info(f"[{file_uuid}]: Request success: {response['Success']}")
                if response['Success']:
                    if 'BlobURLPut' in response:
                        blob_url = response['BlobURLPut']
        self.del_authorization_header()

        if blob_url:
            pk1_file_content = basic_file_ext_content_file_name.replace("{{UUID}}", file_uuid)
            pk2_file_pagedata = default_page_data.replace("{{UUID}}", file_uuid)
            pk3_pdf_name = default_pdf_data.replace("{{UUID}}", file_uuid)
            files = [
                {
                    'name': pk1_file_content,
                    'content': basic_file_ext_content,
                },
                {
                    'name': pk2_file_pagedata,
                    'content': '',
                },
                {
                    'name': pk3_pdf_name,
                    'content': open(file_path, 'rb')
                }
            ]
            blob_data = construct_zip_payload(files=files)
            blob_put = self.session.put(blob_url, data=blob_data.getvalue())

            # If DEBUG level is set, try writing blob file to /tmp/blob.zip.
            if self.logger.getEffectiveLevel() == 10:
                open('/tmp/blob.zip', 'wb').write(blob_data.getvalue())

            if blob_put.status_code == 200:
                self.logger.info(f"[{file_uuid}]: File upload to the cloud. Setting file name.")
                if override_file_name:
                    file_name = override_file_name
                else:
                    file_name = basename(file_path)
                self.set_name_for_uuid(file_uuid, file_name)
        self.del_authorization_header()
        return file_uuid

    def set_name_for_uuid(self, uuid: str, visible_name: str, version: int = 1):
        self.set_user_token_header()
        url = f"{self.storage_baseurl}/{self.endpoints['document_storage']['update-status']}"
        data = [{'ID': uuid, 'Type': 'DocumentType', 'Version': 1, 'VissibleName': visible_name}]
        set_name_request = self.session.put(url=url, json=data)
        if set_name_request.status_code == 200:
            self.logger.info(f"[{uuid}]: File named «{visible_name}»")
            # TODO: add some basic checks!!!
        self.del_authorization_header()
