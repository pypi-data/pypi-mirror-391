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
Package "service.snmp.v3.usm"
"""
from delphixpy.v1_11_31 import response_validator

def create(engine, snmpv3_usm_user_config=None):
    """
    Create a new SNMPV3USMUserConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param snmpv3_usm_user_config: Payload object.
    :type snmpv3_usm_user_config:
        :py:class:`v1_11_31.web.vo.SNMPV3USMUserConfig`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/snmp/v3/usm"
    response = engine.post(url, snmpv3_usm_user_config.to_dict(dirty=True) if snmpv3_usm_user_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SNMPV3USMUserConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_31.web.objects.SNMPV3
        USMUserConfig.SNMPV3USMUserConfig` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_31.web.vo.SNMPV3USMUserConfig`
    """
    url = "/resources/json/delphix/service/snmp/v3/usm/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SNMPV3USMUserConfig'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists SNMP User Security Model users.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_31.web.vo.SNMPV3USMUserConfig`
    """
    url = "/resources/json/delphix/service/snmp/v3/usm"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SNMPV3USMUserConfig'], returns_list=True, raw_result=raw_result)

def update(engine, ref, snmpv3_usm_user_config=None):
    """
    Update the specified SNMPV3USMUserConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_31.web.objects.SNMPV3
        USMUserConfig.SNMPV3USMUserConfig` object
    :type ref: ``str``
    :param snmpv3_usm_user_config: Payload object.
    :type snmpv3_usm_user_config:
        :py:class:`v1_11_31.web.vo.SNMPV3USMUserConfig`
    """
    url = "/resources/json/delphix/service/snmp/v3/usm/%s" % ref
    response = engine.post(url, snmpv3_usm_user_config.to_dict(dirty=True) if snmpv3_usm_user_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SNMPV3USMUserConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_31.web.objects.SNMPV3
        USMUserConfig.SNMPV3USMUserConfig` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/service/snmp/v3/usm/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

