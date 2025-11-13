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
Package "group"
"""
from delphixpy.v1_11_30 import response_validator

def create(engine, group=None):
    """
    Create a new Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param group: Payload object.
    :type group: :py:class:`v1_11_30.web.vo.Group`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/group"
    response = engine.post(url, group.to_dict(dirty=True) if group else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_30.web.objects.Group.Group` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_30.web.vo.Group`
    """
    url = "/resources/json/delphix/group/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Group'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List Group objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_30.web.vo.Group`
    """
    url = "/resources/json/delphix/group"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Group'], returns_list=True, raw_result=raw_result)

def update(engine, ref, group=None):
    """
    Update the specified Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_30.web.objects.Group.Group` object
    :type ref: ``str``
    :param group: Payload object.
    :type group: :py:class:`v1_11_30.web.vo.Group`
    """
    url = "/resources/json/delphix/group/%s" % ref
    response = engine.post(url, group.to_dict(dirty=True) if group else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified Group object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_30.web.objects.Group.Group` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/group/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def lock(engine, ref):
    """
    Protects all sources in the group from deletion and other data-losing
    actions. Cannot be undone.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_30.web.objects.Group.Group` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/group/%s/lock" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

