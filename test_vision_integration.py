"""
测试LayoutVLM的Vision集成是否正常工作
"""
import os
import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from PIL import Image
import io

# 从环境变量读取配置
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

if not API_KEY:
    print("❌ 请设置环境变量 OPENAI_API_KEY")
    exit(1)

print("=" * 60)
print("🧪 测试LangChain ChatOpenAI的Vision功能")
print("=" * 60)

# 创建测试图片
print("\n1️⃣ 创建测试图片...")
img = Image.new('RGB', (100, 100), color='blue')
buffer = io.BytesIO()
img.save(buffer, format='PNG')
img_base64 = base64.b64encode(buffer.getvalue()).decode()
print("   ✅ 已创建100x100蓝色图片")

# 测试不带base_url的情况
print("\n2️⃣ 测试默认配置 (不带base_url)...")
try:
    llm_default = ChatOpenAI(
        model_name="gpt-4o",
        max_tokens=100,
        api_key=API_KEY
    )
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": "What color is this image? Answer in one word."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_base64}"}
            }
        ]
    )
    
    response = llm_default.invoke([message])
    print(f"   📨 回答: {response.content}")
    
    if 'blue' in response.content.lower():
        print("   ✅ 默认配置工作正常")
    else:
        print("   ⚠️  可能未正确识别图片")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 测试带base_url的情况
if BASE_URL:
    print(f"\n3️⃣ 测试自定义端点 (base_url={BASE_URL})...")
    try:
        llm_custom = ChatOpenAI(
            model_name="gpt-4o",
            max_tokens=100,
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "What color is this image? Answer in one word."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                }
            ]
        )
        
        response = llm_custom.invoke([message])
        print(f"   📨 回答: {response.content}")
        
        if 'blue' in response.content.lower():
            print("   ✅ 自定义端点工作正常")
        else:
            print("   ⚠️  可能未正确识别图片")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
else:
    print("\n3️⃣ 跳过自定义端点测试 (未设置OPENAI_BASE_URL)")

print("\n" + "=" * 60)
print("✅ 测试完成")
print("=" * 60)
print("\n💡 提示:")
print("- 如果使用自定义API端点，确保设置 OPENAI_BASE_URL 环境变量")
print("- 运行LayoutVLM时使用 --openai_base_url 参数")
