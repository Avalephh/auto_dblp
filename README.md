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

