#
# Copyright 2025 by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Package "host.oracle.okvclient"
"""
from urllib.parse import urlencode
from delphixpy.v1_11_45 import response_validator

def create(engine, oracle_okv_client=None):
    """
    Create a new OracleOKVClient object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_45.delphix_engine.DelphixEngine`
    :param oracle_okv_client: Payload object.
    :type oracle_okv_client: :py:class:`v1_11_45.web.vo.OracleOKVClient`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/host/oracle/okvclient"
    response = engine.post(url, oracle_okv_client.to_dict(dirty=True) if oracle_okv_client else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified OracleOKVClient object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_45.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_45.web.objects.OracleOKVClient.OracleOKVClie
        nt` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_45.web.vo.OracleOKVClient`
    """
    url = "/resources/json/delphix/host/oracle/okvclient/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['OracleOKVClient'], returns_list=False, raw_result=raw_result)

def get_all(engine, host=None):
    """
    Returns the list of OKV clients within the host or the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_45.delphix_engine.DelphixEngine`
    :param host: A reference to the associated host.
    :type host: ``str``
    :rtype: ``list`` of :py:class:`v1_11_45.web.vo.OracleOKVClient`
    """
    url = "/resources/json/delphix/host/oracle/okvclient"
    query_params = {"host": host}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['OracleOKVClient'], returns_list=True, raw_result=raw_result)

def update(engine, ref, oracle_okv_client=None):
    """
    Update the specified OracleOKVClient object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_45.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_45.web.objects.OracleOKVClient.OracleOKVClie
        nt` object
    :type ref: ``str``
    :param oracle_okv_client: Payload object.
    :type oracle_okv_client: :py:class:`v1_11_45.web.vo.OracleOKVClient`
    """
    url = "/resources/json/delphix/host/oracle/okvclient/%s" % ref
    response = engine.post(url, oracle_okv_client.to_dict(dirty=True) if oracle_okv_client else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified OracleOKVClient object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_45.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_45.web.objects.OracleOKVClient.OracleOKVClie
        nt` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/host/oracle/okvclient/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

