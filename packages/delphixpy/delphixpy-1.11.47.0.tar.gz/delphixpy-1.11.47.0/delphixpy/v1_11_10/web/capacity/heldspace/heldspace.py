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
Package "capacity.heldspace"
"""
from urllib.parse import urlencode
from delphixpy.v1_11_10 import response_validator

def get_all(engine):
    """
    Lists HeldSpace in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_10.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_10.web.vo.HeldSpaceCapacityData`
    """
    url = "/resources/json/delphix/capacity/heldspace"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['HeldSpaceCapacityData'], returns_list=True, raw_result=raw_result)

def deletion_dependencies(engine, storage_container=None):
    """
    Returns instructions on how to free up this HeldSpace.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_10.delphix_engine.DelphixEngine`
    :param storage_container: The unique ID of the retained space to get
        deletion instructions for.
    :type storage_container: ``str``
    :rtype: :py:class:`v1_11_10.web.vo.DeletionDependency`
    """
    url = "/resources/json/delphix/capacity/heldspace/deletionDependencies"
    query_params = {"storageContainer": storage_container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['DeletionDependency'], returns_list=False, raw_result=raw_result)

