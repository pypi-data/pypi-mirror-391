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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Union, Generator
import logging
import requests
import json

logger = logging.getLogger(__name__)


class Runner(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def deploy(self, config: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        pass
    
    @abstractmethod
    def destroy(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def status(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def invoke(self, config: Dict[str, Any], payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, stream: Optional[bool] = None) -> Tuple[bool, Any]:
        """调用服务
        
        Args:
            config: 配置信息
            payload: 请求负载
            headers: 请求头
            stream: 是否使用流式调用。None=自动检测(默认), True=强制流式, False=强制非流式
            
        Returns:
            如果 stream=False: (成功标志, 响应数据)
            如果 stream=True: (成功标志, 生成器对象)
        """
        pass
    
    def _http_post_invoke(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        stream: Optional[bool] = None,
        timeout: int = 60
    ) -> Union[Tuple[bool, Any], Tuple[bool, Generator[Dict[str, Any], None, None]]]:
        """通用的 HTTP POST 调用方法，支持流式和非流式，可自动检测
        
        Args:
            endpoint: 调用端点 URL
            payload: 请求负载
            headers: 请求头
            stream: 是否使用流式调用。None=自动检测，True=强制流式，False=强制非流式
            timeout: 超时时间（秒），流式调用建议使用更长的超时
            
        Returns:
            如果 stream=False: (成功标志, 响应数据字典)
            如果 stream=True: (成功标志, 生成器对象)
        """
        try:
            # 自动检测模式：先尝试建立连接
            auto_detect = stream is None
            if auto_detect:
                logger.debug(f"Auto-detecting stream support for: {endpoint}")
                # 默认先尝试流式
                stream = True
            else:
                logger.debug(f"{'Streaming' if stream else 'Normal'} invoke service: {endpoint}")
            
            # 流式调用使用更长的超时时间
            actual_timeout = timeout if not stream else max(timeout, 300)
            
            response = requests.post(
                url=endpoint,
                json=payload,
                headers=headers,
                timeout=actual_timeout,
                stream=stream
            )
            
            if response.status_code != 200:
                error_msg = f"Invocation failed: {response.status_code} {response.text}"
                logger.error(error_msg)
                return False, error_msg
            
            # 记录响应信息
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # 自动检测：根据 Content-Type 判断
            if auto_detect:
                content_type = response.headers.get('Content-Type', '').lower()
                logger.debug(f"Content-Type: {content_type}")
                is_sse = 'text/event-stream' in content_type
                
                if is_sse:
                    logger.info(f"Detected SSE stream (Content-Type: {content_type})")
                    stream = True
                else:
                    logger.info(f"Detected non-stream response (Content-Type: {content_type})")
                    stream = False
            
            # 非流式调用：直接返回 JSON 响应
            if not stream:
                try:
                    # 记录响应内容用于调试
                    response_text = response.text
                    logger.info(f"Response text length: {len(response_text)}")
                    logger.info(f"Response text preview: {response_text[:200] if response_text else '(empty)'}")
                    
                    # 再次检查：如果响应内容以 "data: " 开头，说明实际是 SSE 流
                    if response_text.strip().startswith("data: "):
                        logger.warning(f"Response looks like SSE stream but Content-Type was not text/event-stream. Switching to stream mode.")
                        logger.warning(f"Using fallback stream parser - entire response ({len(response_text)} bytes) already loaded into memory. "
                                     f"For better performance, ensure server sets 'Content-Type: text/event-stream'.")
                        stream = True
                        # 需要重新处理为流式（注意：此时响应已全部加载到内存，失去了流式的实时性）
                        def event_generator_fallback():
                            """从已读取的文本中解析SSE事件"""
                            logger.debug(f"[FALLBACK] Starting generator, response_text length={len(response_text)}")
                            for i, line in enumerate(response_text.split('\n')):
                                line = line.strip()
                                if not line:
                                    continue
                                logger.debug(f"[FALLBACK] Line {i}: {line[:60]}...")
                                if line.startswith("data: "):
                                    data_str = line[6:].strip()  # 移除 "data: " 前缀并trim
                                    if not data_str:
                                        continue
                                    try:
                                        event_data = json.loads(data_str)
                                        logger.debug(f"[FALLBACK] Parsed JSON successfully, type={type(event_data)}")
                                        yield event_data
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"Failed to parse SSE data: {data_str[:100]}, error: {e}")
                                        # 跳过无法解析的行
                                        continue
                        return True, event_generator_fallback()
                    
                    # 正常的 JSON 响应
                    response_data = response.json()
                    logger.info(f"Successfully parsed JSON response")
                    return True, response_data
                except ValueError as e:
                    error_msg = f"Response parsing failed: {str(e)}"
                    logger.error(error_msg)
                    logger.error(f"Response content: {response.text[:500]}")
                    return False, error_msg
            
            # 流式调用：返回生成器
            else:
                def event_generator():
                    """生成器函数：逐行解析 SSE 格式的流式响应"""
                    try:
                        for line in response.iter_lines(decode_unicode=True):
                            if not line:
                                continue
                            
                            line = line.strip()
                            logger.debug(f"[STREAM] Raw line: {line[:80]}")
                            
                            # SSE 格式: "data: {json}\n\n"
                            if line.startswith("data: "):
                                data_str = line[6:].strip()  # 移除 "data: " 前缀并 trim
                                
                                if not data_str:
                                    # 空数据，跳过
                                    continue
                                
                                try:
                                    event_data = json.loads(data_str)
                                    logger.debug(f"[STREAM] Yielding parsed dict")
                                    yield event_data
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse event data: {data_str[:100]}, error: {e}")
                                    # 跳过无法解析的行，不 yield 字符串
                                    continue
                            else:
                                # 不是 data: 开头的行，可能是注释或其他SSE元数据，跳过
                                if line.startswith(":"):
                                    # SSE 注释行，跳过
                                    logger.debug(f"[STREAM] Comment line, skipping")
                                    continue
                                elif line:
                                    logger.debug(f"[STREAM] Non-SSE line, skipping: {line[:80]}")
                                    continue
                    except Exception as e:
                        logger.error(f"Error in stream processing: {str(e)}")
                        yield {"error": str(e)}
                
                return True, event_generator()
                
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {actual_timeout} seconds"
            logger.error(error_msg)
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Invocation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
