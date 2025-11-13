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
Package "network.test.throughput"
"""
from delphixpy.v1_11_2 import response_validator

def create(engine, network_throughput_test_parameters):
    """
    Create a new NetworkThroughputTest object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_2.delphix_engine.DelphixEngine`
    :param network_throughput_test_parameters: Payload object.
    :type network_throughput_test_parameters:
        :py:class:`v1_11_2.web.vo.NetworkThroughputTestParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/network/test/throughput"
    response = engine.post(url, network_throughput_test_parameters.to_dict(dirty=True) if network_throughput_test_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified NetworkThroughputTest object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_2.web.objects.Network
        ThroughputTest.NetworkThroughputTest` object
    :type ref: ``str``
    :rtype: :py:class:`v1_11_2.web.vo.NetworkThroughputTest`
    """
    url = "/resources/json/delphix/network/test/throughput/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['NetworkThroughputTest'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Returns the list of previously executed tests.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_2.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_11_2.web.vo.NetworkThroughputTest`
    """
    url = "/resources/json/delphix/network/test/throughput"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['NetworkThroughputTest'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified NetworkThroughputTest object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_11_2.web.objects.Network
        ThroughputTest.NetworkThroughputTest` object
    :type ref: ``str``
    """
    url = "/resources/json/delphix/network/test/throughput/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

