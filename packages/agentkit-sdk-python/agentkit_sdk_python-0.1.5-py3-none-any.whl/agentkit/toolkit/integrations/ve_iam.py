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

from volcenginesdkcore.rest import ApiException
import volcenginesdkcore
import volcenginesdkecs
import volcenginesdkcr
import volcenginesdkiam
import os
import logging
from agentkit.client.base_client import BaseAgentkitClient,ApiConfig
logger = logging.getLogger(__name__)

from agentkit.utils.ve_sign import get_volc_ak_sk_region

# 禁用火山引擎SDK的日志输出
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('volcenginesdkcore').setLevel(logging.ERROR)
logging.getLogger('volcenginesdkiam').setLevel(logging.ERROR)
logging.getLogger('volcenginesdkcore.rest').setLevel(logging.ERROR)
logging.getLogger('volcenginesdkcore.api_client').setLevel(logging.ERROR)

# 完全禁用日志输出
logging.disable(logging.CRITICAL)



class VeIAM:
    def __init__(
        self,
        access_key: str = "",
        secret_key: str = "",
        region: str = "",
    ) -> None:
        if not any([access_key, secret_key, region]):
            access_key, secret_key, region = get_volc_ak_sk_region('IAM')
        else:
            if not all([access_key, secret_key, region]):
                raise ValueError("Error create iam instance: missing access key, secret key or region")
        configuration = volcenginesdkcore.Configuration()
        configuration.ak = access_key
        configuration.sk = secret_key
        configuration.region = region
        volcenginesdkcore.Configuration.set_default(configuration)
        self.api_instance = volcenginesdkiam.IAMApi()
    
    def get_user_by_name(self, user_name: str):
        """Get user by name"""
        get_user_request = volcenginesdkiam.GetUserRequest(
            user_name=user_name,
        )
        try:
            resp :volcenginesdkiam.GetUserResponse = self.api_instance.get_user(get_user_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->get_user: %s\n" % e)
            raise e
        return resp

    def get_user_by_uid(self, uid: str):
        """Get user by uid"""
        get_user_request = volcenginesdkiam.GetUserRequest(
            id=uid,
        )
        try:
            resp :volcenginesdkiam.GetUserResponse = self.api_instance.get_user(get_user_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->get_user: %s\n" % e)
            raise e
        return resp
    
    def get_user_by_access_key_id(self, access_key_id: str = None):
        """Get user by access key id"""
        if access_key_id is None:
            access_key_id,_,_ = get_volc_ak_sk_region('IAM')
        get_user_request = volcenginesdkiam.GetUserRequest(
            access_key_id=access_key_id,
        )
        try:
            resp :volcenginesdkiam.GetUserResponse = self.api_instance.get_user(get_user_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->get_user: %s\n" % e)
            raise e
        return resp
        

    def list_users(self):
        """List users"""
        list_users_request = volcenginesdkiam.ListUsersRequest()
        try:
            resp :volcenginesdkiam.ListUsersResponse = self.api_instance.list_users(list_users_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->list_users: %s\n" % e)
        return resp
    
    def list_roles(self):
        """List roles"""
        list_roles_request = volcenginesdkiam.ListRolesRequest()
        try:
            resp :volcenginesdkiam.ListRolesResponse = self.api_instance.list_roles(list_roles_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->list_roles: %s\n" % e)
            raise e
        return resp
    
    def get_role(self, role_name: str):
        """Get role"""
        get_role_request = volcenginesdkiam.GetRoleRequest(
            role_name=role_name,
        )
        try:
            resp :volcenginesdkiam.GetRoleResponse = self.api_instance.get_role(get_role_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->get_role: %s\n" % e)
            if e.status == 404:
                return None
            raise e
        return resp

    def create_role(self, role_name: str, trust_policy_document: str):
        """Create role"""
        create_role_request = volcenginesdkiam.CreateRoleRequest(
            display_name=role_name,
            role_name=role_name,
            trust_policy_document=trust_policy_document,
        )
        
        try:
            resp :volcenginesdkiam.CreateRoleResponse = self.api_instance.create_role(create_role_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->create_role: %s\n" % e)
            raise e
        return resp
    

    def attach_role_policy(self, role_name: str, policy_name: str, policy_type: str):
        """Attach role policy"""
        attach_role_policy_request = volcenginesdkiam.AttachRolePolicyRequest(
            role_name=role_name,
            policy_name=policy_name,
            policy_type=policy_type,
        )
        try:
            resp :volcenginesdkiam.AttachRolePolicyResponse = self.api_instance.attach_role_policy(attach_role_policy_request)
        except ApiException as e:
            logger.error("Exception when calling IAMApi->attach_role_policy: %s\n" % e)
            raise e
        return resp
    
    def ensure_role_for_agentkit(self, role_name: str) -> bool:
        """Ensure role for agentkit"""
        resp = self.get_role(role_name)
        agentkit_service_code = os.getenv("VOLC_AGENTKIT_SERVICE")
        service = 'vefaas'
        if agentkit_service_code and 'stg' in agentkit_service_code:
            service = 'vefaas_dev'
        trust_policy_document = '{"Statement":[{"Effect":"Allow","Action":["sts:AssumeRole"],"Principal":{"Service":["%s"]}}]}' % service
        if resp is None:
            resp = self.create_role(role_name, trust_policy_document)
            '''
            ArkReadOnlyAccess
            TLSReadOnlyAccess
            APMPlusServerReadOnlyAccess
            VikingdbReadOnlyAccess
            ESCloudReadOnlyAccess
            LLMShieldProtectSdkAccess
            AgentKitReadOnlyAccess
            TorchlightApiFullAccess
            '''
            policies = [
                "ArkReadOnlyAccess",
                "TLSReadOnlyAccess",
                "APMPlusServerReadOnlyAccess",
                "VikingdbReadOnlyAccess",
                "ESCloudReadOnlyAccess",
                "LLMShieldProtectSdkAccess",
                "AgentKitReadOnlyAccess",
                "TorchlightApiFullAccess",
            ]
            for policy in policies:
                self.attach_role_policy(role_name, policy_name=policy, policy_type="System")
        return True
    




if __name__ == '__main__':
    ve_iam = VeIAM()
    resp = ve_iam.list_users()
    print(resp)
    resp = ve_iam.list_roles()
    print(resp)
    print("="*20)
    resp = ve_iam.get_role(role_name="ServiceRoleForVeFaaS")
    print(resp)
    print("="*20)
    ak,_,_ = get_volc_ak_sk_region('IAM')
    resp = ve_iam.get_user_by_access_key_id(ak)
    print(resp)
