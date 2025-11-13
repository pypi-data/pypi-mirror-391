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
Package "service.passwordReset"
"""
from delphixpy.v1_11_30 import response_validator

def get(engine):
    """
    Retrieve the specified PasswordResetConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_30.web.vo.PasswordResetConfig`
    """
    url = "/resources/json/delphix/service/passwordReset"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['PasswordResetConfig'], returns_list=False, raw_result=raw_result)

def set(engine, password_reset_config=None):
    """
    Update the specified PasswordResetConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param password_reset_config: Payload object.
    :type password_reset_config:
        :py:class:`v1_11_30.web.vo.PasswordResetConfig`
    """
    url = "/resources/json/delphix/service/passwordReset"
    response = engine.post(url, password_reset_config.to_dict(dirty=True) if password_reset_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def status(engine):
    """
    Status of PasswordReset Service.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/passwordReset/status"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

def generate_reset_request(engine, password_reset_request_parameters=None):
    """
    Generate a password reset request for a given user.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param password_reset_request_parameters: Payload object.
    :type password_reset_request_parameters:
        :py:class:`v1_11_30.web.vo.PasswordResetRequestParameters`
    """
    url = "/resources/json/delphix/service/passwordReset/generateResetRequest"
    response = engine.post(url, password_reset_request_parameters.to_dict(dirty=True) if password_reset_request_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def validate_reset_request(engine, password_reset_validation_parameters=None):
    """
    Validate a password reset request.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_30.delphix_engine.DelphixEngine`
    :param password_reset_validation_parameters: Payload object.
    :type password_reset_validation_parameters:
        :py:class:`v1_11_30.web.vo.PasswordResetValidationParameters`
    :rtype: :py:class:`v1_11_30.web.vo.PasswordResetValidationResult`
    """
    url = "/resources/json/delphix/service/passwordReset/validateResetRequest"
    response = engine.post(url, password_reset_validation_parameters.to_dict(dirty=True) if password_reset_validation_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['PasswordResetValidationResult'], returns_list=False, raw_result=raw_result)

