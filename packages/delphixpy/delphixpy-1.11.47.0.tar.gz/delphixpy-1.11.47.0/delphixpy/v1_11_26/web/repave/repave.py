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
Package "repave"
"""
from delphixpy.v1_11_26 import response_validator

def get(engine):
    """
    Retrieve the specified RepaveStatus object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_26.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_26.web.vo.RepaveStatus`
    """
    url = "/resources/json/delphix/repave"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['RepaveStatus'], returns_list=False, raw_result=raw_result)

def prepare(engine, repave_prepare_parameters):
    """
    Initiate repave in the source engine.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_26.delphix_engine.DelphixEngine`
    :param repave_prepare_parameters: Payload object.
    :type repave_prepare_parameters:
        :py:class:`v1_11_26.web.vo.RepavePrepareParameters`
    """
    url = "/resources/json/delphix/repave/prepare"
    response = engine.post(url, repave_prepare_parameters.to_dict(dirty=True) if repave_prepare_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def apply(engine, repave_apply_parameters):
    """
    Apply repave to target engine.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_26.delphix_engine.DelphixEngine`
    :param repave_apply_parameters: Payload object.
    :type repave_apply_parameters:
        :py:class:`v1_11_26.web.vo.RepaveApplyParameters`
    """
    url = "/resources/json/delphix/repave/apply"
    response = engine.post(url, repave_apply_parameters.to_dict(dirty=True) if repave_apply_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def preview(engine, repave_preview_parameters):
    """
    Preview source engine info before applying Repave in target engine.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_26.delphix_engine.DelphixEngine`
    :param repave_preview_parameters: Payload object.
    :type repave_preview_parameters:
        :py:class:`v1_11_26.web.vo.RepavePreviewParameters`
    :rtype: :py:class:`v1_11_26.web.vo.RepavePreviewResult`
    """
    url = "/resources/json/delphix/repave/preview"
    response = engine.post(url, repave_preview_parameters.to_dict(dirty=True) if repave_preview_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['RepavePreviewResult'], returns_list=False, raw_result=raw_result)

