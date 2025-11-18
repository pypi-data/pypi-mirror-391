import asyncio
import json
import logging
import os
import re
import socket
from copy import deepcopy
from datetime import datetime
from json import JSONDecodeError
from logging.config import dictConfig

import httpx
from httpx import Response
from sysnet_pyutils.data_utils import get_dict_item_value_list
from sysnet_pyutils.utils import who_am_i, Singleton, LoggedObject, is_valid_uuid, is_valid_pid, is_valid_unid
from urllib3.exceptions import NewConnectionError

APP_NAME = 'CITES DDS CONNECTOR'

REMOVED_PREFIX = 'removed_'
RESOURCE_DB = '/api/data'
BIG_LIMIT = 1000
NOT_READY = 'DOMINO server not ready'

try:
    DDS_TIMEOUT = int(os.getenv("DDS_TIMEOUT", "120"))
except ValueError:
    DDS_TIMEOUT = 0  # fallback


DDS_PREFIX = 'dds'
VIEW_PID = f'{DDS_PREFIX}-pid'
VIEW_IDNO = f'{DDS_PREFIX}-idno'
VIEW_UUID = f'{DDS_PREFIX}-identifier'
VIEW_FORM = f'{DDS_PREFIX}-form'
VIEW_KEY = f'{DDS_PREFIX}-key'
VIEW_RESPONSES = f'{DDS_PREFIX}-responses'
VIEW_REQUESTS = f'{DDS_PREFIX}-req'
VIEW_REQUESTS_GOODS = f'{DDS_PREFIX}-req-goods'
VIEW_ADDITIONAL = f'{DDS_PREFIX}-additional'
VIEW_REGCERT = f'{DDS_PREFIX}-regcert'
VIEW_STATEMENT_PERMIT = f'{DDS_PREFIX}-pid-statements'
VIEW_GOODS = f'{DDS_PREFIX}-goods'
VIEW_GOODS_PID = f'{DDS_PREFIX}-goods-pid'
VIEW_GOODS_EXTERNAL = f'{DDS_PREFIX}-goods-external'
VIEW_GOODS_EXTERNAL_PID = f'{DDS_PREFIX}-goods-external-pid'
VIEW_PERMITS = f'{DDS_PREFIX}-permits'
VIEW_PERMITS_PID = f'{DDS_PREFIX}-permits-pid'
VIEW_PERMITS_EXTERNAL = f'{DDS_PREFIX}-permits-external'
VIEW_PERMITS_EXTERNAL_PID = f'{DDS_PREFIX}-permits-external-pid'

DDS_DOCUMENTS = 'documents'
DDS_PERMITS = 'permits'
DDS_CERT_REG = 'cert_reg'
DDS_STATEMENTS = 'statements'

DDS_FORMS = {
    DDS_DOCUMENTS: [
        'documents',
        'certificate-leg',
        'certificate-mov',
        'certification-leg',
        'exhibition',
        'instrument',
        'ownership',
        'sample', ],
    DDS_PERMITS: [
        'permit',
        'request',
        'statement_general',
        'goods',
        'statement', ],
    DDS_CERT_REG: [
        'cert_reg',
        'certificate',
        'regcertcover',
        'registration',
        'additionalRecord',
        'discard',
        'holderChange',
        'holderCheckout',
        'personalRecord',
        'regcertrequest',
        'rejection', ],
    DDS_STATEMENTS: [
        'statements',
        'request',
        'item',
        'statement', ]
}


CONFIG_DDS_DOCUMENTS = f'dds_{DDS_DOCUMENTS}'
CONFIG_DDS_PERMITS = f'dds_{DDS_PERMITS}'
CONFIG_DDS_CERT_REG = f'dds_{DDS_CERT_REG}'
CONFIG_DDS_STATEMENTS = f'dds_{DDS_STATEMENTS}'

CONFIG_USERNAME = 'user'
CONFIG_PASSWORD = 'password'
CONFIG_REPID = 'repid'
CONFIG_URL = 'url'

LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler'],
        },
        'DDS FACTORY': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['info_console_handler'],
        },
        'DDS SOURCE': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['info_console_handler'],
        },
        'DDS_FACTORY': {
            'level': 'INFO',
            'propagate': False,
            'handlers': ['info_console_handler'],
        },
        'DDS_SOURCE': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['info_console_handler'],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_console_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s %(levelname)-4s [%(filename)s:%(lineno)d] %(message)s',
            # 'format': '%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'error': {
            'format': '%(asctime)s %(levelname)s %(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
}

dictConfig(LOGGING_CONFIG)

LOGGER = logging.getLogger(__name__)

LOGGER.info('DDS START')


class DdsSource(LoggedObject):
    def __init__(self, name, url, user, password, repid, object_name='DDS SOURCE', big_limit=BIG_LIMIT,
                 app_name=APP_NAME):
        super().__init__(object_name=object_name)
        self.source_name = name
        self.app_name = app_name
        self.url = url
        self.user = user
        self.password = password
        self.repid = repid
        self._ready = False
        self._auth = None
        self._logger = self._logger = LOGGER.getChild(self.name)
        self._services = None
        self._core = None
        self._collections = None
        self.storages = []
        self._database = None
        self.big_limit = big_limit
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json"
        }
        self.db_file_path = None
        self.db_title = None
        self.log.info(f"{self.name}.{self.source_name} created by lazy constructor.")

    async def update_source(self):
        if (self.db_file_path is None) or (self.db_title is None):
            try:
                db = await self.get_database()
                self.db_file_path = db['@filepath']
                self.db_title = db['@title']
            except Exception as e:
                self.log.error(f"{self.name}.{self.source_name} update failed: {type(e)} - {str(e)}.")
                raise DdsError(status=500, message=f"{self.name}.{self.source_name} update failed: {type(e)} - {str(e)}")

    async def ready(self):
        if not self._ready:
            await self.get_db_collection()
            await asyncio.sleep(1)
        return self._ready

    async def database(self):
        if self._database is None:
            self._database = await self.get_database()
        return self._database

    async def services(self):
        if self._services is None or not bool(self._services):
            self._services = await self.get_services()
        return self._services

    async def core(self):
        if self._core is None or not bool(self._core):
            self._core = await self.get_core()
        return self._core

    async def collections(self):
        if self._collections is None or not bool(self._collections):
            self._collections = await self.get_collections()
        return self._collections

    async def info(self):
        status = "RED"
        out = {'data': False, 'repid': self.repid, 'server': self.url}
        if await self.ready():
            status = "GREEN"
            db = await self.database()
            if db is not None:
                out['database'] = db['@title']
                ss = await self.services()
                for service in ss['services']:
                    if service['name'] == 'Data':
                        out['data'] = service['enabled']
                        out['version'] = service['version']
                        break
        out['status'] = status
        return out

    @property
    def auth(self):
        if (self._auth is None) and (self.user is not None) and (self.password is not None):
            self._auth = (self.user, self.password)
        return self._auth

    async def get_db_collection(self):
        # Tady se kontroluje, jestli je domino ready
        # out = None
        __name__ = who_am_i()
        try:
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                response = await client.get(url=f"{self.url}{RESOURCE_DB}")
            if response.status_code != 200:
                raise DdsError(status=response.status_code, message=f"DDS '{self.name}': {str(response)}")
            out = json.loads(response.text)
            self._ready = True
        except (httpx.ConnectError, httpx.HTTPError) as e:
            out = None
            self._ready = False
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {str(e)}")
        except DdsError as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - DDS ERROR: {str(e)}")
            raise DdsError(status=e.status, message=e.message)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")
        return out

    async def get_database(self, repid=None):
        __name__ = who_am_i()
        if repid in [None, '']:
            repid = self.repid
        col = await self.get_db_collection()
        out = None
        for item in col:
            if item['@replicaid'] == repid:
                out = item
                break
        return out

    async def _get_resource(self, resource='api'):
        __name__ = who_am_i()
        if not await self.ready():
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - Source not ready")
            return None
        uri = f"{self.url}/{resource}"
        try:
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                response = await client.get(url=uri, timeout=DDS_TIMEOUT)
            if response is None:
                self.log.error(f"{self.name}.{self.source_name}.{__name__} - {uri}: Nothing returned")
                return None
            if response.status_code != 200:
                self.log.error(
                    f"{self.name}.{self.source_name}.{__name__} uri: {uri} - status: {response.status_code}, msg: {response.text}")
                return None
            out = json.loads(response.text)
            self.log.debug(f"{self.name}.{self.source_name}.{__name__} uri: {uri} - {str(out)}")
            return out
        except (httpx.RequestError, NewConnectionError, socket.gaierror, TimeoutError) as e:
            # except (RequestException, NewConnectionError, socket.gaierror, TimeoutError) as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} uri: {uri} - {str(e)}")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            # raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")
            return None

    async def get_services(self):
        return await self._get_resource(resource='api')

    async def get_core(self):
        return await self._get_resource(resource='api/core')

    async def get_collections(self):
        __name__ = who_am_i()
        if await self.database() is None:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - Database is None")
        if '@href' not in await self.database():
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - Database is not loaded")
        db = await self.database()
        return await self._get_resource(resource=db['@href'])

    async def get_data_service(self):
        out = None
        ss = await self.services()
        for service in ss['services']:
            if service['name'] == 'Data':
                out = service
                break
        return out

    async def patch_document(self, unid=None, form=None, compute_with_form=False, data_dict=None):
        # partially update document
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        if unid is None:
            raise DdsError(message='UNID must not be None')
        if data_dict is None:
            raise DdsError(message='data must not be None')
        await self.update_source()
        try:
            if form is not None:
                cwf = ''
                if compute_with_form:
                    cwf = '&computewithform=true'
                uri = f"{self.url}/{self.db_file_path}/api/data/documents/unid/{unid}?form={form}{cwf}"
            else:
                uri = f"{self.url}/{self.db_file_path}/api/data/documents/unid/{unid}"
            json_data = json.dumps(data_dict)
            headers = {'Cache-Control': 'no-cache', 'Content-type': 'application/json', 'X-HTTP-Method-Override': 'PATCH'}
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                response: Response = await client.patch(url=uri, auth=self.auth, json=json_data, headers=headers)
            if response.status_code != 200:
                json_obj = json.loads(response.text)
                self.log.error(
                    f"{self.name}.{self.source_name}.{__name__} - status: {response.status_code}, msg: {json_obj['message']}")
                raise DdsError(status=response.status_code, message=json_obj['message'], module=__name__)
            self.log.debug(
                f"{self.name}.{self.source_name}.{__name__} - URL:{uri}, status: {response.status_code}, reason: {response.text}")
            return response
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)} - {str(e)}")
            raise DdsError(status=400, message=e.response.text)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)} - {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)} - {str(e)}")

    async def put_document(self, unid=None, form=None, compute_with_form=False, data_dict=None):
        # update document
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        if unid is None:
            raise DdsError(message='UNID must not be None')
        if form is None:
            raise DdsError(message='form must not be None')
        if data_dict is None:
            raise DdsError(message='data must not be None')
        cwf = ''
        if compute_with_form:
            cwf = '&computewithform=true'
        await self.update_source()
        try:
            uri = f"{self.url}/{self.db_file_path}/api/data/documents/unid/{unid}?form={form}{cwf}"
            json_data = json.dumps(data_dict)
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                response = await client.put(url=uri, auth=self.auth, json=json_data, headers=self.headers)
            # self.log.debug(f"{self.name}.{self.source_name}.{__name__} - PUT: {response.status_code}")
            if response.status_code != 200:
                json_obj = json.loads(response.text)
                self.log.error(
                    f"{self.name}.{self.source_name}.{__name__} - status: {response.status_code}, msg: {json_obj['message']}")
                raise DdsError(status=response.status_code, message=json_obj['message'], module=__name__)
            self.log.debug(
                f"{self.name}.{self.source_name}.{__name__} - URL:{uri}, status: {response.status_code}, reason: {response.text}")
            return True
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            # except (RequestException, NewConnectionError, socket.gaierror) as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {str(e)}")
            raise DdsError(status=400, message=e.response.text)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)} - {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)} - {str(e)}")

    async def post_document(self, form=None, compute_with_form=False, parent_id=None, data_dict=None):
        # create a new document
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        if form is None:
            raise DdsError(message='form must not be None')
        if data_dict is None:
            raise DdsError(message='data must not be None')
        parent = ''
        if parent_id is not None:
            parent_unid = self.get_parent_unid(parent_id)  # konsolidace parent_id
            parent = f"&parentid={parent_unid}"
        await self.update_source()
        try:
            uri = f"{self.url}/{self.db_file_path}/api/data/documents?form={form}&computewithform={str(compute_with_form).lower()}{parent}"
            json_data = json.dumps(data_dict)
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                try:
                    response = await client.post(url=uri, auth=self.auth, json=json_data, headers=self.headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    raise DdsError(status=err.response.status_code, message=err.response.text, module=__name__)
            if response.status_code == 201:
                out = response.headers['Location']
                self.log.debug(f"{__name__} - URL:{uri}, status: {response.status_code}, reason: {response.text}")
                return out
            else:
                # json_obj = json.loads(response.text)
                # raise DocError(status=response.status_code, message=json_obj['message'], module=__name__)
                raise DdsError(status=response.status_code, message=response.text, module=__name__)
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            raise DdsError(status=400, message=e.response.text, module=__name__)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")

    async def get_parent_unid(self, parent_identifier):
        parent_doc = await self.get_parent_doc(parent_identifier=parent_identifier)
        out = parent_doc['@unid']
        return out

    async def get_parent_doc(self, parent_identifier):
        if parent_identifier is None:
            raise DdsError(status=404, message='Parent identifier is None')
        parent_doc = await self.get_document_by_identifier(identifier=parent_identifier)
        if parent_doc is None:
            raise DdsError(
                status=404, message='Parent document does not exist {}'.format(parent_identifier))
        return parent_doc

    async def get_document_by_identifier(self, identifier):
        __name__ = who_am_i()
        if identifier is None:
            return None
        if is_valid_uuid(identifier):
            LOGGER.debug('{} - identifier: {}'.format(__name__, identifier))
            out = await self.get_document_by_idno(identifier)
        elif is_valid_pid(identifier):
            LOGGER.debug('{} - pid: {}'.format(__name__, identifier))
            out = await self.get_document_by_pid(identifier)
        elif is_valid_unid(identifier):
            LOGGER.debug('{} - unid: {}'.format(__name__, identifier))
            out = await self.get_document(identifier)
        else:
            raise DdsError(status=404, message='Document identifier {} is invalid'.format(identifier))
        return out

    async def get_document(self, unid=None):
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        if unid is None:
            raise DdsError(status=400, message='Invalid attribute UNIID')
        try:
            await self.update_source()
            uri = f"{self.url}/{self.db_file_path}/api/data/documents/unid/{unid}?attachmentlinks=true"
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                try:
                    response = await client.get(url=uri, auth=self.auth, headers=self.headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    raise DdsError(status=err.response.status_code, message=err.response.text, module=__name__)
            out = json.loads(response.text)
            if response.status_code != 200:
                raise DdsError(status=response.status_code, message=out['message'])
            self.log.debug(f"{self.name}.{__name__} - URL:{uri}, status: {response.status_code}, reason: {response.text}")
            return out
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            raise DdsError(status=400, message=e.response.text, module=__name__)
        except JSONDecodeError as e:
            self.log.error(f"{self.name}.{__name__} Chyba dekódování dokumentu: {unid} \n{str(e)}")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")

    async def get_document_by_pid(self, pid=None):
        out = await self.get_document_by_key(view_name=VIEW_PID, key=pid)
        return out

    #    def get_document_by_crzp(self, crzp=None):
    #        out = self.get_document_by_key(view_name=VIEW_CRZP, key=crzp)
    #        return out

    async def get_document_by_idno(self, idno=None, view_name=VIEW_IDNO):
        key = idno.replace('_', '/')
        out = await self.get_document_by_key(view_name=view_name, key=key)
        return out

    async def get_document_by_uuid(self, uuid=None):
        out = await self.get_document_by_key(view_name=VIEW_UUID, key=uuid)
        return out

    async def get_document_by_key(self, view_name=None, key=None):
        out = None
        entry = await self.get_entry_by_key(view_name=view_name, key=key, exact_match=True)
        if entry is not None:
            out = await self.get_document(unid=entry['@unid'])
        return out

    async def get_entry_by_key(self, view_name=None, key=None, exact_match=True):
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        # print(f"{self.name}.{__name__} - DATABASE READY")
        if (view_name is None) or (key is None):
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - Missing view_name or key")
            return None
        await self.update_source()
        try:
            if exact_match:
                uri = f"{self.url}/{self.db_file_path}/api/data/collections/name/{view_name}?keys={key}&keysexactmatch=true"
            else:
                uri = f"{self.url}/{self.db_file_path}/api/data/collections/name/{view_name}?keys={key}"
            self.log.info(f"{self.name}.{self.source_name}.{__name__} - uri: {uri}")
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                try:
                    response = await client.get(url=uri, auth=self.auth, headers=self.headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    raise DdsError(status=err.response.status_code, message=err.response.text, module=__name__)
            if response.status_code != 200:
                msg = f"Key '{key}' not found ({response.status_code}: {response.text})"
                self.log.warning(f"{self.name}.{self.source_name}.{__name__} - {msg}")
                return None
                # raise DocError(status=400, message=msg, module=__name__)
            entry_list = json.loads(response.text)
            if bool(entry_list):
                out = entry_list[0]
            else:
                msg = f"Key '{key}' not found in the view '{view_name}'"
                self.log.warning(f"{self.name}.{self.source_name}.{__name__} - {msg}")
                raise DdsError(status=404, message=msg, module=__name__)
            return out
        except DdsError as e:
            msg = f"{self.name}.{self.source_name}.{__name__} - DDS ERROR {e.status}: {e.message}"
            self.log.error(msg)
            return None
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            msg = f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}"
            self.log.error(msg)
            return None
        except Exception as e:
            msg = f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}"
            self.log.error(msg)
            return None

    async def get_entry_by_category(self, view_name=None, category=None):
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        if (view_name is None) or (category is None):
            return None
        try:
            await self.update_source()
            uri = f"{self.url}/{self.db_file_path}/api/data/collections/name/{view_name}?category={category}"
            self.log.debug(f"{self.name}.{__name__} - uri: {uri}")
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                try:
                    response = await client.get(url=uri, auth=self.auth, headers=self.headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    raise DdsError(status=err.response.status_code, message=err.response.text, module=__name__)
            if response.status_code != 200:
                raise DdsError(
                    status=400,
                    message='Key \"\" not found ({}: {})'.format(category, response.status_code, str(response)),
                    module=__name__)
            entry_list = json.loads(response.text)
            if bool(entry_list):
                out = entry_list[0]
            else:
                raise DdsError(
                    status=400,
                    message='Key \"{}\" not found in the view \"{}\"'.format(category, view_name),
                    module=__name__)
            return out
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            # except (RequestException, NewConnectionError, socket.gaierror) as e:
            raise DdsError(status=400, message=e.response.text, module=__name__)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")

    async def soft_delete_document(self, unid=None):
        # soft delete document
        __name__ = who_am_i()
        if unid is None:
            raise DdsError(message='UNID must not be None')
        doc = await self.get_document(unid=unid)
        form = doc['@form']
        if form.lower().startswith(REMOVED_PREFIX):
            raise DdsError(status=404, message='Document {} is already soft deleted'.format(unid))
        date_deleted = get_dict_item_value_list(data=doc, item_name='date_deleted')
        date_deleted.append(datetime.now().isoformat())
        doc['date_deleted'] = date_deleted
        deleted_by = get_dict_item_value_list(data=doc, item_name='deleted_by')
        deleted_by.append('{} ({})'.format(self.app_name, self.user))
        doc['deleted_by'] = deleted_by
        form = '{}{}'.format(REMOVED_PREFIX, form)
        success = self.put_document(unid=unid, form=form, compute_with_form=False, data_dict=doc)  # success True/False
        return success

    async def undelete_document(self, unid=None):
        # undelete soft deleted document
        __name__ = who_am_i()
        if unid is None:
            raise DdsError(message='UNID must not be None')
        doc = await self.get_document(unid=unid)
        form = doc['@form']
        if not form.lower().startswith(REMOVED_PREFIX):
            raise DdsError(status=404, message='Document {} is not soft deleted'.format(unid))
        date_undeleted = get_dict_item_value_list(data=doc, item_name='date_undeleted')
        date_undeleted.append(datetime.now().isoformat())
        doc['date_undeleted'] = date_undeleted
        undeleted_by = get_dict_item_value_list(data=doc, item_name='undeleted_by')
        undeleted_by.append('{} ({})'.format(self.app_name, self.user))
        doc['undeleted_by'] = undeleted_by
        form = form.split(REMOVED_PREFIX)[1]
        success = await self.put_document(unid=unid, form=form, compute_with_form=False, data_dict=doc)
        return success

    async def delete_document(self, unid=None):
        # delete document
        __name__ = who_am_i()
        if not await self.ready():
            msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
            self.log.error(msg)
            raise DdsError(status=503, message=msg)
        if unid is None:
            raise DdsError(message='UNID must not be None')
        try:
            await self.update_source()
            uri = f"{self.url}/{self.db_file_path}/api/data/documents/unid/{unid}"
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                try:
                    response = await client.get(url=uri, auth=self.auth, headers=self.headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    raise DdsError(status=err.response.status_code, message=err.response.text, module=__name__)
            if response.status_code == 200:
                out = response
                return out
            else:
                json_obj = json.loads(response.text)
                raise DdsError(status=response.status_code, message=json_obj['message'], module=__name__)
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            # except (RequestException, NewConnectionError, socket.gaierror) as e:
            raise DdsError(status=400, message=e.response.text, module=__name__)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")

    async def get_all_responses(self, parentid=None):
        __name__ = who_am_i()
        if parentid is None:
            return []
        try:
            out = await self.get_all_entries(view_name=VIEW_RESPONSES, key=parentid, page_size=100)
        except DdsError as e:
            msg = f"{self.name}.{__name__} - DDS ERROR {e.status}: {e.message}"
            self.log.error(msg)
            out = []
        except Exception as e:
            msg = f"{self.name}.{__name__} - ERROR {type(e)}: {str(e)}"
            self.log.error(msg)
            out = []
        return out



    async def get_all_responses_documents(self, parentid=None):
        out = []
        reply = await self.get_all_responses(parentid=parentid)
        for entry in reply['entries']:
            entry_dict = dict(entry)
            unid = entry_dict['@unid']
            parent_uuid = entry_dict['parent_uuid'] if 'parent_uuid' in entry_dict else None
            doc = await self.get_document(unid=unid)
            doc['parent_uuid'] = parent_uuid
            out.append(doc)
        return out

    async def get_all_entries(
            self, view_name=None, key=None, search=None, category=None, parentid=None,
            sortcolumn=None, sortorder='ascending',
            start=0, page_size=10, page=0, searchmaxdocs=BIG_LIMIT):
        __name__ = who_am_i()
        try:
            out = await self._get_all_entries_flexlimit(
                view_name=view_name, key=key, search=search, category=category, parentid=parentid,
                sortcolumn=sortcolumn, sortorder=sortorder, start=start, page_size=page_size, page=page,
                searchmaxdocs=searchmaxdocs, retry=False)
            if out is not None:
                if 'retry' in out:
                    if out['retry']:
                        searchmaxdocs = out['searchmaxdocs']
                        out = await self._get_all_entries_flexlimit(
                            view_name=view_name, search=search, category=category, parentid=parentid,
                            sortcolumn=sortcolumn, sortorder=sortorder, start=start, page_size=page_size, page=page,
                            searchmaxdocs=searchmaxdocs, retry=True)
            return out
        except DdsError as e:
            msg = f"{self.name}.{__name__} - DDS ERROR {e.status}: {e.message}"
            self.log.error(msg)
            return []
        except Exception as e:
            msg = f"{self.name}.{__name__} - ERROR {type(e)}: {str(e)}"
            self.log.error(msg)
            return []

    async def get_all_entries_by_category(self, view_name=None, category=None, start=0, page_size=100, page=0):
        __name__ = who_am_i()
        try:
            out = await self.get_all_entries(view_name=view_name, category=category, start=start, page_size=page_size, page=page)
        except DdsError as e:
            msg = f"{self.name}.{__name__} - DDS ERROR {e.status}: {e.message}"
            self.log.error(msg)
            out = []
        except Exception as e:
            msg = f"{self.name}.{__name__} - ERROR {type(e)}: {str(e)}"
            self.log.error(msg)
            out = []
        return out

    def check_limit(self, msg, retry, out, uri):
        if ('Limit exceeded' in msg) and not retry:
            num = re.findall(r'\d+', msg)
            if bool(num):
                searchmaxdocs = int(num[0])
                retry = True
                out['retry'] = retry
                out['searchmaxdocs'] = searchmaxdocs
                self.log.info(f"{__name__} - URL:{uri}, {msg}, retry with searchmaxdocs: {searchmaxdocs}")
                return out
        return None

    async def _get_all_entries_flexlimit(
            self, view_name=None, key=None, search=None, category=None, parentid=None,
            sortcolumn=None, sortorder='ascending',
            start=0, page_size=10, page=0, searchmaxdocs=BIG_LIMIT, retry=False):
        __name__ = who_am_i()
        out = None
        uri = None
        try:
            if not await self.ready():
                msg = f"{self.name}.{self.source_name}.{__name__} - {NOT_READY}"
                self.log.error(msg)
                raise DdsError(status=503, message=msg)
            if not retry:
                searchmaxdocs = self.big_limit
            await self.update_source()
            out = {
                'key': key,
                'search': search,
                'category': category,
                'parentid': parentid,
                'sortcolumn': sortcolumn,
                'sortorder': sortorder,
                'start': start,
                'page_size': page_size,
                'page': page,
                'searchmaxdocs': searchmaxdocs,
                'count': 0,
                'entries': [],
                'retry': retry
            }
            if view_name is None:
                return None
            if start is None:
                start = 0
            if page_size is None:
                page_size = 10
            if page is None:
                page = 0
            uri = f"{self.url}/{self.db_file_path}/api/data/collections/name/{view_name}?si={start}&ps={page_size}&page={page}"
            if key is not None:
                uri = f"{uri}&keys={key}"
            if search is not None:
                uri = f"{uri}&search={search}&searchmaxdocs={searchmaxdocs}"
            if category is not None:
                uri = f"{uri}&category={category}"
            if sortcolumn not in [None, '']:
                if sortorder not in ['ascending', 'descending']:
                    sortorder = 'ascending'
                uri = f"{uri}&sortcolumn={sortcolumn}&sortorder={sortorder}"

            LOGGER.debug(f"{self.name}{__name__} (start) - URL: {uri}")
            async with httpx.AsyncClient(auth=self.auth, headers=self.headers, timeout=DDS_TIMEOUT) as client:
                try:
                    response = await client.get(url=uri, auth=self.auth, headers=self.headers)
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    raise DdsError(status=err.response.status_code, message=err.response.text, module=__name__)
            if response.status_code != 200:
                if hasattr(response, 'text'):
                    msg = response.text
                    out = self.check_limit(msg=msg, retry=retry, out=out, uri=uri)
                    if out is not None:
                        return out
                raise DdsError(status=response.status_code, message=response.text, module=__name__)
            else:
                headers = response.headers
                if 'Content-Range' in headers:
                    cr = headers['Content-Range']
                    count = int(cr.split('/')[1])
                    out['count'] = count
                out['entries'] = json.loads(response.text)
                LOGGER.debug('{} (end) - URL:{}, status: {}, count: {}'.format(
                    __name__, uri, response.status_code, out['count']))
            return out
        except DdsError as e:
            raise DdsError(status=e.status, message=e.message, module=__name__)
        except (httpx.RequestError, NewConnectionError, socket.gaierror) as e:
            if hasattr(e, 'response'):
                if hasattr(e.response, 'text'):
                    msg = e.response.text
                    out = self.check_limit(msg=msg, retry=retry, out=out, uri=uri)
                    if out is not None:
                        return out
            msg = str(e)
            if hasattr(e, 'response'):
                msg = str(e.response)
                if hasattr(e.response, 'text'):
                    msg = e.response.text
            raise DdsError(status=400, message=msg, module=__name__)
        except Exception as e:
            self.log.error(f"{self.name}.{self.source_name}.{__name__} - {type(e)}: {str(e)}")
            raise DdsError(status=500, message=f"{self.name}.{self.source_name}.{__name__} - {type(e)}:{str(e)}")

class DdsFactory(LoggedObject, metaclass=Singleton):
    def __init__(self, object_name='DDS FACTORY', big_limit=BIG_LIMIT, config: dict = None, app_name=APP_NAME):
        super().__init__(object_name)
        self.config = config or {}
        self.app_name = app_name
        self.dds_list = [DDS_DOCUMENTS, DDS_PERMITS, DDS_STATEMENTS, DDS_CERT_REG]
        self._logger = LOGGER.getChild('DDS FACTORY')
        self.dds = {
            DDS_DOCUMENTS: DdsSource(
                name=DDS_DOCUMENTS,
                url=self.config[CONFIG_DDS_DOCUMENTS][CONFIG_URL],
                user=self.config[CONFIG_DDS_DOCUMENTS][CONFIG_USERNAME],
                password=self.config[CONFIG_DDS_DOCUMENTS][CONFIG_PASSWORD],
                repid=self.config[CONFIG_DDS_DOCUMENTS][CONFIG_REPID],
                big_limit=big_limit,
                app_name=self.app_name,
            ),
            DDS_PERMITS: DdsSource(
                name=DDS_PERMITS,
                url=self.config[CONFIG_DDS_PERMITS][CONFIG_URL],
                user=self.config[CONFIG_DDS_PERMITS][CONFIG_USERNAME],
                password=self.config[CONFIG_DDS_PERMITS][CONFIG_PASSWORD],
                repid=self.config[CONFIG_DDS_PERMITS][CONFIG_REPID],
                big_limit=big_limit
            ),
            DDS_STATEMENTS: DdsSource(
                name=DDS_STATEMENTS,
                url=self.config[CONFIG_DDS_STATEMENTS][CONFIG_URL],
                user=self.config[CONFIG_DDS_STATEMENTS][CONFIG_USERNAME],
                password=self.config[CONFIG_DDS_STATEMENTS][CONFIG_PASSWORD],
                repid=self.config[CONFIG_DDS_STATEMENTS][CONFIG_REPID],
                big_limit=big_limit
            ),
            DDS_CERT_REG: DdsSource(
                name=DDS_CERT_REG,
                url=self.config[CONFIG_DDS_CERT_REG][CONFIG_URL],
                user=self.config[CONFIG_DDS_CERT_REG][CONFIG_USERNAME],
                password=self.config[CONFIG_DDS_CERT_REG][CONFIG_PASSWORD],
                repid=self.config[CONFIG_DDS_CERT_REG][CONFIG_REPID],
                big_limit=big_limit
            ),
        }
        self.big_limit = big_limit
        self._ready = False
        self.log.info(f'{self.name} created by lazy constructor.')

    def is_ready(self):
        return self.ready

    async def ready(self):
        if not self._ready:
            i = j = 0
            for dds in self.dds_list:
                i += 1
                if await self.dds[dds].ready():
                    j += 1
            if (i > 0) and (i == j):
                self._ready = True
        return self._ready

    async def info(self):
        status = "RED"
        if await self.ready():
            status = "GREEN"
        out = {
            "status": status,
            "sources": {}
        }
        if (self.dds is not None) and (bool(self.dds)):
            ready = True
            for k, v in self.dds.items():
                info = await v.info()
                out["sources"][k] = info
                ready1 = await v.ready()
                ready = ready and ready1
            if ready:
                out["status"] = "GREEN"
        return out

    async def get_note_dda_dict(self, key):
        """
        Najde dokument Notes ve zdroji podle PID nebo UNID

        :param key: PID nebo UNID
        :return:    Pro případ permitu a žádosti o permit vrací tuple note a goods, jinak tuple note a None.
        """
        out = None, None
        if key in [None, '']:
            self.log.error(f"{self.name}.{__name__} Missing key.")
            return out
        where_found = None
        note = None
        if is_valid_unid(key):
            for k, v in self.dds.items():
                note = await v.get_document(unid=key)
                if note is not None:
                    where_found = k
                    break
        elif is_valid_pid(key):
            for k, v in self.dds.items():
                note = await v.get_document_by_pid(pid=key)
                if note is not None:
                    where_found = k
                    break
        else:
            self.log.error(f"{self.name}.{__name__} Invalid key: {key}.")
            return out
        if note is None:
            self.log.warning(f"{self.name}.{__name__} Document {key} not found.")
            return out
        pid = note['PID']
        form = note['@form']
        if form not in DDS_FORMS[where_found]:
            self.log.error(f"{self.name}.{__name__} Invalid form: {where_found}:{form}.")
            return out
        if where_found == DDS_PERMITS:
            if form == 'permit':
                external = True if ('external' in note) and (note['external'] == '1') else False
                goods = await self.get_permit_goods_dda_dict(pid_permit=pid, external=external)
                out = note, goods
            elif form == 'request':
                goods = await self.get_req_goods_dda_dict(pid_req=pid)
                out = note, goods
            elif form == 'statement':
                out = note, None
            else:
                self.log.error(f"{self.name}.{__name__} Not implemented form: {where_found}:{form}.")
                out = None, None
        elif where_found == DDS_STATEMENTS:
            note_sav = deepcopy(note)
            while '@parentid' in note:
                parent = deepcopy(note['@parentid'])
                note = await self.dds[where_found].get_document(unid=parent)
                if note is None:
                    self.log.error(f"{self.name}.{__name__} Missing declared parent: {where_found}:{parent}.")
                    return note_sav, None
            await self.get_statement_cert_request_responses_dict(note)
            out = note, None
        return out

    async def get_additional_dda_dict(self, key):
        __name__ = who_am_i()
        if key in [None, '']:
            self.log.error(f"{self.name}.{__name__} Missing key.")
            return None
        try:
            if is_valid_unid(key):
                reply = await self.dds[DDS_CERT_REG].get_document(unid=key)
            else:
                reply = await self.dds[DDS_CERT_REG].get_document_by_key(view_name=VIEW_ADDITIONAL, key=key)
            if reply is None:
                self.log.warning(f"{self.name}.{__name__} Document {key} not found.")
                return None
            return reply
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None


    async def get_regcert_dda_dict(self, key):
        __name__ = who_am_i()
        if key in [None, '']:
            self.log.error(f"{self.name}.{__name__} Missing key.")
            return None
        try:
            if is_valid_unid(key):
                reply = await self.dds[DDS_CERT_REG].get_document(unid=key)
            else:
                reply = await self.dds[DDS_CERT_REG].get_document_by_key(view_name=VIEW_PID, key=key)
            if reply is None:
                self.log.warning(f"{self.name}.{__name__} Document {key} not found.")
                return None, None
            return reply
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None


    async def get_statement_cert_request_responses_dict(self, parent):
        unid = parent['@unid']
        parent['@responses'] = []
        try:
            resp = await self.dds[DDS_STATEMENTS].get_all_entries(key=unid, view_name=VIEW_RESPONSES)
            for item in list(resp['entries']):
                resp_unid = item['@unid']
                doc = await self.dds[DDS_STATEMENTS].get_document(resp_unid)
                doc['@responses'] = []
                resp2 = await self.dds['statements'].get_all_entries(key=resp_unid, view_name=VIEW_RESPONSES)
                for resp_item in list(resp2['entries']):
                    doc2 = await self.dds[DDS_STATEMENTS].get_document(resp_item['@unid'])
                    doc['@responses'].append(doc2)
                parent['@responses'].append(doc)
            return parent
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None

    async def get_statement_cert_request_dict(self, key):
        __name__ = who_am_i()
        if key in [None, '']:
            self.log.error(f"{self.name}.{__name__} Missing key.")
            return None, None
        try:
            if is_valid_unid(key):
                reply = await self.dds[DDS_STATEMENTS].get_document(unid=key)
            else:
                reply = await self.dds[DDS_STATEMENTS].get_document_by_key(view_name=VIEW_PID, key=key)
            if reply is None:
                self.log.warning(f"{self.name}.{__name__} Document {key} not found.")
                return None, None
            reply = await self.get_statement_cert_request_responses_dict(parent=reply)
            return reply
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None

    async def get_statement_permit_dda_dict(self, key):
        __name__ = who_am_i()
        if key in [None, '']:
            self.log.error(f"{self.name}.{__name__} Missing key.")
            return None
        try:
            reply = await self.dds[DDS_PERMITS].get_document_by_key(view_name=VIEW_STATEMENT_PERMIT, key=key)
            if reply is None:
                self.log.warning(f"{self.name}.{__name__} Document {key} not found.")
                return None
            return reply
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None

    async def get_req_goods_dda_dict(self, pid_req):
        __name__ = who_am_i()
        try:
            goods_req = await self.dds[DDS_PERMITS].get_all_entries(
                view_name=VIEW_REQUESTS_GOODS, key=pid_req, start=0, page_size=100, page=0)
            if (goods_req is None) or (goods_req['count'] == 0):
                return None
            goods = []
            entries = goods_req['entries']
            for entry in entries:
                if isinstance(entry, dict) and ('@unid' in entry):
                    unid = entry['@unid']
                    g = await self.dds[DDS_PERMITS].get_document(unid=unid)
                    goods.append(g)
            return goods
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None

    async def get_req_dda_dict(self, key):
        __name__ = who_am_i()
        if key in [None, '']:
            self.log.error(f"{self.name}.{__name__} Missing key.")
            return None, None
        try:
            if is_valid_unid(key):
                req = await self.dds[DDS_PERMITS].get_document(unid=key)
            else:
                req = await self.dds[DDS_PERMITS].get_document_by_key(view_name=VIEW_REQUESTS, key=key)
            if req is None:
                self.log.warning(f"{self.name}.{__name__} Request {key} not found.")
                return None, None
            pid = req['PID']
            goods = await self.get_req_goods_dda_dict(pid_req=pid)
            if goods is None:
                self.log.warning(f"{self.name}.{__name__} Goods for Request {key} not found.")
                return req, None
            return req, goods
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None, None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None, None

    async def get_permit_goods_dda_dict(self, pid_permit, external=False):
        __name__ = who_am_i()
        try:
            if external:
                goods_entries = await self.dds[DDS_PERMITS].get_all_entries(
                    view_name=VIEW_GOODS_EXTERNAL_PID, key=pid_permit, start=0, page_size=100, page=0)
            else:
                goods_entries = await self.dds[DDS_PERMITS].get_all_entries(
                    view_name=VIEW_GOODS_PID, key=pid_permit, start=0, page_size=100, page=0)
            if (goods_entries is None) or (goods_entries['count'] == 0):
                return None
            goods = []
            entries = goods_entries['entries']
            for entry in entries:
                if isinstance(entry, dict) and ('@unid' in entry):
                    unid = entry['@unid']
                    g = await self.dds[DDS_PERMITS].get_document(unid=unid)
                    goods.append(g)
            return goods
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return []
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None


    async def get_permit_dda_dict(self, idno):
        __name__ = who_am_i()
        if idno in [None, '']:
            self.log.error(f"{self.name}.{__name__} idno missing.")
            return None, None
        identifier = deepcopy(idno)
        try:
            if is_valid_unid(identifier):
                permit = await self.dds[DDS_PERMITS].get_document(unid=identifier)
                if permit is None:
                    self.log.warning(f"{self.name}.{__name__} Permit '{identifier}' not found.")
                    return None, None
            elif len(idno) > 10:
                # pid
                permit = await self.dds[DDS_PERMITS].get_document_by_key(view_name=VIEW_PERMITS_PID, key=idno)
                if permit is None:
                    self.log.warning(f"{self.name}.{__name__} Permit '{identifier}' not found.")
                    return None, None
            else:
                # idno
                permit = await self.dds[DDS_PERMITS].get_document_by_key(view_name=VIEW_PERMITS, key=idno)
                if permit is None:
                    self.log.warning(f"{self.name}.{__name__} Permit '{identifier}' not found.")
                    return None, None
            pid = permit['PID']
            goods = await self.get_permit_goods_dda_dict(pid_permit=pid)
            if goods is None:
                self.log.warning(f"{self.name}.{__name__} Goods for Permit '{identifier}' not found.")
                return permit, None
            return permit, goods
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None, None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None, None


    async def get_permit_external_dda_dict(self, idno):
        __name__ = who_am_i()
        if idno in [None, '']:
            self.log.error(f"{self.name}.{__name__} idno missing.")
            return None, None
        identifier = deepcopy(idno)
        try:
            if is_valid_unid(idno):
                permit = await self.dds[DDS_PERMITS].get_document(unid=idno)
                if permit is None:
                    self.log.warning(f"{self.name}.{__name__} Permit External '{identifier}' not found.")
                    return None, None
            elif is_valid_pid(idno):
                # pid
                permit = await self.dds[DDS_PERMITS].get_document_by_key(view_name=VIEW_PERMITS_EXTERNAL_PID, key=idno)
                if permit is None:
                    self.log.warning(f"{self.name}.{__name__} Permit External '{identifier}' not found.")
                    return None, None
            else:
                # idno
                permit = await self.dds[DDS_PERMITS].get_document_by_key(view_name=VIEW_PERMITS_EXTERNAL, key=idno)
                if permit is None:
                    self.log.warning(f"{self.name}.{__name__} Permit External '{identifier}' not found.")
                    return None, None
            pid = permit['PID']
            goods = await self.get_permit_goods_dda_dict(pid_permit=pid, external=True)
            if goods is None:
                self.log.warning(f"{self.name}.{__name__} Goods for Permit External'{identifier}' not found.")
                return permit, None
            return permit, goods
        except DdsError as e:
            self.log.error(f"{self.name}.{__name__} DDS ERROR: {e.status} -{e.message} ")
            return None, None
        except Exception as e:
            self.log.error(f"{self.name}.{__name__} ERROR: {type(e)} - {str(e)} ")
            return None, None


class DdsError(BaseException):
    def __init__(self, status=500, message=f"CITES DDS Exception", module=None):
        self.status = status
        self.message = message
        self.module = module
        super().__init__(self.message)
