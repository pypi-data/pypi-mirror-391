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
class CustomJwtAuthorizerForGetAgentKitRuntimeVersion(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForGetAgentKitRuntimeVersion(BaseModel):
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForGetAgentKitRuntimeVersion(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForGetAgentKitRuntimeVersion] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForGetAgentKitRuntimeVersion] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class EnvsForGetAgentKitRuntimeVersion(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TagsForGetAgentKitRuntimeVersion(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForListAgentKitRuntimes(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForListAgentKitRuntimes(BaseModel):
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForListAgentKitRuntimes(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForListAgentKitRuntimes] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForListAgentKitRuntimes] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class EnvsForListAgentKitRuntimes(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TagsForListAgentKitRuntimes(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AgentKitRuntimesForListAgentKitRuntimes(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    artifact_type: Optional[str] = Field(default=None, alias="ArtifactType")
    artifact_url: Optional[str] = Field(default=None, alias="ArtifactUrl")
    authorizer_configuration: Optional[AuthorizerConfigurationForListAgentKitRuntimes] = Field(default=None, alias="AuthorizerConfiguration")
    command: Optional[str] = Field(default=None, alias="Command")
    cpu_milli: Optional[int] = Field(default=None, alias="CpuMilli")
    create_time: Optional[str] = Field(default=None, alias="CreateTime")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    current_version_number: Optional[int] = Field(default=None, alias="CurrentVersionNumber")
    description: Optional[str] = Field(default=None, alias="Description")
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    envs: Optional[list[EnvsForListAgentKitRuntimes]] = Field(default=None, alias="Envs")
    memory_mb: Optional[int] = Field(default=None, alias="MemoryMb")
    name: Optional[str] = Field(default=None, alias="Name")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    status: Optional[str] = Field(default=None, alias="Status")
    tags: Optional[list[TagsForListAgentKitRuntimes]] = Field(default=None, alias="Tags")
    update_time: Optional[str] = Field(default=None, alias="UpdateTime")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForListAgentKitRuntimeVersions(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForListAgentKitRuntimeVersions(BaseModel):
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForListAgentKitRuntimeVersions(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForListAgentKitRuntimeVersions] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForListAgentKitRuntimeVersions] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class EnvsForListAgentKitRuntimeVersions(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AgentKitRuntimeVersionsForListAgentKitRuntimeVersions(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    artifact_type: Optional[str] = Field(default=None, alias="ArtifactType")
    artifact_url: Optional[str] = Field(default=None, alias="ArtifactUrl")
    authorizer_configuration: Optional[AuthorizerConfigurationForListAgentKitRuntimeVersions] = Field(default=None, alias="AuthorizerConfiguration")
    command: Optional[str] = Field(default=None, alias="Command")
    cpu_milli: Optional[int] = Field(default=None, alias="CpuMilli")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    description: Optional[str] = Field(default=None, alias="Description")
    envs: Optional[list[EnvsForListAgentKitRuntimeVersions]] = Field(default=None, alias="Envs")
    is_current_version: Optional[bool] = Field(default=None, alias="IsCurrentVersion")
    memory_mb: Optional[int] = Field(default=None, alias="MemoryMb")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    status: Optional[str] = Field(default=None, alias="Status")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    version_number: Optional[int] = Field(default=None, alias="VersionNumber")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForGetAgentKitRuntime(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForGetAgentKitRuntime(BaseModel):
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForGetAgentKitRuntime(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForGetAgentKitRuntime] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForGetAgentKitRuntime] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class EnvsForGetAgentKitRuntime(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TagsForGetAgentKitRuntime(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateAgentKitRuntime - Request
class AuthorizerConfiguration(BaseModel):
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
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class EnvsItem(BaseModel):
    key: str = Field(..., alias="Key")
    value: str = Field(..., alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class TagsItem(BaseModel):
    key: str = Field(..., alias="Key")
    value: str = Field(..., alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class UpdateAgentKitRuntimeRequest(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    artifact_url: Optional[str] = Field(default=None, alias="ArtifactUrl")
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    description: Optional[str] = Field(default=None, alias="Description")
    release_enable: Optional[bool] = Field(default=None, alias="ReleaseEnable")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    runtime_id: str = Field(..., alias="RuntimeId")
    authorizer_configuration: Optional[AuthorizerConfiguration] = Field(default=None, alias="AuthorizerConfiguration")
    envs: Optional[list[EnvsItem]] = Field(default=None, alias="Envs")
    tags: Optional[list[TagsItem]] = Field(default=None, alias="Tags")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateAgentKitRuntime - Response
class UpdateAgentKitRuntimeResponse(BaseModel):
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateAgentKitRuntime - Request
class AuthorizerConfiguration(BaseModel):
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
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class EnvsItem(BaseModel):
    key: str = Field(..., alias="Key")
    value: str = Field(..., alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class TagsItem(BaseModel):
    key: str = Field(..., alias="Key")
    value: str = Field(..., alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CreateAgentKitRuntimeRequest(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    artifact_type: str = Field(..., alias="ArtifactType")
    artifact_url: str = Field(..., alias="ArtifactUrl")
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    command: Optional[str] = Field(default=None, alias="Command")
    description: Optional[str] = Field(default=None, alias="Description")
    name: str = Field(..., alias="Name")
    project_name: Optional[str] = Field(default=None, alias="ProjectName")
    role_name: str = Field(..., alias="RoleName")
    authorizer_configuration: Optional[AuthorizerConfiguration] = Field(default=None, alias="AuthorizerConfiguration")
    envs: Optional[list[EnvsItem]] = Field(default=None, alias="Envs")
    tags: Optional[list[TagsItem]] = Field(default=None, alias="Tags")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateAgentKitRuntime - Response
class CreateAgentKitRuntimeResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="Id")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ReleaseAgentKitRuntime - Request
class ReleaseAgentKitRuntimeRequest(BaseModel):
    runtime_id: str = Field(..., alias="RuntimeId")
    version_number: Optional[int] = Field(default=None, alias="VersionNumber")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ReleaseAgentKitRuntime - Response
class ReleaseAgentKitRuntimeResponse(BaseModel):
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetAgentKitRuntimeVersion - Request
class GetAgentKitRuntimeVersionRequest(BaseModel):
    runtime_id: str = Field(..., alias="RuntimeId")
    version_number: Optional[int] = Field(default=None, alias="VersionNumber")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetAgentKitRuntimeVersion - Response
class GetAgentKitRuntimeVersionResponse(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    artifact_type: Optional[str] = Field(default=None, alias="ArtifactType")
    artifact_url: Optional[str] = Field(default=None, alias="ArtifactUrl")
    authorizer_configuration: Optional[AuthorizerConfigurationForGetAgentKitRuntimeVersion] = Field(default=None, alias="AuthorizerConfiguration")
    command: Optional[str] = Field(default=None, alias="Command")
    cpu_milli: Optional[int] = Field(default=None, alias="CpuMilli")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    description: Optional[str] = Field(default=None, alias="Description")
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    envs: Optional[list[EnvsForGetAgentKitRuntimeVersion]] = Field(default=None, alias="Envs")
    memory_mb: Optional[int] = Field(default=None, alias="MemoryMb")
    name: Optional[str] = Field(default=None, alias="Name")
    project_name: Optional[str] = Field(default=None, alias="ProjectName")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    status: Optional[str] = Field(default=None, alias="Status")
    tags: Optional[list[TagsForGetAgentKitRuntimeVersion]] = Field(default=None, alias="Tags")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    version_number: Optional[int] = Field(default=None, alias="VersionNumber")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListAgentKitRuntimes - Request
class FiltersItem(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    name_contains: Optional[str] = Field(default=None, alias="NameContains")
    values: Optional[list[str]] = Field(default=None, alias="Values")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ListAgentKitRuntimesRequest(BaseModel):
    create_time_after: Optional[str] = Field(default=None, alias="CreateTimeAfter")
    create_time_before: Optional[str] = Field(default=None, alias="CreateTimeBefore")
    max_results: Optional[int] = Field(default=None, alias="MaxResults")
    next_token: Optional[str] = Field(default=None, alias="NextToken")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    update_time_after: Optional[str] = Field(default=None, alias="UpdateTimeAfter")
    update_time_before: Optional[str] = Field(default=None, alias="UpdateTimeBefore")
    filters: Optional[list[FiltersItem]] = Field(default=None, alias="Filters")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListAgentKitRuntimes - Response
class ListAgentKitRuntimesResponse(BaseModel):
    agent_kit_runtimes: Optional[list[AgentKitRuntimesForListAgentKitRuntimes]] = Field(default=None, alias="AgentKitRuntimes")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    next_token: Optional[str] = Field(default=None, alias="NextToken")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetAgentKitRuntimeCozeToken - Request
class GetAgentKitRuntimeCozeTokenRequest(BaseModel):
    runtime_id: str = Field(..., alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetAgentKitRuntimeCozeToken - Response
class GetAgentKitRuntimeCozeTokenResponse(BaseModel):
    jwt_token: Optional[str] = Field(default=None, alias="JwtToken")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteAgentKitRuntime - Request
class DeleteAgentKitRuntimeRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    runtime_id: str = Field(..., alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteAgentKitRuntime - Response
class DeleteAgentKitRuntimeResponse(BaseModel):
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListAgentKitRuntimeVersions - Request
class ListAgentKitRuntimeVersionsRequest(BaseModel):
    max_results: Optional[int] = Field(default=None, alias="MaxResults")
    next_token: Optional[str] = Field(default=None, alias="NextToken")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    runtime_id: str = Field(..., alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListAgentKitRuntimeVersions - Response
class ListAgentKitRuntimeVersionsResponse(BaseModel):
    agent_kit_runtime_versions: Optional[list[AgentKitRuntimeVersionsForListAgentKitRuntimeVersions]] = Field(default=None, alias="AgentKitRuntimeVersions")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetAgentKitRuntime - Request
class GetAgentKitRuntimeRequest(BaseModel):
    runtime_id: str = Field(..., alias="RuntimeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetAgentKitRuntime - Response
class GetAgentKitRuntimeResponse(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    artifact_type: Optional[str] = Field(default=None, alias="ArtifactType")
    artifact_url: Optional[str] = Field(default=None, alias="ArtifactUrl")
    authorizer_configuration: Optional[AuthorizerConfigurationForGetAgentKitRuntime] = Field(default=None, alias="AuthorizerConfiguration")
    command: Optional[str] = Field(default=None, alias="Command")
    cpu_milli: Optional[int] = Field(default=None, alias="CpuMilli")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    current_version_number: Optional[int] = Field(default=None, alias="CurrentVersionNumber")
    description: Optional[str] = Field(default=None, alias="Description")
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    envs: Optional[list[EnvsForGetAgentKitRuntime]] = Field(default=None, alias="Envs")
    memory_mb: Optional[int] = Field(default=None, alias="MemoryMb")
    name: Optional[str] = Field(default=None, alias="Name")
    project_name: Optional[str] = Field(default=None, alias="ProjectName")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    runtime_id: Optional[str] = Field(default=None, alias="RuntimeId")
    status: Optional[str] = Field(default=None, alias="Status")
    tags: Optional[list[TagsForGetAgentKitRuntime]] = Field(default=None, alias="Tags")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

