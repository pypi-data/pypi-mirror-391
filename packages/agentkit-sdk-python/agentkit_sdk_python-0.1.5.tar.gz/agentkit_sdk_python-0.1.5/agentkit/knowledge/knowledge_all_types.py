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
class KnowledgeBasesForListKnowledgeBases(BaseModel):
    create_time: Optional[str] = Field(default=None, alias="CreateTime")
    description: Optional[str] = Field(default=None, alias="Description")
    knowledge_id: Optional[str] = Field(default=None, alias="KnowledgeId")
    last_update_time: Optional[str] = Field(default=None, alias="LastUpdateTime")
    name: Optional[str] = Field(default=None, alias="Name")
    provider_knowledge_id: Optional[str] = Field(default=None, alias="ProviderKnowledgeId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class KnowledgeBasesForAddKnowledgeBase(BaseModel):
    knowledge_id: Optional[str] = Field(default=None, alias="KnowledgeId")
    provider_knowledge_id: Optional[str] = Field(default=None, alias="ProviderKnowledgeId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ConnectionInfosForGetKnowledgeConnectionInfo(BaseModel):
    auth_key: Optional[str] = Field(default=None, alias="AuthKey")
    auth_type: Optional[str] = Field(default=None, alias="AuthType")
    base_url: Optional[str] = Field(default=None, alias="BaseUrl")
    expire_at: Optional[str] = Field(default=None, alias="ExpireAt")
    extra_config: Optional[str] = Field(default=None, alias="ExtraConfig")
    region: Optional[str] = Field(default=None, alias="Region")
    vpc_id: Optional[str] = Field(default=None, alias="VpcId")
    vpc_name: Optional[str] = Field(default=None, alias="VpcName")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListKnowledgeBases - Request
class FiltersItem(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    name_contains: Optional[str] = Field(default=None, alias="NameContains")
    values: Optional[list[str]] = Field(default=None, alias="Values")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ListKnowledgeBasesRequest(BaseModel):
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


# ListKnowledgeBases - Response
class ListKnowledgeBasesResponse(BaseModel):
    knowledge_bases: Optional[list[KnowledgeBasesForListKnowledgeBases]] = Field(default=None, alias="KnowledgeBases")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# AddKnowledgeBase - Request
class KnowledgeBasesItem(BaseModel):
    name: str = Field(..., alias="Name")
    provider_knowledge_id: str = Field(..., alias="ProviderKnowledgeId")
    provider_type: str = Field(..., alias="ProviderType")
    description: Optional[str] = Field(default=None, alias="Description")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AddKnowledgeBaseRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    project_name: Optional[str] = Field(default=None, alias="ProjectName")
    knowledge_bases: Optional[list[KnowledgeBasesItem]] = Field(default=None, alias="KnowledgeBases")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# AddKnowledgeBase - Response
class AddKnowledgeBaseResponse(BaseModel):
    knowledge_bases: Optional[list[KnowledgeBasesForAddKnowledgeBase]] = Field(default=None, alias="KnowledgeBases")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetKnowledgeConnectionInfo - Request
class GetKnowledgeConnectionInfoRequest(BaseModel):
    knowledge_id: str = Field(..., alias="KnowledgeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetKnowledgeConnectionInfo - Response
class GetKnowledgeConnectionInfoResponse(BaseModel):
    connection_infos: Optional[list[ConnectionInfosForGetKnowledgeConnectionInfo]] = Field(default=None, alias="ConnectionInfos")
    error_message: Optional[str] = Field(default=None, alias="ErrorMessage")
    knowledge_id: Optional[str] = Field(default=None, alias="KnowledgeId")
    provider_knowledge_id: Optional[str] = Field(default=None, alias="ProviderKnowledgeId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteKnowledgeBase - Request
class DeleteKnowledgeBaseRequest(BaseModel):
    knowledge_id: str = Field(..., alias="KnowledgeId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteKnowledgeBase - Response
class DeleteKnowledgeBaseResponse(BaseModel):
    knowledge_id: Optional[str] = Field(default=None, alias="KnowledgeId")
    provider_knowledge_id: Optional[str] = Field(default=None, alias="ProviderKnowledgeId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    request_id: Optional[str] = Field(default=None, alias="RequestId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

