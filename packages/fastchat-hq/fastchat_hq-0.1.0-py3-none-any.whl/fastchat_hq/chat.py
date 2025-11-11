import os
import asyncio
from typing import List, Dict, Optional, AsyncIterator
from openai import AsyncOpenAI
import aiohttp


class OpenAIChatClient:
    """
    封装 OpenAI Chat Completions 接口的高性能异步客户端。
    支持并发请求、连接池、流式响应等特性。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 512,
        max_concurrent: int = 10,
        timeout: float = 30.0,
        **kwargs
    ):
        """
        :param api_key: OpenAI API Key。如果 None，则从环境变量读取。
        :param base_url: API Base URL。如果 None，则从环境变量读取或使用默认值。
        :param model: 模型名称
        :param temperature: 温度，控制生成的随机性
        :param max_tokens: 最大输出 token 数
        :param max_concurrent: 最大并发请求数
        :param timeout: 请求超时时间（秒）
        :param kwargs: 其它 openai 参数
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 未设置")

        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        # 使用新版 AsyncOpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
            max_retries=2
        )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._extra_params = kwargs

        # 并发控制信号量
        self.semaphore = asyncio.Semaphore(max_concurrent)

    def build_messages(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        构建 messages 列表。
        """
        messages: List[Dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})
        return messages

    async def chat(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        **override_params
    ) -> str:
        """
        异步调用 Chat 接口并返回模型的内容。
        自动进行并发控制。
        """
        async with self.semaphore:  # 并发控制
            messages = self.build_messages(user_message, system_message, history)

            params = {
                "model": override_params.get("model", self.model),
                "temperature": override_params.get("temperature", self.temperature),
                "max_tokens": override_params.get("max_tokens", self.max_tokens),
                **self._extra_params
            }
            params.update({k: v for k, v in override_params.items() if k not in params})

            response = await self.client.chat.completions.create(
                messages=messages,
                **params
            )
            return response.choices[0].message.content

    async def chat_stream(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        **override_params
    ) -> AsyncIterator[str]:
        """
        流式返回 Chat 内容，适合实时展示。
        """
        async with self.semaphore:
            messages = self.build_messages(user_message, system_message, history)

            params = {
                "model": override_params.get("model", self.model),
                "temperature": override_params.get("temperature", self.temperature),
                "max_tokens": override_params.get("max_tokens", self.max_tokens),
                **self._extra_params
            }
            params.update({k: v for k, v in override_params.items() if k not in params})

            stream = await self.client.chat.completions.create(
                messages=messages,
                stream=True,
                **params
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    async def chat_batch(
        self,
        requests: List[Dict],
        show_progress: bool = False
    ) -> List[str]:
        """
        批量并发处理多个请求。
        :param requests: 请求列表，每个元素包含 user_message, system_message, history 等
        :param show_progress: 是否显示进度
        :return: 结果列表
        """
        tasks = []
        for req in requests:
            task = self.chat(
                user_message=req.get("user_message", ""),
                system_message=req.get("system_message"),
                history=req.get("history"),
                **req.get("override_params", {})
            )
            tasks.append(task)

        if show_progress:
            results = []
            for i, task in enumerate(asyncio.as_completed(tasks), 1):
                result = await task
                results.append(result)
                print(f"进度: {i}/{len(tasks)}")
            return results
        else:
            return await asyncio.gather(*tasks, return_exceptions=True)

    async def close(self):
        """关闭客户端连接"""
        await self.client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

