# 🔧 Colab运行LayoutVLM修复指南

## 问题诊断

你遇到的错误是因为**LangChain没有使用你的自定义API端点**（BASE_URL），导致图像无法正确传递给GPT-4o。

## ✅ 已完成的修复

### 1. 修改 `layoutvlm.py`
- 添加 `openai_api_key` 和 `openai_base_url` 参数
- 确保所有LLM实例都使用正确的配置

### 2. 修改 `main.py`
- 添加 `--openai_base_url` 命令行参数
- 将配置传递给 `LayoutVLM` 类

### 3. 改进错误处理
- 检测LLM返回自然语言而非代码的情况
- 提供清晰的错误信息帮助调试

## 🚀 在Colab中使用修复后的代码

### 方法1: 直接修改Colab中的代码

在Colab notebook中，修改运行命令：

```python
# 设置你的API配置
API_KEY = "your-api-key"
BASE_URL = "your-base-url"  # 例如: "https://api.example.com/v1"

# 运行LayoutVLM，添加 --openai_base_url 参数
!python main.py \
  --scene_json_file /path/to/scene.json \
  --save_dir /content/results \
  --openai_api_key {API_KEY} \
  --openai_base_url {BASE_URL} \
  --asset_dir /path/to/assets
```

### 方法2: 使用环境变量

```python
import os

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_BASE_URL"] = "your-base-url"

# 如果你的代码读取这些环境变量，也可以这样运行
!python main.py \
  --scene_json_file /path/to/scene.json \
  --save_dir /content/results \
  --openai_api_key $OPENAI_API_KEY \
  --openai_base_url $OPENAI_BASE_URL
```

### 方法3: 修改临时运行脚本

如果你使用的是临时脚本（如 `/tmp/run_layoutvlm.py`），确保它包含：

```python
from src.layoutvlm.layoutvlm import LayoutVLM

# 创建LayoutVLM实例时传递参数
layout_solver = LayoutVLM(
    mode="one_shot",
    save_dir=save_dir,
    asset_source="objaverse",
    openai_api_key="your-api-key",
    openai_base_url="your-base-url"  # ← 关键！
)
```

## 🧪 测试修复

### 1. 测试Vision功能

在Colab中运行测试脚本：

```python
# 上传修改后的代码到Colab
!cd /content/LayoutVLM && git pull  # 或重新上传文件

# 运行测试
!cd /content/LayoutVLM && python test_vision_integration.py
```

预期输出：
```
✅ 自定义端点工作正常
📨 回答: Blue
```

### 2. 检查LLM输出文件

运行LayoutVLM后，检查生成的程序：

```python
# 查看LLM实际返回的内容
!cat /content/drive/MyDrive/LayoutVLM_Project/results/group_0/llm_output_program_0.py
```

如果修复成功，你应该看到Python代码而不是自然语言。

## 📋 完整的Colab运行示例

```python
# ========== 1. 克隆/更新代码 ==========
!git clone https://github.com/HUMBLEDDDD/LayoutVLM.git /content/LayoutVLM
!cd /content/LayoutVLM && git checkout colab-compatibility

# ========== 2. 安装依赖 ==========
!pip install -r /content/LayoutVLM/requirements.txt

# ========== 3. 配置API ==========
API_KEY = "sk-xxx"  # 你的API密钥
BASE_URL = "https://your-api-endpoint.com/v1"  # 你的API端点

import os
os.environ["OPENAI_API_KEY"] = API_KEY

# ========== 4. 准备场景数据 ==========
scene_json = "/content/scene.json"
asset_dir = "/content/objaverse_processed"
save_dir = "/content/drive/MyDrive/LayoutVLM_Project/results"

# ========== 5. 运行LayoutVLM（修复版）==========
!python /content/LayoutVLM/main.py \
  --scene_json_file {scene_json} \
  --save_dir {save_dir} \
  --openai_api_key {API_KEY} \
  --openai_base_url {BASE_URL} \
  --asset_dir {asset_dir}
```

## 🔍 故障排查

### 如果仍然看到"I can't access images"

1. **验证BASE_URL格式**：
   ```python
   # 正确格式示例
   BASE_URL = "https://api.example.com/v1"  # ✅
   
   # 错误格式
   BASE_URL = "https://api.example.com"     # ❌ 缺少 /v1
   BASE_URL = "api.example.com/v1"          # ❌ 缺少 https://
   ```

2. **检查图像大小**：
   ```python
   import os
   img_path = f"{save_dir}/group_0/top_down_rendering.png"
   if os.path.exists(img_path):
       size_mb = os.path.getsize(img_path) / 1024 / 1024
       print(f"图像大小: {size_mb:.2f} MB")
       if size_mb > 20:
           print("⚠️  图像太大，可能导致上传失败")
   ```

3. **检查LangChain版本**：
   ```python
   import langchain_openai
   print(f"LangChain OpenAI版本: {langchain_openai.__version__}")
   # 建议版本: >= 0.0.2
   ```

4. **启用调试日志**：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # 然后运行LayoutVLM，查看详细的API调用日志
   ```

## 📝 更新后的文件清单

- ✅ `src/layoutvlm/layoutvlm.py` - 添加API配置参数
- ✅ `src/layoutvlm/sandbox.py` - 改进错误处理
- ✅ `main.py` - 添加命令行参数
- ✅ `test_vision_integration.py` - Vision功能测试脚本

## 🎯 下一步

1. 将修改后的文件同步到Colab
2. 使用 `--openai_base_url` 参数运行
3. 检查LLM输出文件确认修复成功

如果问题仍然存在，请提供：
- LLM输出文件内容（`llm_output_program_0.py`）
- 使用的完整命令
- 任何新的错误信息
