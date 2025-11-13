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
Package "service.insight.splunkHec"
"""
from delphixpy.v1_11_33 import response_validator

def create(engine, splunk_hec_config=None):
    """
    Create a new SplunkHecConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_33.delphix_engine.DelphixEngine`
    :param splunk_hec_config: Payload object.
    :type splunk_hec_config: :py:class:`v1_11_33.web.vo.SplunkHecConfig`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/insight/splunkHec"
    response = engine.post(url, splunk_hec_config.to_dict(dirty=True) if splunk_hec_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SplunkHecConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_33.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_33.web.objects.SplunkHecConfig.SplunkHecConf
        ig` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_33.web.vo.SplunkHecConfig`
    """
    url = "/resources/json/delphix/service/insight/splunkHec/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SplunkHecConfig'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List SplunkHecConfig objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_33.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_33.web.vo.SplunkHecConfig`
    """
    url = "/resources/json/delphix/service/insight/splunkHec"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SplunkHecConfig'], returns_list=True, raw_result=raw_result)

def update(engine, ref, splunk_hec_config=None):
    """
    Update the specified SplunkHecConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_33.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_33.web.objects.SplunkHecConfig.SplunkHecConf
        ig` object
    :type ref: ``str``
    :param splunk_hec_config: Payload object.
    :type splunk_hec_config: :py:class:`v1_11_33.web.vo.SplunkHecConfig`
    """
    url = "/resources/json/delphix/service/insight/splunkHec/%s" % ref
    response = engine.post(url, splunk_hec_config.to_dict(dirty=True) if splunk_hec_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SplunkHecConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_33.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_11_33.web.objects.SplunkHecConfig.SplunkHecConf
        ig` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/service/insight/splunkHec/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def test(engine, splunk_hec_config=None):
    """
    Tests the given Splunk configuration by sending a test event to the
    specified index or indexes.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_33.delphix_engine.DelphixEngine`
    :param splunk_hec_config: Payload object.
    :type splunk_hec_config: :py:class:`v1_11_33.web.vo.SplunkHecConfig`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/insight/splunkHec/test"
    response = engine.post(url, splunk_hec_config.to_dict(dirty=True) if splunk_hec_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

