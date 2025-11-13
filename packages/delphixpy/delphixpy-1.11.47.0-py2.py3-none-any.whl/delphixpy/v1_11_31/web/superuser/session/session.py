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
Package "superuser.session"
"""
from urllib.parse import urlencode
from delphixpy.v1_11_31 import response_validator

def get(engine, ref):
    """
    Retrieve the specified SuperuserSession object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_31.web.objects.Superu
        serSession.SuperuserSession` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_31.web.vo.SuperuserSession`
    """
    url = "/resources/json/delphix/superuser/session/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SuperuserSession'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List SuperuserSession objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_31.web.vo.SuperuserSession`
    """
    url = "/resources/json/delphix/superuser/session"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SuperuserSession'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SuperuserSession object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_31.web.objects.Superu
        serSession.SuperuserSession` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/superuser/session/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def download(engine, session_log_name=None):
    """
    Download a session log.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_31.delphix_engine.DelphixEngine`
    :param session_log_name: Name of the session log file to be downloaded.
    :type session_log_name: ``str``
    """
    url = "/resources/json/delphix/superuser/session/download"
    query_params = {"sessionLogName": session_log_name}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

