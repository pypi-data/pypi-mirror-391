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
Package "notification"
"""
from urllib.parse import urlencode
from delphixpy.v1_11_27 import response_validator

def get_all(engine, channel=None, timeout=None, max=None):
    """
    Returns a list of pending notifications for the current session.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_27.delphix_engine.DelphixEngine`
    :param channel: Client-specific ID to specify an independent channel.
    :type channel: ``str``
    :param timeout: Timeout, in milliseconds, to wait for one or more
        responses.
    :type timeout: ``str``
    :param max: Maximum number of entries to return at once.
    :type max: ``str``
    :rtype: ``list`` of :py:class:`v1_11_27.web.vo.Notification`
    """
    url = "/resources/json/delphix/notification"
    query_params = {"channel": channel, "timeout": timeout, "max": max}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['Notification'], returns_list=True, raw_result=raw_result)

