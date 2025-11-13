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
class CustomJwtAuthorizerForListTools(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForListTools(BaseModel):
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForListTools(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForListTools] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForListTools] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TagsForListTools(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ToolsForListTools(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    authorizer_configuration: Optional[AuthorizerConfigurationForListTools] = Field(default=None, alias="AuthorizerConfiguration")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    description: Optional[str] = Field(default=None, alias="Description")
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    name: Optional[str] = Field(default=None, alias="Name")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    status: Optional[str] = Field(default=None, alias="Status")
    tags: Optional[list[TagsForListTools]] = Field(default=None, alias="Tags")
    tool_id: Optional[str] = Field(default=None, alias="ToolId")
    tool_type: Optional[str] = Field(default=None, alias="ToolType")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CustomJwtAuthorizerForGetTool(BaseModel):
    allowed_clients: Optional[list[str]] = Field(default=None, alias="AllowedClients")
    discovery_url: Optional[str] = Field(default=None, alias="DiscoveryUrl")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KeyAuthForGetTool(BaseModel):
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    api_key_location: Optional[str] = Field(default=None, alias="ApiKeyLocation")
    api_key_name: Optional[str] = Field(default=None, alias="ApiKeyName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AuthorizerConfigurationForGetTool(BaseModel):
    custom_jwt_authorizer: Optional[CustomJwtAuthorizerForGetTool] = Field(default=None, alias="CustomJwtAuthorizer")
    key_auth: Optional[KeyAuthForGetTool] = Field(default=None, alias="KeyAuth")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TagsForGetTool(BaseModel):
    key: Optional[str] = Field(default=None, alias="Key")
    value: Optional[str] = Field(default=None, alias="Value")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateTool - Request
class UpdateToolRequest(BaseModel):
    description: Optional[str] = Field(default=None, alias="Description")
    tool_id: str = Field(..., alias="ToolId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateTool - Response
class UpdateToolResponse(BaseModel):
    tool_id: Optional[str] = Field(default=None, alias="ToolId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListTools - Request
class FiltersItem(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    name_contains: Optional[str] = Field(default=None, alias="NameContains")
    values: Optional[list[str]] = Field(default=None, alias="Values")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ListToolsRequest(BaseModel):
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


# ListTools - Response
class ListToolsResponse(BaseModel):
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    tools: Optional[list[ToolsForListTools]] = Field(default=None, alias="Tools")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteTool - Request
class DeleteToolRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    tool_id: str = Field(..., alias="ToolId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteTool - Response
class DeleteToolResponse(BaseModel):
    tool_id: Optional[str] = Field(default=None, alias="ToolId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateTool - Request
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
class NetworkConfiguration(BaseModel):
    network_type: str = Field(..., alias="NetworkType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class Network(BaseModel):
    vpc_configuration: Optional[VpcConfiguration] = Field(default=None, alias="VpcConfiguration")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class VpcConfiguration(BaseModel):
    security_group_ids: Optional[list[str]] = Field(default=None, alias="SecurityGroupIds")
    subnet_ids: Optional[list[str]] = Field(default=None, alias="SubnetIds")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    
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


class CreateToolRequest(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    command: Optional[str] = Field(default=None, alias="Command")
    description: Optional[str] = Field(default=None, alias="Description")
    name: str = Field(..., alias="Name")
    project_name: Optional[str] = Field(default=None, alias="ProjectName")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    tool_type: str = Field(..., alias="ToolType")
    authorizer_configuration: Optional[AuthorizerConfiguration] = Field(default=None, alias="AuthorizerConfiguration")
    envs: Optional[list[EnvsItem]] = Field(default=None, alias="Envs")
    network_configuration: Optional[NetworkConfiguration] = Field(default=None, alias="NetworkConfiguration")
    tags: Optional[list[TagsItem]] = Field(default=None, alias="Tags")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateTool - Response
class CreateToolResponse(BaseModel):
    tool_id: Optional[str] = Field(default=None, alias="ToolId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetTool - Request
class GetToolRequest(BaseModel):
    tool_id: str = Field(..., alias="ToolId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetTool - Response
class GetToolResponse(BaseModel):
    apmplus_enable: Optional[bool] = Field(default=None, alias="ApmplusEnable")
    authorizer_configuration: Optional[AuthorizerConfigurationForGetTool] = Field(default=None, alias="AuthorizerConfiguration")
    created_at: Optional[str] = Field(default=None, alias="CreatedAt")
    description: Optional[str] = Field(default=None, alias="Description")
    endpoint: Optional[str] = Field(default=None, alias="Endpoint")
    name: Optional[str] = Field(default=None, alias="Name")
    role_name: Optional[str] = Field(default=None, alias="RoleName")
    status: Optional[str] = Field(default=None, alias="Status")
    tags: Optional[list[TagsForGetTool]] = Field(default=None, alias="Tags")
    tool_id: Optional[str] = Field(default=None, alias="ToolId")
    tool_type: Optional[str] = Field(default=None, alias="ToolType")
    updated_at: Optional[str] = Field(default=None, alias="UpdatedAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

