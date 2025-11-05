"""
Gradio Client Adapter for Qwen3-VL-Demo
适配 Hugging Face Space 上的 Qwen3-VL-Demo API
"""

from gradio_client import Client, handle_file
import base64
from typing import List, Dict, Any
import os


class GradioQwenAdapter:
    """
    适配器：让 Gradio Client 的调用方式兼容 langchain_openai.ChatOpenAI 的接口
    """
    
    def __init__(self, space_name: str = "Qwen/Qwen3-VL-Demo", max_tokens: int = 2048, timeout: int = 300):
        """
        Args:
            space_name: Hugging Face Space 名称
            max_tokens: 最大token数（目前Gradio API不支持，仅作为兼容参数）
            timeout: API调用超时时间（秒），默认300秒（5分钟）
        """
        print(f"🔗 连接到 Hugging Face Space: {space_name}")
        print(f"⏱️  超时设置: {timeout}秒")
        self.client = Client(space_name)
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.model_name = "qwen3-vl"  # 用于日志显示
        print("✅ Gradio Client 初始化完成")
        
    def invoke(self, messages: List[Any]) -> Any:
        """
        模拟 ChatOpenAI.invoke() 接口
        
        Args:
            messages: LangChain 格式的消息列表
                例如: [("system", "..."), HumanMessage(content=[...])]
        
        Returns:
            模拟的 response 对象，包含 .content 属性
        """
        # 提取最后一条 HumanMessage 的内容
        human_message = None
        for msg in messages:
            if hasattr(msg, 'content'):  # HumanMessage
                human_message = msg
                break
        
        if human_message is None:
            raise ValueError("No HumanMessage found in messages")
        
        # 解析 content（可能包含文本和图片）
        text_content = ""
        image_paths = []
        
        if isinstance(human_message.content, str):
            # 纯文本
            text_content = human_message.content
        elif isinstance(human_message.content, list):
            # 多模态内容
            for item in human_message.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")
                elif item.get("type") == "image_url":
                    # 从 base64 data URI 中提取图片并保存为临时文件
                    image_url = item.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image"):
                        # 保存为临时文件
                        temp_path = self._save_base64_image(image_url)
                        image_paths.append(temp_path)
        
        # 构造 Gradio API 调用参数
        input_value = {
            "files": [handle_file(img_path) for img_path in image_paths] if image_paths else None,
            "text": text_content
        }
        
        # 调用 Gradio API
        import time
        print(f"📡 正在调用 Gradio API (超时: {self.timeout}秒)...")
        print(f"   图片数量: {len(image_paths)}")
        print(f"   文本长度: {len(text_content)} 字符")
        
        start_time = time.time()
        try:
            # 使用 submit() + result() 方式支持超时控制
            job = self.client.submit(
                input_value=input_value,
                api_name="/add_message"
            )
            
            # 等待结果，带超时
            print(f"⏳ 等待响应...")
            result = job.result(timeout=self.timeout)
            
            elapsed = time.time() - start_time
            print(f"✅ 收到响应 (耗时: {elapsed:.1f}秒)")
            
            # 解析返回结果（新的API格式）
            # result[1] 是一个包含 'value' 键的字典
            # result[1]['value'] 是消息列表
            # 最后一条消息是 AI 的回复
            # content 是一个列表，最后一项包含文本
            messages_data = result[1]['value']
            last_message = messages_data[-1]
            content_items = last_message['content']
            
            # 提取文本内容（通常是最后一个 content 项）
            response_text = ""
            for item in content_items:
                if item.get('type') == 'text':
                    response_text = item.get('content', '')
            
            if not response_text:
                raise ValueError(f"无法从返回结果中提取文本: {last_message}")
            
            print(f"📝 响应长度: {len(response_text)} 字符")
            
            # 清理临时文件
            for img_path in image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
            
            # 返回模拟的 response 对象
            return MockResponse(response_text)
            
        except TimeoutError:
            elapsed = time.time() - start_time
            print(f"❌ API 调用超时 ({elapsed:.1f}秒)")
            print(f"⚠️  Hugging Face Space 可能负载过高")
            print(f"💡 建议:")
            print(f"   1. 稍后重试")
            print(f"   2. 或切换到阿里云百炼 API（付费但稳定）")
            # 清理临时文件
            for img_path in image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
            raise RuntimeError(f"Gradio API timeout after {self.timeout}s")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ API 调用失败 (耗时: {elapsed:.1f}秒)")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   错误信息: {str(e)[:200]}")
            # 清理临时文件
            for img_path in image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
            raise RuntimeError(f"Gradio API call failed: {e}")
    
    def _save_base64_image(self, data_uri: str) -> str:
        """
        从 data:image/jpeg;base64,... 格式的 URI 中提取并保存图片
        
        Returns:
            临时文件路径
        """
        import tempfile
        import re
        
        # 提取 base64 数据
        match = re.match(r'data:image/(\w+);base64,(.+)', data_uri)
        if not match:
            raise ValueError("Invalid data URI format")
        
        image_format = match.group(1)  # jpeg, png, etc.
        base64_data = match.group(2)
        
        # 解码并保存
        image_data = base64.b64decode(base64_data)
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f".{image_format}"
        )
        temp_file.write(image_data)
        temp_file.close()
        
        return temp_file.name


class MockResponse:
    """模拟 ChatOpenAI 的 response 对象"""
    
    def __init__(self, content: str):
        self.content = content
    
    def __str__(self):
        return self.content
    
    def __repr__(self):
        return f"MockResponse(content={self.content[:50]}...)"
