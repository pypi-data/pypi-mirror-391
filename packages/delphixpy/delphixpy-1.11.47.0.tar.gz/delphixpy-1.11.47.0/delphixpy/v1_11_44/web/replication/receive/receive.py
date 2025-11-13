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
Package "replication.receive"
"""
from delphixpy.v1_11_44 import response_validator

def create(engine, offline_replication_receive_spec=None):
    """
    Create a new OfflineReplicationReceiveSpec object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param offline_replication_receive_spec: Payload object.
    :type offline_replication_receive_spec:
        :py:class:`v1_11_44.web.vo.OfflineReplicationReceiveSpec`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/replication/receive"
    response = engine.post(url, offline_replication_receive_spec.to_dict(dirty=True) if offline_replication_receive_spec else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified OfflineReplicationReceiveSpec object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_44.web.objects.Offlin
        eReplicationReceiveSpec.OfflineReplicationReceiveSpec` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_44.web.vo.OfflineReplicationReceiveSpec`
    """
    url = "/resources/json/delphix/replication/receive/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['OfflineReplicationReceiveSpec'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List OfflineReplicationReceiveSpec objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :rtype: ``list`` of
        :py:class:`v1_11_44.web.vo.OfflineReplicationReceiveSpec`
    """
    url = "/resources/json/delphix/replication/receive"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['OfflineReplicationReceiveSpec'], returns_list=True, raw_result=raw_result)

def update(engine, ref, offline_replication_receive_spec=None):
    """
    Update the specified OfflineReplicationReceiveSpec object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_44.web.objects.Offlin
        eReplicationReceiveSpec.OfflineReplicationReceiveSpec` object
    :type ref: ``str``
    :param offline_replication_receive_spec: Payload object.
    :type offline_replication_receive_spec:
        :py:class:`v1_11_44.web.vo.OfflineReplicationReceiveSpec`
    """
    url = "/resources/json/delphix/replication/receive/%s" % ref
    response = engine.post(url, offline_replication_receive_spec.to_dict(dirty=True) if offline_replication_receive_spec else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified OfflineReplicationReceiveSpec object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_44.web.objects.Offlin
        eReplicationReceiveSpec.OfflineReplicationReceiveSpec` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/replication/receive/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def execute(engine, ref):
    """
    Manually trigger execution of a replication receive spec.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_44.web.objects.Offlin
        eReplicationReceiveSpec.OfflineReplicationReceiveSpec` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/replication/receive/%s/execute" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

