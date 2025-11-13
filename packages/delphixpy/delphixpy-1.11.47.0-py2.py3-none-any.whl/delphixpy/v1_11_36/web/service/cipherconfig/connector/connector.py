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
Package "service.cipherconfig.connector"
"""
from delphixpy.v1_11_36 import response_validator

def create(engine, connector_ciphers=None):
    """
    Create a new ConnectorCiphers object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_36.delphix_engine.DelphixEngine`
    :param connector_ciphers: Payload object.
    :type connector_ciphers: :py:class:`v1_11_36.web.vo.ConnectorCiphers`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/cipherconfig/connector"
    response = engine.post(url, connector_ciphers.to_dict(dirty=True) if connector_ciphers else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists connector cipher change request in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_36.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_36.web.vo.ConnectorCiphers`
    """
    url = "/resources/json/delphix/service/cipherconfig/connector"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['ConnectorCiphers'], returns_list=True, raw_result=raw_result)

