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
Package "service.snmp.v3.manager"
"""
from delphixpy.v1_11_43 import response_validator

def create(engine, snmpv3_manager=None):
    """
    Create a new SNMPV3Manager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :param snmpv3_manager: Payload object.
    :type snmpv3_manager: :py:class:`v1_11_43.web.vo.SNMPV3Manager`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/snmp/v3/manager"
    response = engine.post(url, snmpv3_manager.to_dict(dirty=True) if snmpv3_manager else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SNMPV3Manager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_43.web.objects.SNMPV3Manager.SNMPV3Manager`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_43.web.vo.SNMPV3Manager`
    """
    url = "/resources/json/delphix/service/snmp/v3/manager/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SNMPV3Manager'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists SNMP managers in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_43.web.vo.SNMPV3Manager`
    """
    url = "/resources/json/delphix/service/snmp/v3/manager"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SNMPV3Manager'], returns_list=True, raw_result=raw_result)

def update(engine, ref, snmpv3_manager=None):
    """
    Update the specified SNMPV3Manager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_43.web.objects.SNMPV3Manager.SNMPV3Manager`
        object
    :type ref: ``str``
    :param snmpv3_manager: Payload object.
    :type snmpv3_manager: :py:class:`v1_11_43.web.vo.SNMPV3Manager`
    """
    url = "/resources/json/delphix/service/snmp/v3/manager/%s" % ref
    response = engine.post(url, snmpv3_manager.to_dict(dirty=True) if snmpv3_manager else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SNMPV3Manager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_43.web.objects.SNMPV3Manager.SNMPV3Manager`
        object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/service/snmp/v3/manager/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def test(engine, ref):
    """
    Tests the ability to send an SNMP INFORM message to the manager (only
    applies when useInform is true).

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_43.web.objects.SNMPV3Manager.SNMPV3Manager`
        object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/service/snmp/v3/manager/%s/test" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

