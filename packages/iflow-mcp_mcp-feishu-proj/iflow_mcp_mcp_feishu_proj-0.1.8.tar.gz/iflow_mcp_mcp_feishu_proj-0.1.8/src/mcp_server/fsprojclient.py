#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
飞书项目Open API客户端
基于飞书项目Open API文档实现
"""

import os
import json
import time
import requests
from typing import Dict, List, Union, Optional, Any, Tuple, Literal

# Define custom type for work item types
WorkItemType = Literal["story", "version", "issue"]
class FSProjClient:
    """飞书项目Open API客户端"""

    def __init__(
        self,
        base_url: str,
        project_key: str,
        plugin_id: str = None,
        plugin_secret: str = None,
        plugin_token: str = None,
        user_key: str = None,
        user_plugin_token: str = None,
        refresh_token: str = None,
    ):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL，例如 https://project.feishu.cn
            project_key: 项目标识
            plugin_id: 插件ID
            plugin_secret: 插件密钥
            plugin_token: 插件身份凭证，如果提供则不需要plugin_id和plugin_secret
            user_key: 用户标识，当使用插件身份凭证时需要
            user_plugin_token: 用户身份凭证，如果提供则不需要user_key
            refresh_token: 刷新token，用于刷新user_plugin_token
        """
        self.base_url = base_url.rstrip("/")
        self.project_key = project_key
        self.plugin_id = plugin_id
        self.plugin_secret = plugin_secret
        self.plugin_token = plugin_token
        self.plugin_token_expires_time = 0
        self.user_key = user_key
        self.user_plugin_token = user_plugin_token
        self.refresh_token = refresh_token
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        
        Returns:
            请求头字典
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.user_plugin_token:
            headers["X-PLUGIN-TOKEN"] = self.user_plugin_token
        elif self.plugin_token:
            headers["X-PLUGIN-TOKEN"] = self.plugin_token
            if self.user_key:
                headers["X-USER-KEY"] = self.user_key
        
        return headers
    
    def _request(
        self,
        method: str,
        path: str,
        params: Dict = None,
        data: Dict = None,
        json_data: Dict = None,
        files: Dict = None,
        headers: Dict = None,
        idem_uuid: str = None,
    ) -> Dict:
        """
        发送请求
        
        Args:
            method: 请求方法，GET, POST, PUT, DELETE等
            path: 请求路径
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            files: 文件数据
            headers: 额外的请求头
            idem_uuid: 幂等UUID
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{path}"
        
        req_headers = self._get_headers()
        
        if headers:
            req_headers.update(headers)
        
        if idem_uuid:
            req_headers["X-IDEM-UUID"] = idem_uuid

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                files=files,
                headers=req_headers,
            )
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            if e.response.content:
                try:
                    error_data = e.response.json()
                    raise Exception(f"API错误: {error_data.get('err_msg', str(e))}, 错误码: {error_data.get('err_code')}")
                except json.JSONDecodeError:
                    raise Exception(f"HTTP错误: {str(e)}, 响应内容: {e.response.text}")
            raise Exception(f"HTTP错误: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求错误: {str(e)}")
        except json.JSONDecodeError:
            raise Exception(f"JSON解析错误: {response.text}")
    
    # ===== 认证相关 =====
    
    def get_plugin_token(self) -> str:
        """
        获取plugin_token
        
        Returns:
            plugin_token
        """
        if not self.plugin_id or not self.plugin_secret:
            raise Exception("plugin_id和plugin_secret不能为空")
        
        if self.plugin_token and time.time() < self.plugin_token_expires_time:
            return self.plugin_token
        data = {
            "plugin_id": self.plugin_id,
            "plugin_secret": self.plugin_secret,
        }
        
        response = self._request("POST", "/open_api/authen/plugin_token", json_data=data)
        self.plugin_token = response.get("data", {}).get("token")
        # expires_in为有效期秒数，expire_time为过期时间戳
        expires_in = int(response.get("data", {}).get("expire_time"))
        expires_time = time.time() + expires_in
        self.plugin_token_expires_time = expires_time
        return self.plugin_token
    
    def get_auth_code(self, state: str = "111", cookie: str = None) -> str:
        """
        获取code
        
        Args:
            state: 状态参数
            cookie: 用户cookie
            
        Returns:
            auth_code
        """
        if not self.plugin_id:
            raise Exception("plugin_id不能为空")
        
        data = {
            "plugin_id": self.plugin_id,
            "state": state,
        }
        
        headers = {"cookie": cookie} if cookie else {}
        
        response = self._request(
            "POST", 
            "/open_api/authen/auth_code", 
            json_data=data,
            headers=headers
        )
        return response.get("data", {}).get("code")
    
    def get_user_plugin_token(self, code: str) -> Dict:
        """
        获取user_plugin_token
        
        Args:
            code: 授权码
            
        Returns:
            包含user_plugin_token和refresh_token的字典
        """
        if not self.plugin_token:
            raise Exception("plugin_token不能为空")
        
        data = {
            "code": code,
            "grant_type": "authorization_code",
        }
        
        response = self._request(
            "POST", 
            "/open_api/authen/user_plugin_token", 
            json_data=data
        )
        
        result = response.get("data", {})
        self.user_plugin_token = result.get("user_plugin_token")
        self.refresh_token = result.get("refresh_token")
        
        return {
            "user_plugin_token": self.user_plugin_token,
            "refresh_token": self.refresh_token,
            "expires_in": result.get("expires_in"),
        }
    
    def refresh_user_token(self, refresh_token: str = None, token_type: int = 1) -> Dict:
        """
        刷新用户token
        
        Args:
            refresh_token: 刷新token，如果不提供则使用实例中的refresh_token
            token_type: token类型，1表示user_plugin_token
            
        Returns:
            包含新token的字典
        """
        if not self.plugin_token:
            raise Exception("plugin_token不能为空")
        
        refresh_token = refresh_token or self.refresh_token
        if not refresh_token:
            raise Exception("refresh_token不能为空")
        
        data = {
            "refresh_token": refresh_token,
            "type": token_type,
        }
        
        response = self._request(
            "POST", 
            "/open_api/authen/refresh_token", 
            json_data=data
        )
        
        result = response.get("data", {})
        self.user_plugin_token = result.get("user_plugin_token")
        self.refresh_token = result.get("refresh_token")
        
        return {
            "user_plugin_token": self.user_plugin_token,
            "refresh_token": self.refresh_token,
            "expires_in": result.get("expires_in"),
        }
    
    # ===== 视图相关 =====
    def get_view_list(self, work_item_type_key: WorkItemType, created_by: str = "", page_num: int = 1, page_size: int = 100) -> Dict:
        """获取视图列表及配置信息
        
        Args:
            work_item_type_key: 工作项类型标识
            created_by: 创建者标识
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            视图列表及配置信息
        """
        
        data = {
            "work_item_type_key": work_item_type_key,
            "page_num": page_num,
            "page_size": page_size,
            "created_by": created_by
        }
        response = self._request(
            "POST", 
            f"/open_api/{self.project_key}/view_conf/list", 
            json_data=data
        )
        err_code = response.get("code", 0)
        if err_code != 0:
            raise Exception(f"获取视图列表及配置信息失败，错误码: {err_code}, 错误信息: {response.get('err_msg')}")
        return response.get("data", {})
    
    def get_view_detail(self, view_id: str, page_num: int = 1, page_size: int = 20) -> Dict:
        """获取视图工作项列表
        
        Args:
            view_id: 视图标识
            page_num: 页码
            page_size: 每页数量
            
        """
        
        data = {
            "page_num": page_num,
            "page_size": page_size
        }
        response = self._request(
            "GET", 
            f"/open_api/{self.project_key}/fix_view/{view_id}", 
            params=data
        )
        err_code = response.get("code", 0)
        if err_code != 0:
            raise Exception(f"获取视图工作项列表失败，错误码: {err_code}, 错误信息: {response.get('err_msg')}")
        return response.get("data", {})
    

    # ===== 工作项相关 =====
    def get_workitem_detail(self, work_item_type_key: WorkItemType, work_item_ids: List[int]) -> List[Dict]:
        """获取工作项详情
        
        Args:
            work_item_type_key: 工作项类型标识
            
        """
        data = {
            "work_item_ids": work_item_ids
        }
        
        response = self._request(
            "POST", 
            f"/open_api/{self.project_key}/work_item/{work_item_type_key}/query",
            json_data=data
        )
        err_code = response.get("code", 0)
        if err_code != 0:
            raise Exception(f"获取工作项详情失败，错误码: {err_code}, 错误信息: {response.get('err_msg')}")
        return response.get("data", {})
    

    def get_work_item_type_meta(self, work_item_type_key: WorkItemType) -> Dict:
        """获取工作项类型元数据
        
        - 在工作项详情的"fields"字段中各个字段的具体意义及信息可以在工作项类型元数据中获取

        Args:
            work_item_type_key: 工作项类型标识
            
        Returns:
            工作项类型元数据
        """
        response = self._request(
            "GET", 
            f"/open_api/{self.project_key}/work_item/{work_item_type_key}/meta"
        )
        err_code = response.get("code", 0)
        if err_code != 0:
            raise Exception(f"获取工作项类型元数据失败，错误码: {err_code}, 错误信息: {response.get('err_msg')}")
        return response.get("data", {})
    
    def get_flow_roles(self, work_item_type_key: WorkItemType) -> Dict:
        """获取流程角色配置详情
        
        Args:
            work_item_type_key: 工作项类型标识，可选值为"story"、"version"、"issue"
            
        Returns:
            流程角色配置详情
        """
        response = self._request(
            "GET", 
            f"/open_api/{self.project_key}/flow_roles/{work_item_type_key}"
        )
        err_code = response.get("code", 0)
        if err_code != 0:
            raise Exception(f"获取流程角色配置详情失败，错误码: {err_code}, 错误信息: {response.get('err_msg')}")
        return response.get("data", {})
