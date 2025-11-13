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
Package "delphix"
"""
from delphixpy.v1_11_43 import response_validator

def logout(engine):
    """
    Logs the current authenticated user out.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    """
    url = "/resources/json/delphix/logout"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def login(engine, login_request):
    """
    Establishes an authenticated user session.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_43.delphix_engine.DelphixEngine`
    :param login_request: Payload object.
    :type login_request: :py:class:`v1_11_43.web.vo.LoginRequest`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/login"
    response = engine.post(url, login_request.to_dict(dirty=True) if login_request else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

