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
Package "database"
"""
from delphixpy.v1_11_27.web.database import performanceHistory
from urllib.parse import urlencode
from delphixpy.v1_11_27 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Container object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_27.web.vo.Container`
    """
    url = "/resources/json/delphix/database/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Container'], returns_list=False, raw_result=raw_result)

def get_all(engine, provision_container=None, group=None, no_js_data_source=None, no_js_container_data_source=None, valid_for_secure_replication=None, cdb_container=None):
    """
    Returns a list of databases on the system or within a group.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param provision_container: Restrict databases to those provisioned from
        the specified container. This option is mutually exclusive with the
        "group" option.
    :type provision_container: ``str``
    :param group: Restrict databases to those within the specified group. This
        option is mutually exclusive with the "provisionContainer" option.
    :type group: ``str``
    :param no_js_data_source: Restrict databases to those which are not part of
        a Self-Service data layout (data template or data container). This
        option is mutually exclusive with the "noJSContainerDataSource" option.
    :type no_js_data_source: ``bool``
    :param no_js_container_data_source: Restrict databases to those which are
        not part of a Self-Service data container. This option is mutually
        exclusive with the "noJSDataSource" option.
    :type no_js_container_data_source: ``bool``
    :param valid_for_secure_replication: Restrict listing to include only
        datasets that can be securely replicated.
    :type valid_for_secure_replication: ``bool``
    :param cdb_container: Restrict listing to only include the PDB datasets
        belonging to the specified CDB dataset reference. This option is
        mutually exclusive with all the other options.
    :type cdb_container: ``str``
    :rtype: ``list`` of :py:class:`v1_11_27.web.vo.Container`
    """
    url = "/resources/json/delphix/database"
    query_params = {"provisionContainer": provision_container, "group": group, "noJSDataSource": no_js_data_source, "noJSContainerDataSource": no_js_container_data_source, "validForSecureReplication": valid_for_secure_replication, "cdbContainer": cdb_container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Container'], returns_list=True, raw_result=raw_result)

def update(engine, ref, container=None):
    """
    Update the specified Container object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param container: Payload object.
    :type container: :py:class:`v1_11_27.web.vo.Container`
    """
    url = "/resources/json/delphix/database/%s" % ref
    response = engine.post(url, container.to_dict(dirty=True) if container else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref, delete_parameters=None):
    """
    Delete the specified Container object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param delete_parameters: Payload object.
    :type delete_parameters: :py:class:`v1_11_27.web.vo.DeleteParameters`
    """
    url = "/resources/json/delphix/database/%s/delete" % ref
    response = engine.post(url, delete_parameters.to_dict(dirty=True) if delete_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def refresh(engine, ref, refresh_parameters):
    """
    Refreshes a container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param refresh_parameters: Payload object.
    :type refresh_parameters: :py:class:`v1_11_27.web.vo.RefreshParameters`
    """
    url = "/resources/json/delphix/database/%s/refresh" % ref
    response = engine.post(url, refresh_parameters.to_dict(dirty=True) if refresh_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def rollback(engine, ref, rollback_parameters):
    """
    Rolls back a container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param rollback_parameters: Payload object.
    :type rollback_parameters: :py:class:`v1_11_27.web.vo.RollbackParameters`
    """
    url = "/resources/json/delphix/database/%s/rollback" % ref
    response = engine.post(url, rollback_parameters.to_dict(dirty=True) if rollback_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def deprovision(engine, ref, reprovision_parameters):
    """
    Deprovisions a container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param reprovision_parameters: Payload object.
    :type reprovision_parameters:
        :py:class:`v1_11_27.web.vo.ReprovisionParameters`
    :rtype: ``dict``
    """
    url = "/resources/json/delphix/database/%s/deprovision" % ref
    response = engine.post(url, reprovision_parameters.to_dict(dirty=True) if reprovision_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['dict'], returns_list=False, raw_result=raw_result)

def reprovision(engine, ref, reprovision_parameters):
    """
    Reprovisions a container. This should only be called after a deprovision
    using the ReprovisionParameters returned from that operation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param reprovision_parameters: Payload object.
    :type reprovision_parameters:
        :py:class:`v1_11_27.web.vo.ReprovisionParameters`
    """
    url = "/resources/json/delphix/database/%s/reprovision" % ref
    response = engine.post(url, reprovision_parameters.to_dict(dirty=True) if reprovision_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def undo(engine, ref):
    """
    Reverts the effects of the latest refresh or rollback operation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/database/%s/undo" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def switch_timeflow(engine, ref, switch_timeflow_parameters):
    """
    Switch to the latest point on the specified TimeFlow.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param switch_timeflow_parameters: Payload object.
    :type switch_timeflow_parameters:
        :py:class:`v1_11_27.web.vo.SwitchTimeflowParameters`
    """
    url = "/resources/json/delphix/database/%s/switchTimeflow" % ref
    response = engine.post(url, switch_timeflow_parameters.to_dict(dirty=True) if switch_timeflow_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def sync(engine, ref, sync_parameters=None):
    """
    Performs SnapSync on a database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param sync_parameters: Payload object.
    :type sync_parameters: :py:class:`v1_11_27.web.vo.SyncParameters`
    """
    url = "/resources/json/delphix/database/%s/sync" % ref
    response = engine.post(url, sync_parameters.to_dict(dirty=True) if sync_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def detach_source(engine, ref, detach_source_parameters):
    """
    Detaches a linked source from a database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param detach_source_parameters: Payload object.
    :type detach_source_parameters:
        :py:class:`v1_11_27.web.vo.DetachSourceParameters`
    """
    url = "/resources/json/delphix/database/%s/detachSource" % ref
    response = engine.post(url, detach_source_parameters.to_dict(dirty=True) if detach_source_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def attach_source(engine, ref, attach_source_parameters):
    """
    Attaches a database source to a previously detached container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param attach_source_parameters: Payload object.
    :type attach_source_parameters:
        :py:class:`v1_11_27.web.vo.AttachSourceParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/database/%s/attachSource" % ref
    response = engine.post(url, attach_source_parameters.to_dict(dirty=True) if attach_source_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def connection_info(engine, ref):
    """
    Returns the connection information for the source associated with this
    container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_27.web.vo.SourceConnectionInfo`
    """
    url = "/resources/json/delphix/database/%s/connectionInfo" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SourceConnectionInfo'], returns_list=False, raw_result=raw_result)

def purge_logs(engine, ref, purge_logs_parameters):
    """
    Delete logs to reclaim storage space.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param purge_logs_parameters: Payload object.
    :type purge_logs_parameters:
        :py:class:`v1_11_27.web.vo.PurgeLogsParameters`
    :rtype: :py:class:`v1_11_27.web.vo.PurgeLogsResult`
    """
    url = "/resources/json/delphix/database/%s/purgeLogs" % ref
    response = engine.post(url, purge_logs_parameters.to_dict(dirty=True) if purge_logs_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['PurgeLogsResult'], returns_list=False, raw_result=raw_result)

def add_live_source(engine, ref, add_live_source_parameters):
    """
    Add a LiveSource for this dSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param add_live_source_parameters: Payload object.
    :type add_live_source_parameters:
        :py:class:`v1_11_27.web.vo.AddLiveSourceParameters`
    """
    url = "/resources/json/delphix/database/%s/addLiveSource" % ref
    response = engine.post(url, add_live_source_parameters.to_dict(dirty=True) if add_live_source_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def add_live_source_defaults(engine, ref):
    """
    Returns a partially constructed add LiveSource parameters object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_27.web.vo.AddLiveSourceParameters`
    """
    url = "/resources/json/delphix/database/%s/addLiveSource/defaults" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['AddLiveSourceParameters'], returns_list=False, raw_result=raw_result)

def remove_live_source(engine, ref):
    """
    Remove the LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/database/%s/removeLiveSource" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def start_live_source_resync(engine, ref):
    """
    Resync the LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/database/%s/startLiveSourceResync" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def discard_live_source_resync(engine, ref):
    """
    Discard the data from previous resync for LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/database/%s/discardLiveSourceResync" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def apply_live_source_resync(engine, ref):
    """
    Apply the resync to the LiveSource.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/database/%s/applyLiveSourceResync" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def create_transformation(engine, ref, create_transformation_parameters):
    """
    Defines a new transformation against this container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :param create_transformation_parameters: Payload object.
    :type create_transformation_parameters:
        :py:class:`v1_11_27.web.vo.CreateTransformationParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/database/%s/createTransformation" % ref
    response = engine.post(url, create_transformation_parameters.to_dict(dirty=True) if create_transformation_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def timeflow_snapshot_day_range(engine, ref):
    """
    Returns the count of TimeFlow snapshots of the container aggregated by day.
    The time zone used to perform the computation is the time zone of the last
    snapshot of this container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_27.web.objects.Container.Container` object
    :type ref: ``str``
    :rtype: ``list`` of :py:class:`v1_11_27.web.vo.TimeflowSnapshotDayRange`
    """
    url = "/resources/json/delphix/database/%s/timeflowSnapshotDayRange" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TimeflowSnapshotDayRange'], returns_list=True, raw_result=raw_result)

def provision(engine, provision_parameters):
    """
    Provisions the container specified by the provision parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param provision_parameters: Payload object.
    :type provision_parameters: :py:class:`v1_11_27.web.vo.ProvisionParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/database/provision"
    response = engine.post(url, provision_parameters.to_dict(dirty=True) if provision_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def provision_defaults(engine, timeflow_point_parameters):
    """
    Returns a partially constructed provision parameters object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param timeflow_point_parameters: Payload object.
    :type timeflow_point_parameters:
        :py:class:`v1_11_27.web.vo.TimeflowPointParameters`
    :rtype: :py:class:`v1_11_27.web.vo.ProvisionParameters`
    """
    url = "/resources/json/delphix/database/provision/defaults"
    response = engine.post(url, timeflow_point_parameters.to_dict(dirty=True) if timeflow_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['ProvisionParameters'], returns_list=False, raw_result=raw_result)

def create_empty(engine, empty_dataset_creation_parameters):
    """
    Creates a new empty virtual dataset.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param empty_dataset_creation_parameters: Payload object.
    :type empty_dataset_creation_parameters:
        :py:class:`v1_11_27.web.vo.EmptyDatasetCreationParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/database/createEmpty"
    response = engine.post(url, empty_dataset_creation_parameters.to_dict(dirty=True) if empty_dataset_creation_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def link(engine, link_parameters):
    """
    Links the database specified by link parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param link_parameters: Payload object.
    :type link_parameters: :py:class:`v1_11_27.web.vo.LinkParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/database/link"
    response = engine.post(url, link_parameters.to_dict(dirty=True) if link_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def link_defaults(engine, config=None):
    """
    Returns a partially constructed linking parameters object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param config: The config being linked.
    :type config: ``str``
    :rtype: :py:class:`v1_11_27.web.vo.LinkParameters`
    """
    url = "/resources/json/delphix/database/link/defaults"
    query_params = {"config": config}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['LinkParameters'], returns_list=False, raw_result=raw_result)

def export(engine, export_parameters):
    """
    Provision a physical database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param export_parameters: Payload object.
    :type export_parameters: :py:class:`v1_11_27.web.vo.ExportParameters`
    """
    url = "/resources/json/delphix/database/export"
    response = engine.post(url, export_parameters.to_dict(dirty=True) if export_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def file_mapping(engine, file_mapping_parameters):
    """
    Generate file mappings for a particular TimeFlow point and a set of rules.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param file_mapping_parameters: Payload object.
    :type file_mapping_parameters:
        :py:class:`v1_11_27.web.vo.FileMappingParameters`
    :rtype: :py:class:`v1_11_27.web.vo.FileMappingResult`
    """
    url = "/resources/json/delphix/database/fileMapping"
    response = engine.post(url, file_mapping_parameters.to_dict(dirty=True) if file_mapping_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['FileMappingResult'], returns_list=False, raw_result=raw_result)

def oracle_supported_character_sets(engine):
    """
    Retrieves all possible character sets for an Oracle database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_27.web.vo.OracleCharacterSet`
    """
    url = "/resources/json/delphix/database/oracleSupportedCharacterSets"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['OracleCharacterSet'], returns_list=True, raw_result=raw_result)

def batch_delete(engine, batch_container_delete_parameters):
    """
    Delete a collection of containers.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param batch_container_delete_parameters: Payload object.
    :type batch_container_delete_parameters:
        :py:class:`v1_11_27.web.vo.BatchContainerDeleteParameters`
    """
    url = "/resources/json/delphix/database/batchDelete"
    response = engine.post(url, batch_container_delete_parameters.to_dict(dirty=True) if batch_container_delete_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def batch_refresh(engine, batch_container_refresh_parameters):
    """
    Refresh a collection of containers.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param batch_container_refresh_parameters: Payload object.
    :type batch_container_refresh_parameters:
        :py:class:`v1_11_27.web.vo.BatchContainerRefreshParameters`
    """
    url = "/resources/json/delphix/database/batchRefresh"
    response = engine.post(url, batch_container_refresh_parameters.to_dict(dirty=True) if batch_container_refresh_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

