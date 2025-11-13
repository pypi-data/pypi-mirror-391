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
class StrategiesForUpdateMemoryCollection(BaseModel):
    custom_extraction_instructions: Optional[str] = Field(default=None, alias="CustomExtractionInstructions")
    name: Optional[str] = Field(default=None, alias="Name")
    type: Optional[str] = Field(default=None, alias="Type")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class LongTermConfigurationForUpdateMemoryCollection(BaseModel):
    strategies: Optional[list[StrategiesForUpdateMemoryCollection]] = Field(default=None, alias="Strategies")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MemoriesForListMemoryCollections(BaseModel):
    create_time: Optional[str] = Field(default=None, alias="CreateTime")
    description: Optional[str] = Field(default=None, alias="Description")
    last_update_time: Optional[str] = Field(default=None, alias="LastUpdateTime")
    managed: Optional[bool] = Field(default=None, alias="Managed")
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    name: Optional[str] = Field(default=None, alias="Name")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    strategies_count: Optional[int] = Field(default=None, alias="StrategiesCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CollectionsForAddMemoryCollection(BaseModel):
    error_message: Optional[str] = Field(default=None, alias="ErrorMessage")
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ConnectionInfoForGetMemoryCollection(BaseModel):
    auth_key: Optional[str] = Field(default=None, alias="AuthKey")
    auth_type: Optional[str] = Field(default=None, alias="AuthType")
    base_url: Optional[str] = Field(default=None, alias="BaseUrl")
    expire_at: Optional[str] = Field(default=None, alias="ExpireAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class StrategiesForGetMemoryCollection(BaseModel):
    custom_extraction_instructions: Optional[str] = Field(default=None, alias="CustomExtractionInstructions")
    name: Optional[str] = Field(default=None, alias="Name")
    type: Optional[str] = Field(default=None, alias="Type")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class LongTermConfigurationForGetMemoryCollection(BaseModel):
    strategies: Optional[list[StrategiesForGetMemoryCollection]] = Field(default=None, alias="Strategies")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ConnectionInfosForGetMemoryConnectionInfo(BaseModel):
    auth_key: Optional[str] = Field(default=None, alias="AuthKey")
    auth_type: Optional[str] = Field(default=None, alias="AuthType")
    base_url: Optional[str] = Field(default=None, alias="BaseUrl")
    expire_at: Optional[str] = Field(default=None, alias="ExpireAt")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMemoryCollection - Request
class LongTermConfiguration(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class StrategiesItem(BaseModel):
    name: str = Field(..., alias="Name")
    type: str = Field(..., alias="Type")
    custom_extraction_instructions: Optional[str] = Field(default=None, alias="CustomExtractionInstructions")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class UpdateMemoryCollectionRequest(BaseModel):
    description: Optional[str] = Field(default=None, alias="Description")
    memory_id: str = Field(..., alias="MemoryId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# UpdateMemoryCollection - Response
class UpdateMemoryCollectionResponse(BaseModel):
    long_term_configuration: Optional[LongTermConfigurationForUpdateMemoryCollection] = Field(default=None, alias="LongTermConfiguration")
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateMemoryCollection - Request
class LongTermConfiguration(BaseModel):
    pass
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }
class StrategiesItem(BaseModel):
    name: str = Field(..., alias="Name")
    type: str = Field(..., alias="Type")
    custom_extraction_instructions: Optional[str] = Field(default=None, alias="CustomExtractionInstructions")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class CreateMemoryCollectionRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    description: Optional[str] = Field(default=None, alias="Description")
    name: str = Field(..., alias="Name")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# CreateMemoryCollection - Response
class CreateMemoryCollectionResponse(BaseModel):
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteMemoryCollection - Request
class DeleteMemoryCollectionRequest(BaseModel):
    memory_id: str = Field(..., alias="MemoryId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# DeleteMemoryCollection - Response
class DeleteMemoryCollectionResponse(BaseModel):
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# ListMemoryCollections - Request
class FiltersItem(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    name_contains: Optional[str] = Field(default=None, alias="NameContains")
    values: Optional[list[str]] = Field(default=None, alias="Values")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ListMemoryCollectionsRequest(BaseModel):
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


# ListMemoryCollections - Response
class ListMemoryCollectionsResponse(BaseModel):
    memories: Optional[list[MemoriesForListMemoryCollections]] = Field(default=None, alias="Memories")
    page_number: Optional[int] = Field(default=None, alias="PageNumber")
    page_size: Optional[int] = Field(default=None, alias="PageSize")
    total_count: Optional[int] = Field(default=None, alias="TotalCount")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# AddMemoryCollection - Request
class CollectionsItem(BaseModel):
    provider_collection_id: str = Field(..., alias="ProviderCollectionId")
    description: Optional[str] = Field(default=None, alias="Description")
    name: Optional[str] = Field(default=None, alias="Name")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AddMemoryCollectionRequest(BaseModel):
    client_token: Optional[str] = Field(default=None, alias="ClientToken")
    collections: Optional[list[CollectionsItem]] = Field(default=None, alias="Collections")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# AddMemoryCollection - Response
class AddMemoryCollectionResponse(BaseModel):
    collections: Optional[list[CollectionsForAddMemoryCollection]] = Field(default=None, alias="Collections")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMemoryCollection - Request
class GetMemoryCollectionRequest(BaseModel):
    memory_id: str = Field(..., alias="MemoryId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMemoryCollection - Response
class GetMemoryCollectionResponse(BaseModel):
    connection_info: Optional[ConnectionInfoForGetMemoryCollection] = Field(default=None, alias="ConnectionInfo")
    create_time: Optional[str] = Field(default=None, alias="CreateTime")
    description: Optional[str] = Field(default=None, alias="Description")
    last_update_time: Optional[str] = Field(default=None, alias="LastUpdateTime")
    long_term_configuration: Optional[LongTermConfigurationForGetMemoryCollection] = Field(default=None, alias="LongTermConfiguration")
    managed: Optional[bool] = Field(default=None, alias="Managed")
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    name: Optional[str] = Field(default=None, alias="Name")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    trn: Optional[str] = Field(default=None, alias="Trn")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMemoryConnectionInfo - Request
class GetMemoryConnectionInfoRequest(BaseModel):
    memory_id: str = Field(..., alias="MemoryId")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


# GetMemoryConnectionInfo - Response
class GetMemoryConnectionInfoResponse(BaseModel):
    connection_infos: Optional[list[ConnectionInfosForGetMemoryConnectionInfo]] = Field(default=None, alias="ConnectionInfos")
    managed: Optional[bool] = Field(default=None, alias="Managed")
    memory_id: Optional[str] = Field(default=None, alias="MemoryId")
    provider_collection_id: Optional[str] = Field(default=None, alias="ProviderCollectionId")
    provider_type: Optional[str] = Field(default=None, alias="ProviderType")
    status: Optional[str] = Field(default=None, alias="Status")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

