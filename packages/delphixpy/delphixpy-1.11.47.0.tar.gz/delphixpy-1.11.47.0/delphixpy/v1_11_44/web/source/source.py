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
Package "source"
"""
from delphixpy.v1_11_44.web.source import operationTemplate
from urllib.parse import urlencode
from delphixpy.v1_11_44 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Source object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_44.web.vo.Source`
    """
    url = "/resources/json/delphix/source/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Source'], returns_list=False, raw_result=raw_result)

def get_all(engine, database=None, config=None, all_sources=None, repository=None, environment=None, include_hosts=None):
    """
    Lists sources on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param database: List visible sources associated with the given container
        reference. Visible sources are of type LINKED or VIRTUAL.
    :type database: ``str``
    :param config: List visible sources associated with the given sourceconfig
        reference. Visible sources are of type LINKED or VIRTUAL.
    :type config: ``str``
    :param all_sources: List all sources associated with the given source
        container reference.
    :type all_sources: ``bool``
    :param repository: List sources associated with the given source repository
        reference.
    :type repository: ``str``
    :param environment: List sources associated with the given source
        environment reference.
    :type environment: ``str``
    :param include_hosts: Whether to include the list of hosts for each source
        in the response.
    :type include_hosts: ``bool``
    :rtype: ``list`` of :py:class:`v1_11_44.web.vo.Source`
    """
    url = "/resources/json/delphix/source"
    query_params = {"database": database, "config": config, "allSources": all_sources, "repository": repository, "environment": environment, "includeHosts": include_hosts}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Source'], returns_list=True, raw_result=raw_result)

def update(engine, ref, source=None):
    """
    Update the specified Source object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :param source: Payload object.
    :type source: :py:class:`v1_11_44.web.vo.Source`
    """
    url = "/resources/json/delphix/source/%s" % ref
    response = engine.post(url, source.to_dict(dirty=True) if source else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable(engine, ref, source_enable_parameters=None):
    """
    Enables the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_enable_parameters: Payload object.
    :type source_enable_parameters:
        :py:class:`v1_11_44.web.vo.SourceEnableParameters`
    """
    url = "/resources/json/delphix/source/%s/enable" % ref
    response = engine.post(url, source_enable_parameters.to_dict(dirty=True) if source_enable_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def disable(engine, ref, source_disable_parameters=None):
    """
    Disables the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_disable_parameters: Payload object.
    :type source_disable_parameters:
        :py:class:`v1_11_44.web.vo.SourceDisableParameters`
    """
    url = "/resources/json/delphix/source/%s/disable" % ref
    response = engine.post(url, source_disable_parameters.to_dict(dirty=True) if source_disable_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def start(engine, ref, source_start_parameters=None):
    """
    Starts the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_start_parameters: Payload object.
    :type source_start_parameters:
        :py:class:`v1_11_44.web.vo.SourceStartParameters`
    """
    url = "/resources/json/delphix/source/%s/start" % ref
    response = engine.post(url, source_start_parameters.to_dict(dirty=True) if source_start_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def stop(engine, ref, source_stop_parameters=None):
    """
    Stops the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_stop_parameters: Payload object.
    :type source_stop_parameters:
        :py:class:`v1_11_44.web.vo.SourceStopParameters`
    """
    url = "/resources/json/delphix/source/%s/stop" % ref
    response = engine.post(url, source_stop_parameters.to_dict(dirty=True) if source_stop_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def upgrade(engine, ref, source_upgrade_parameters=None):
    """
    Upgrades the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_upgrade_parameters: Payload object.
    :type source_upgrade_parameters:
        :py:class:`v1_11_44.web.vo.SourceUpgradeParameters`
    """
    url = "/resources/json/delphix/source/%s/upgrade" % ref
    response = engine.post(url, source_upgrade_parameters.to_dict(dirty=True) if source_upgrade_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def lock(engine, ref):
    """
    Protects source from deletion and other data-losing actions. Cannot be
    undone.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_44.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_44.web.objects.Source.Source` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/source/%s/lock" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

