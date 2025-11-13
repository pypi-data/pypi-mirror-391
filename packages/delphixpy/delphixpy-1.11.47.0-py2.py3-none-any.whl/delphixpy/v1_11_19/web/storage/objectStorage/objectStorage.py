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
Package "storage.objectStorage"
"""
from urllib.parse import urlencode
from delphixpy.v1_11_19 import response_validator

def get(engine):
    """
    Retrieve the specified ObjectStore object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_19.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_19.web.vo.ObjectStore`
    """
    url = "/resources/json/delphix/storage/objectStorage"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['ObjectStore'], returns_list=False, raw_result=raw_result)

def set(engine, object_store=None):
    """
    Update the specified ObjectStore object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_19.delphix_engine.DelphixEngine`
    :param object_store: Payload object.
    :type object_store: :py:class:`v1_11_19.web.vo.ObjectStore`
    """
    url = "/resources/json/delphix/storage/objectStorage"
    response = engine.post(url, object_store.to_dict(dirty=True) if object_store else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def test_connection(engine, object_store_test):
    """
    Test connectivity to an object store.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_19.delphix_engine.DelphixEngine`
    :param object_store_test: Payload object.
    :type object_store_test: :py:class:`v1_11_19.web.vo.ObjectStoreTest`
    """
    url = "/resources/json/delphix/storage/objectStorage/testConnection"
    response = engine.post(url, object_store_test.to_dict(dirty=True) if object_store_test else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def cache_hits_report(engine, json=None):
    """
    Get a ZettaCache hits-by-size report.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_19.delphix_engine.DelphixEngine`
    :param json: True if the result should return a JSON formatted result.
    :type json: ``bool``
    """
    url = "/resources/json/delphix/storage/objectStorage/cacheHitsReport"
    query_params = {"json": json}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def clear_cache_hits(engine):
    """
    Clear the accumulated ZettaCache hits-by-size data.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_19.delphix_engine.DelphixEngine`
    """
    url = "/resources/json/delphix/storage/objectStorage/clearCacheHits"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

