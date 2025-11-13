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
Package "storage.trim"
"""
from delphixpy import response_validator

def get(engine):
    """
    Retrieve the specified TrimStatus object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.delphix_engine.DelphixEngine`
    :rtype: :py:class:`delphixpy.web.vo.TrimStatus`
    """
    url = "/resources/json/delphix/storage/trim"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TrimStatus'], returns_list=False, raw_result=raw_result)

def start(engine):
    """
    Initiate a manual TRIM operation on all compatible storage devices.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.delphix_engine.DelphixEngine`
    """
    url = "/resources/json/delphix/storage/trim/start"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable_autotrim(engine):
    """
    Turn on autotrim for the main storage pool.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.delphix_engine.DelphixEngine`
    """
    url = "/resources/json/delphix/storage/trim/enableAutotrim"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def disable_autotrim(engine):
    """
    Turn off autotrim for the main storage pool.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.delphix_engine.DelphixEngine`
    """
    url = "/resources/json/delphix/storage/trim/disableAutotrim"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

