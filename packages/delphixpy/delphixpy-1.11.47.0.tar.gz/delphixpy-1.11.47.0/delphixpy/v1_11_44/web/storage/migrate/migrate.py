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
Package "storage.migrate"
"""
from delphixpy.v1_11_44 import response_validator

def get(engine):
    """
    Retrieve the specified ObjectStoreMigrationStatus object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_44.web.vo.ObjectStoreMigrationStatus`
    """
    url = "/resources/json/delphix/storage/migrate"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['ObjectStoreMigrationStatus'], returns_list=False, raw_result=raw_result)

def start(engine, object_store=None):
    """
    Migrate block-based pool to object store.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param object_store: Payload object.
    :type object_store: :py:class:`v1_11_44.web.vo.ObjectStore`
    """
    url = "/resources/json/delphix/storage/migrate/start"
    response = engine.post(url, object_store.to_dict(dirty=True) if object_store else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

