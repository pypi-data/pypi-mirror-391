import asyncio
from fastchat_hq import OpenAIChatClient

# ============== 使用示例 ==============
"""
async def example_basic():
    print("=== 基础使用示例 ===")

    async with OpenAIChatClient(
        api_key="6b87ba5a-f465-48a8-9a56-1f6d57d3042d",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        model="deepseek-v3-250324",
        temperature=0.7,
        max_concurrent=5
    ) as client:
        response = await client.chat(
            user_message="介绍一下 Python 的异步编程",
            system_message="你是一个编程助手"
        )
        print(f"回答: {response}\n")

"""
"""
async def example_concurrent():
    print("=== 并发请求示例 ===")
    
    async with OpenAIChatClient(max_concurrent=10,api_key="6b87ba5a-f465-48a8-9a56-1f6d57d3042d",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        model="deepseek-v3-250324") as client:
        # 准备多个问题
        questions = [
            "什么是机器学习？",
            "什么是深度学习？",
            "什么是神经网络？",
            "什么是自然语言处理？",
            "什么是计算机视觉？"
        ]
        
        # 并发执行所有请求
        tasks = [client.chat(q) for q in questions]
        results = await asyncio.gather(*tasks)
        
        for q, a in zip(questions, results):
            print(f"Q: {q}")
            print(f"A: {a[:100]}...\n")
"""
"""
async def example_batch():
    print("=== 批量处理示例 ===")
    
    async with OpenAIChatClient(max_concurrent=5,
        api_key="6b87ba5a-f465-48a8-9a56-1f6d57d3042d",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        model="deepseek-v3-250324"
        ) as client:
        requests = [
            {
                "user_message": "翻译成英文：你好，世界",
                "system_message": "你是一个翻译助手"
            },
            {
                "user_message": "翻译成英文：机器学习很有趣",
                "system_message": "你是一个翻译助手"
            },
            {
                "user_message": "翻译成英文：人工智能改变世界",
                "system_message": "你是一个翻译助手"
            }
        ]
        
        results = await client.chat_batch(requests, show_progress=True)
        
        for i, result in enumerate(results, 1):
            print(f"结果 {i}: {result}\n")
"""
# """
async def example_stream():
    print("=== 流式响应示例 ===")
    
    async with OpenAIChatClient(
        api_key="6b87ba5a-f465-48a8-9a56-1f6d57d3042d",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        model="deepseek-v3-250324"
        ) as client:
        print("流式输出: ", end="", flush=True)
        
        async for chunk in client.chat_stream(
            user_message="写一首关于春天的短诗",
            system_message="你是一个诗人"
        ):
            print(chunk, end="", flush=True)
        
        print("\n")

# """
"""
async def example_with_history():
    print("=== 带历史对话示例 ===")
    
    async with OpenAIChatClient(
        api_key="6b87ba5a-f465-48a8-9a56-1f6d57d3042d",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        model="deepseek-v3-250324"
        ) as client:
        history = []
        
        # 第一轮对话
        response1 = await client.chat(
            user_message="我叫张三，今年25岁",
            system_message="你是一个友好的助手"
        )
        print(f"助手: {response1}")
        history.append({"role": "user", "content": "我叫张三，今年25岁"})
        history.append({"role": "assistant", "content": response1})
        
        # 第二轮对话（带历史）
        response2 = await client.chat(
            user_message="我刚才说我叫什么？",
            system_message="你是一个友好的助手",
            history=history
        )
        print(f"助手: {response2}\n")
"""

async def example_high_concurrency():
    """高并发压力测试示例"""
    print("=== 高并发测试（50个请求）===")
    
    async with OpenAIChatClient(
            max_concurrent=20,
            api_key="6b87ba5a-f465-48a8-9a56-1f6d57d3042d",
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            model="deepseek-v3-250324"
        ) as client:
        import time
        start = time.time()
        
        # 创建50个请求
        tasks = [
            client.chat(f"用一句话介绍数字 {i}")
            for i in range(50)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start
        success = sum(1 for r in results if not isinstance(r, Exception))
        
        print(f"完成 {success}/{len(tasks)} 个请求")
        print(f"总耗时: {elapsed:.2f} 秒")
        print(f"平均耗时: {elapsed/len(tasks):.2f} 秒/请求\n")


async def main():
    """运行所有示例"""
    # 设置你的 API Key
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # await example_basic()
    # await example_concurrent()
    # await example_batch()
    await example_stream()

    # await example_with_history()
    # await example_high_concurrency()


if __name__ == "__main__":
    asyncio.run(main())