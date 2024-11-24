# DBLP Title Fetcher with OpenAI Integration

## 项目介绍

该项目旨在从 DBLP 数据库中获取特定会议和年份的论文标题，并使用 OpenAI 的 GPT 模型对这些标题进行分析和翻译。通过并发调用 OpenAI 接口，用户可以快速获取与给定上下文相关的论文标题，并对结果进行统计分析。

## 功能

- 从 DBLP 获取论文标题
- 使用 OpenAI API 进行相关性查询
- 对选中的论文标题进行频次统计
- 将论文标题翻译成中文

## 安装

1. 克隆该项目：

   ```bash
   git clone https://github.com/yourusername/dblp-title-fetcher.git
   cd dblp-title-fetcher


2. 安装依赖：

pip install -r requirements.txt


3. API设置：
在你的操作系统中设置环境变量。具体方法取决于你的操作系统：

Linux/Mac:
export OPENAI_API_KEY="sk-XXX"
export OPENAI_BASE_URL="https://XXXX"


Windows:
set OPENAI_API_KEY="sk-XXX"
set OPENAI_BASE_URL"https://XXXX"


## 使用步骤

1. **运行程序**：
在命令行中运行 Python 脚本：
python your_script_name.py

2. **输入会议名称和年份**：
输入会议名称和年份：
当程序提示时，输入你感兴趣的会议名称和年份。例如：

请输入会议名称: ICML
请输入年份: 2023

3. **输入上下文**：
程序将输出获取到的论文标题。接下来，输入你期望的上下文。例如：

请输入你期望的上下文: 深度学习在图像识别中的应用

4. **查看结果**：
程序将调用 OpenAI 接口并统计结果，最终输出被选中的论文标题及其翻译......

