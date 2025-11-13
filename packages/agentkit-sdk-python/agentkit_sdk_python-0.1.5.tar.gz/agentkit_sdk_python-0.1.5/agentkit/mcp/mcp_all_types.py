# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Auto-generated from API JSON definition
# Do not edit manually

from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Data Types
class TlsSettingsForGetMCPService(BaseModel):
    tls_mode: Optional[str] = Field(default=None, alias="TlsMode")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomConfigurationForGetMCPService(BaseModel):
    domain: Optional[str] = Field(default=None, alias="Domain")
    port: Optional[int] = Field(default=None, alias="Port")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType")
    tls_settings: Optional[TlsSettingsForGetMCPService] = Field(default=None, alias="TlsSettings")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class FunctionConfigurationForGetMCPService(BaseModel):
    function_id: Optional[str] = Field(default=None, alias="FunctionId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class BackendConfigurationForGetMCPService(BaseModel):
    custom_configuration: Optional[CustomConfigurationForGetMCPService] = Field(default=None, alias="CustomConfiguration")
    function_configuration: Optional[FunctionConfigurationForGetMCPService] = Field(default=None, alias="FunctionConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForGetMCPService(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ApiKeysForGetMCPService(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    name: Optional[str] = Field(default=None, alias="Name")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForGetMCPService(BaseModel):
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_keys: Optional[list[ApiKeysForGetMCPService]] = Field(default=None, alias="ApiKeys")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerForGetMCPService(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForGetMCPService] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForGetMCPService] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class InboundAuthorizerConfigurationForGetMCPService(BaseModel):
    authorizer: Optional[AuthorizerForGetMCPService] = Field(default=None, alias="Authorizer")
    authorizer_type: Optional[str] = Field(default=None, alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class VpcConfigForGetMCPService(BaseModel):
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class NetworkConfigurationsForGetMCPService(BaseModel):
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    vpc_config: Optional[VpcConfigForGetMCPService] = Field(default=None, alias="VpcConfig")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForGetMCPService(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ApiKeysForGetMCPService(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    name: Optional[str] = Field(default=None, alias="Name")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForGetMCPService(BaseModel):
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_keys: Optional[list[ApiKeysForGetMCPService]] = Field(default=None, alias="ApiKeys")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerForGetMCPService(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForGetMCPService] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForGetMCPService] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class OutboundAuthorizerConfigurationForGetMCPService(BaseModel):
    authorizer: Optional[AuthorizerForGetMCPService] = Field(default=None, alias="Authorizer")
    authorizer_type: Optional[str] = Field(default=None, alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ProtocolConfigurationForGetMCPService(BaseModel):
    protocol_convert_configuration: Optional[str] = Field(default=None, alias="ProtocolConvertConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPServiceForGetMCPService(BaseModel):
    backend_configuration: Optional[BackendConfigurationForGetMCPService] = Field(default=None, alias="BackendConfiguration")
    backend_type: Optional[str] = Field(default=None, alias="BackendType")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    inbound_authorizer_configuration: Optional[InboundAuthorizerConfigurationForGetMCPService] = Field(default=None, alias="InboundAuthorizerConfiguration")
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    name: Optional[str] = Field(default=None, alias="Name")
    network_configurations: Optional[list[NetworkConfigurationsForGetMCPService]] = Field(default=None, alias="NetworkConfigurations")
    outbound_authorizer_configuration: Optional[OutboundAuthorizerConfigurationForGetMCPService] = Field(default=None, alias="OutboundAuthorizerConfiguration")
    path: Optional[str] = Field(default=None, alias="Path")
    protocol_configuration: Optional[ProtocolConfigurationForGetMCPService] = Field(default=None, alias="ProtocolConfiguration")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForGetMCPToolset(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ApiKeysForGetMCPToolset(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    name: Optional[str] = Field(default=None, alias="Name")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForGetMCPToolset(BaseModel):
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_keys: Optional[list[ApiKeysForGetMCPToolset]] = Field(default=None, alias="ApiKeys")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerForGetMCPToolset(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForGetMCPToolset] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForGetMCPToolset] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForGetMCPToolset(BaseModel):
    authorizer: Optional[AuthorizerForGetMCPToolset] = Field(default=None, alias="Authorizer")
    authorizer_type: Optional[str] = Field(default=None, alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class VpcConfigForGetMCPToolset(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class NetworkConfigurationsForGetMCPToolset(BaseModel):
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    vpc_config: Optional[VpcConfigForGetMCPToolset] = Field(default=None, alias="VpcConfig")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ProtocolConfigurationForGetMCPToolset(BaseModel):
    protocol_convert_configuration: Optional[str] = Field(default=None, alias="ProtocolConvertConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPServicesForGetMCPToolset(BaseModel):
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    name: Optional[str] = Field(default=None, alias="Name")
    network_configurations: Optional[list[NetworkConfigurationsForGetMCPToolset]] = Field(default=None, alias="NetworkConfigurations")
    path: Optional[str] = Field(default=None, alias="Path")
    protocol_configuration: Optional[ProtocolConfigurationForGetMCPToolset] = Field(default=None, alias="ProtocolConfiguration")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType")
    status: Optional[str] = Field(default=None, alias="Status")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class VpcConfigForGetMCPToolset(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class NetworkConfigurationsForGetMCPToolset(BaseModel):
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    vpc_config: Optional[VpcConfigForGetMCPToolset] = Field(default=None, alias="VpcConfig")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPToolsetForGetMCPToolset(BaseModel):
    authorizer_configuration: Optional[AuthorizerConfigurationForGetMCPToolset] = Field(default=None, alias="AuthorizerConfiguration")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    m_c_p_services: Optional[list[MCPServicesForGetMCPToolset]] = Field(default=None, alias="MCPServices")
    m_c_p_toolset_id: Optional[str] = Field(default=None, alias="MCPToolsetId")
    name: Optional[str] = Field(default=None, alias="Name")
    network_configurations: Optional[list[NetworkConfigurationsForGetMCPToolset]] = Field(default=None, alias="NetworkConfigurations")
    path: Optional[str] = Field(default=None, alias="Path")
    status: Optional[str] = Field(default=None, alias="Status")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class VpcConfigForListMCPServices(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class NetworkConfigurationsForListMCPServices(BaseModel):
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    vpc_config: Optional[VpcConfigForListMCPServices] = Field(default=None, alias="VpcConfig")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ProtocolConfigurationForListMCPServices(BaseModel):
    protocol_convert_configuration: Optional[str] = Field(default=None, alias="ProtocolConvertConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPServicesForListMCPServices(BaseModel):
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    name: Optional[str] = Field(default=None, alias="Name")
    network_configurations: Optional[list[NetworkConfigurationsForListMCPServices]] = Field(default=None, alias="NetworkConfigurations")
    path: Optional[str] = Field(default=None, alias="Path")
    protocol_configuration: Optional[ProtocolConfigurationForListMCPServices] = Field(default=None, alias="ProtocolConfiguration")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType")
    status: Optional[str] = Field(default=None, alias="Status")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPServiceToolsForListMCPTools(BaseModel):
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    tools: Optional[str] = Field(default=None, alias="Tools")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForListMCPToolsets(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ApiKeysForListMCPToolsets(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    name: Optional[str] = Field(default=None, alias="Name")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForListMCPToolsets(BaseModel):
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_keys: Optional[list[ApiKeysForListMCPToolsets]] = Field(default=None, alias="ApiKeys")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerForListMCPToolsets(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForListMCPToolsets] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForListMCPToolsets] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForListMCPToolsets(BaseModel):
    authorizer: Optional[AuthorizerForListMCPToolsets] = Field(default=None, alias="Authorizer")
    authorizer_type: Optional[str] = Field(default=None, alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class VpcConfigForListMCPToolsets(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class NetworkConfigurationsForListMCPToolsets(BaseModel):
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    vpc_config: Optional[VpcConfigForListMCPToolsets] = Field(default=None, alias="VpcConfig")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ProtocolConfigurationForListMCPToolsets(BaseModel):
    protocol_convert_configuration: Optional[str] = Field(default=None, alias="ProtocolConvertConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPServicesForListMCPToolsets(BaseModel):
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    name: Optional[str] = Field(default=None, alias="Name")
    network_configurations: Optional[list[NetworkConfigurationsForListMCPToolsets]] = Field(default=None, alias="NetworkConfigurations")
    path: Optional[str] = Field(default=None, alias="Path")
    protocol_configuration: Optional[ProtocolConfigurationForListMCPToolsets] = Field(default=None, alias="ProtocolConfiguration")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType")
    status: Optional[str] = Field(default=None, alias="Status")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class VpcConfigForListMCPToolsets(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class NetworkConfigurationsForListMCPToolsets(BaseModel):
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    vpc_config: Optional[VpcConfigForListMCPToolsets] = Field(default=None, alias="VpcConfig")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MCPToolsetsForListMCPToolsets(BaseModel):
    authorizer_configuration: Optional[AuthorizerConfigurationForListMCPToolsets] = Field(default=None, alias="AuthorizerConfiguration")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    m_c_p_services: Optional[list[MCPServicesForListMCPToolsets]] = Field(default=None, alias="MCPServices")
    m_c_p_toolset_id: Optional[str] = Field(default=None, alias="MCPToolsetId")
    name: Optional[str] = Field(default=None, alias="Name")
    network_configurations: Optional[list[NetworkConfigurationsForListMCPToolsets]] = Field(default=None, alias="NetworkConfigurations")
    path: Optional[str] = Field(default=None, alias="Path")
    status: Optional[str] = Field(default=None, alias="Status")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMCPToolset - Request
class AuthorizerConfiguration(BaseModel):
    authorizer_type: str = Field(..., alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Authorizer(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizer] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuth] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class CustomJwtAuthorizer(BaseModel):
    discovery_url: str = Field(..., alias="DiscoveryUrl")
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class KeyAuth(BaseModel):
    api_key_location: str = Field(..., alias="ApiKeyLocation")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ApiKeysItem(BaseModel):
    name: str = Field(..., alias="Name")
    key: Optional[str] = Field(default=None, alias="Key")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class UpdateMCPToolsetRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    m_c_p_service_ids: Optional[str] = Field(default=None, alias="MCPServiceIds")
    m_c_p_toolset_id: str = Field(..., alias="MCPToolsetId")
    authorizer_configuration: Optional[AuthorizerConfiguration] = Field(default=None, alias="AuthorizerConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMCPToolset - Response
class UpdateMCPToolsetResponse(BaseModel):
    m_c_p_toolset_id: Optional[str] = Field(default=None, alias="MCPToolsetId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMCPTools - Request
class UpdateMCPToolsRequest(BaseModel):
    m_c_p_service_id: str = Field(..., alias="MCPServiceId")
    tools: str = Field(..., alias="Tools")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMCPTools - Response
class UpdateMCPToolsResponse(BaseModel):
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMCPTools - Request
class GetMCPToolsRequest(BaseModel):
    m_c_p_toolset_id: str = Field(..., alias="MCPToolsetId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMCPTools - Response
class GetMCPToolsResponse(BaseModel):
    tools: Optional[str] = Field(default=None, alias="Tools")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteMCPToolset - Request
class DeleteMCPToolsetRequest(BaseModel):
    m_c_p_toolset_id: str = Field(..., alias="MCPToolsetId", description="MCP工具集ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteMCPToolset - Response
class DeleteMCPToolsetResponse(BaseModel):
    m_c_p_toolset_id: Optional[str] = Field(default=None, alias="MCPToolsetId", description="MCP工具集ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMCPService - Request
class GetMCPServiceRequest(BaseModel):
    m_c_p_service_id: str = Field(..., alias="MCPServiceId", description="MCP服务ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMCPService - Response
class GetMCPServiceResponse(BaseModel):
    m_c_p_service: Optional[MCPServiceForGetMCPService] = Field(default=None, alias="MCPService")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMCPToolset - Request
class GetMCPToolsetRequest(BaseModel):
    m_c_p_toolset_id: str = Field(..., alias="MCPToolsetId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMCPToolset - Response
class GetMCPToolsetResponse(BaseModel):
    m_c_p_toolset: Optional[MCPToolsetForGetMCPToolset] = Field(default=None, alias="MCPToolset")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMCPServices - Request
class FiltersItem(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    name_contains: Optional[str] = Field(default=None, alias="NameContains")
    values: Optional[list[str]] = Field(default=None, alias="Values")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ListMCPServicesRequest(BaseModel):
    max_results: Optional[int] = Field(default=None, alias="MaxResults")
    next_token: Optional[str] = Field(default=None, alias="NextToken")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    filters: Optional[list[FiltersItem]] = Field(default=None, alias="Filters")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMCPServices - Response
class ListMCPServicesResponse(BaseModel):
    m_c_p_services: Optional[list[MCPServicesForListMCPServices]] = Field(default=None, alias="MCPServices")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMCPService - Request
class BackendConfiguration(BaseModel):
    custom_configuration: Optional[CustomConfiguration] = Field(default=None, alias="CustomConfiguration")
    function_configuration: Optional[FunctionConfiguration] = Field(default=None, alias="FunctionConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class CustomConfiguration(BaseModel):
    domain: Optional[str] = Field(default=None, alias="Domain")
    port: Optional[int] = Field(default=None, alias="Port")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType")
    tls_settings: Optional[TlsSettings] = Field(default=None, alias="TlsSettings")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class TlsSettings(BaseModel):
    tls_mode: str = Field(..., alias="TlsMode")
    sni: Optional[str] = Field(default=None, alias="Sni")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class FunctionConfiguration(BaseModel):
    function_id: Optional[str] = Field(default=None, alias="FunctionId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class InboundAuthorizerConfiguration(BaseModel):
    authorizer_type: str = Field(..., alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Authorizer(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizer] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuth] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class CustomJwtAuthorizer(BaseModel):
    discovery_url: str = Field(..., alias="DiscoveryUrl")
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class KeyAuth(BaseModel):
    api_key_location: str = Field(..., alias="ApiKeyLocation")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Network(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class OutboundAuthorizerConfiguration(BaseModel):
    authorizer_type: str = Field(..., alias="AuthorizerType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Authorizer(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizer] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuth] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class CustomJwtAuthorizer(BaseModel):
    discovery_url: str = Field(..., alias="DiscoveryUrl")
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class KeyAuth(BaseModel):
    api_key_location: str = Field(..., alias="ApiKeyLocation")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ApiKeysItem(BaseModel):
    name: str = Field(..., alias="Name")
    key: Optional[str] = Field(default=None, alias="Key")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class VpcConfigurationItem(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class NetworkConfigurationsItem(BaseModel):
    network_type: str = Field(..., alias="NetworkType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ApiKeysItem(BaseModel):
    name: str = Field(..., alias="Name")
    key: Optional[str] = Field(default=None, alias="Key")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class UpdateMCPServiceRequest(BaseModel):
    backend_type: Optional[str] = Field(default=None, alias="BackendType")
    m_c_p_service_id: str = Field(..., alias="MCPServiceId")
    backend_configuration: Optional[BackendConfiguration] = Field(default=None, alias="BackendConfiguration")
    inbound_authorizer_configuration: Optional[InboundAuthorizerConfiguration] = Field(default=None, alias="InboundAuthorizerConfiguration")
    network_configurations: Optional[list[NetworkConfigurationsItem]] = Field(default=None, alias="NetworkConfigurations")
    outbound_authorizer_configuration: Optional[OutboundAuthorizerConfiguration] = Field(default=None, alias="OutboundAuthorizerConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMCPService - Response
class UpdateMCPServiceResponse(BaseModel):
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteMCPService - Request
class DeleteMCPServiceRequest(BaseModel):
    m_c_p_service_id: str = Field(..., alias="MCPServiceId", description="MCP服务ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteMCPService - Response
class DeleteMCPServiceResponse(BaseModel):
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId", description="MCP服务ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMCPTools - Request
class ListMCPToolsRequest(BaseModel):
    m_c_p_toolset_ids: str = Field(..., alias="MCPToolsetIds")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMCPTools - Response
class ListMCPToolsResponse(BaseModel):
    m_c_p_service_tools: Optional[list[MCPServiceToolsForListMCPTools]] = Field(default=None, alias="MCPServiceTools")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMCPToolsets - Request
class FiltersItem(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    name_contains: Optional[str] = Field(default=None, alias="NameContains")
    values: Optional[list[str]] = Field(default=None, alias="Values")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ListMCPToolsetsRequest(BaseModel):
    max_results: Optional[int] = Field(default=None, alias="MaxResults")
    next_token: Optional[str] = Field(default=None, alias="NextToken")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    filters: Optional[list[FiltersItem]] = Field(default=None, alias="Filters")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMCPToolsets - Response
class ListMCPToolsetsResponse(BaseModel):
    m_c_p_toolsets: Optional[list[MCPToolsetsForListMCPToolsets]] = Field(default=None, alias="MCPToolsets")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateMCPToolset - Request
class AuthorizerConfiguration(BaseModel):
    authorizer_type: str = Field(..., alias="AuthorizerType", description="访问MCP工具集的认证类型，可选：ApiKey")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Authorizer(BaseModel):
    key_auth: Optional[KeyAuth] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class KeyAuth(BaseModel):
    api_key_location: str = Field(..., alias="ApiKeyLocation", description="访问MCP工具集网关，ApiKey传递的位置。")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Network(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ApiKeysItem(BaseModel):
    name: str = Field(..., alias="Name", description="ApiKey名称，长度为4-64的字符串，由字母、数字、“-”和“_”组成")
    key: Optional[str] = Field(default=None, alias="Key", description="MCP工具集的入口鉴权ApiKey，留空默认随机生成一个字符串")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class VpcConfigurationItem(BaseModel):
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds", description="需要进行内网访问MCP工具集的子网ID")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId", description="需要进行内网访问MCP工具集的私有网络ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class NetworkConfigurationsItem(BaseModel):
    network_type: str = Field(..., alias="NetworkType", description="需要开启的访问类型，如：公网、私网")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CreateMCPToolsetRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken", description="保证请求幂等性。由客户端自动生成一个参数值，确保不同请求间该参数值唯一，避免当调用API超时或服务器内部错误时，客户端多次重试导致重复性操作。取值：仅支持ASCII字符，且不能超过64个字符。")
    m_c_p_service_ids: str = Field(..., alias="MCPServiceIds", description="MCP服务的资源ID列表")
    name: str = Field(..., alias="Name", description="MCP工具集名称，长度为4-64的字符串，由字母、数字、“-”和“_”组成")
    path: str = Field(..., alias="Path", description="MCP工具集的访问路径，例如 /mcp")
    authorizer_configuration: Optional[AuthorizerConfiguration] = Field(default=None, alias="AuthorizerConfiguration")
    network_configurations: Optional[list[NetworkConfigurationsItem]] = Field(default=None, alias="NetworkConfigurations")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateMCPToolset - Response
class CreateMCPToolsetResponse(BaseModel):
    m_c_p_toolset_id: Optional[str] = Field(default=None, alias="MCPToolsetId", description="MCP工具集ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateMCPService - Request
class BackendConfiguration(BaseModel):
    custom_configuration: Optional[CustomConfiguration] = Field(default=None, alias="CustomConfiguration")
    function_configuration: Optional[FunctionConfiguration] = Field(default=None, alias="FunctionConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class CustomConfiguration(BaseModel):
    domain: Optional[str] = Field(default=None, alias="Domain", description="自定义后端场景的域名")
    port: Optional[int] = Field(default=None, alias="Port", description="自定义后端场景的端口")
    protocol_type: Optional[str] = Field(default=None, alias="ProtocolType", description="自定义后端类型")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class FunctionConfiguration(BaseModel):
    function_id: Optional[str] = Field(default=None, alias="FunctionId", description="VeFaas函数ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class InboundAuthorizerConfiguration(BaseModel):
    authorizer_type: str = Field(..., alias="AuthorizerType", description="访问MCP服务的认证类型，可选：ApiKey")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Authorizer(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class KeyAuth(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Network(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class OutboundAuthorizerConfiguration(BaseModel):
    authorizer_type: str = Field(..., alias="AuthorizerType", description="访问MCP服务的认证类型，可选：ApiKey")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Authorizer(BaseModel):
    key_auth: Optional[KeyAuth] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class KeyAuth(BaseModel):
    api_key_location: str = Field(..., alias="ApiKeyLocation", description="MCP服务网关对应后端服务使用ApiKey鉴权时，ApiKey传递的位置。")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ProtocolConfiguration(BaseModel):
    http_api_configuration: Optional[HttpApiConfiguration] = Field(default=None, alias="HttpApiConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class HttpApiConfiguration(BaseModel):
    configuration: Optional[str] = Field(default=None, alias="Configuration", description="MCP后端服务的接口描述，如：Swagger 的json，需要进行Base64编码")
    type: Optional[str] = Field(default=None, alias="Type", description="当后端接口为HTTP时，后端接口的展示形式，如：Swagger")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ApiKeysItem(BaseModel):
    name: str = Field(..., alias="Name", description="ApiKey名称，长度为4-64的字符串，由字母、数字、“-”和“_”组成")
    key: Optional[str] = Field(default=None, alias="Key", description="MCP服务的入口鉴权ApiKey，留空默认随机生成一个字符串")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class VpcConfigurationItem(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds", description="网卡关联的安全组ID。")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds", description="需要进行内网访问MCP服务的子网ID")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId", description="需要进行内网访问MCP服务的私有网络ID")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class NetworkConfigurationsItem(BaseModel):
    network_type: str = Field(..., alias="NetworkType", description="需要开启的访问类型，如：公网、私网")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class ApiKeysItem(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key", description="MCP服务对于的后端服务鉴权ApiKey。")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CreateMCPServiceRequest(BaseModel):
    backend_type: str = Field(..., alias="BackendType", description="MCP后端服务的类型，可选：Function（对应VeFaas函数）、Domain（自定义域名和端口）")
    client_token: Optional[str] = Field(default=None, alias="ClientToken", description="保证请求幂等性。由客户端自动生成一个参数值，确保不同请求间该参数值唯一，避免当调用API超时或服务器内部错误时，客户端多次重试导致重复性操作。取值：仅支持ASCII字符，且不能超过64个字符。")
    name: str = Field(..., alias="Name", description="MCP服务名称，长度为4-64的字符串，由字母、数字、“-”和“_”组成")
    path: str = Field(..., alias="Path", description="后端MCP服务的访问路径，例如 /mcp ")
    protocol_type: str = Field(..., alias="ProtocolType", description="MCP服务后端协议类型。")
    backend_configuration: Optional[BackendConfiguration] = Field(default=None, alias="BackendConfiguration")
    inbound_authorizer_configuration: Optional[InboundAuthorizerConfiguration] = Field(default=None, alias="InboundAuthorizerConfiguration")
    network_configurations: Optional[list[NetworkConfigurationsItem]] = Field(default=None, alias="NetworkConfigurations")
    outbound_authorizer_configuration: Optional[OutboundAuthorizerConfiguration] = Field(default=None, alias="OutboundAuthorizerConfiguration")
    protocol_configuration: Optional[ProtocolConfiguration] = Field(default=None, alias="ProtocolConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateMCPService - Response
class CreateMCPServiceResponse(BaseModel):
    m_c_p_service_id: Optional[str] = Field(default=None, alias="MCPServiceId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

