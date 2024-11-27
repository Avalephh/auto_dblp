from concurrent.futures import ThreadPoolExecutor
import streamlit as st
import requests
import json
import random
from collections import Counter
import openai
# 从 main 文件中导入翻译函数
from api import translate_title

# 配置 OpenAI API
openai.api_key = "sk-FCG2SnikRxW6O6XoBf791390C2Ac4aEf86B471984dB8BdFa"
openai.base_url = "https://api.gpt.ge/v1/"
openai.default_headers = {"x-foo": "true"}

# 获取 DBLP 标题的函数
def fetch_dblp_titles(conference, year):
    query = f"{conference} {year}"
    url = f"https://dblp.org/search/publ/api?q={query}&format=json&h=400"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        filtered_titles = [
            hit.get("info", {}).get("title", "No Title")
            for hit in hits
            if str(year) == hit.get("info", {}).get("year", "")
        ]
        return filtered_titles
    except Exception as e:
        st.error(f"请求失败: {e}")
        return []


# 调用 OpenAI 接口分析相关性
def query_openai(titles, context):
    indexed_titles = list(enumerate(titles, 1))
    shuffled_titles = random.sample(indexed_titles, len(indexed_titles))

    prompt = f"以下是一些文章标题，请根据上下文选择你认为相关的文章序号，每个一行：\n\n上下文：{context}\n\n文章标题：\n"
    for index, title in shuffled_titles:
        prompt += f"{index}. {title}\n"
    prompt += "\n相关的文章序号："

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        content = completion.choices[0].message.content
        selected_indices = [
            int(line.strip())
            for line in content.splitlines()
            if line.strip().isdigit()
        ]
        return selected_indices
    except Exception as e:
        st.error(f"请求 OpenAI 接口失败: {e}")
        return []


def concurrent_query(titles, context, num_iterations=10, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _ in range(num_iterations):
            futures.append(executor.submit(query_openai, titles, context))

        for future in futures:
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"并发调用失败: {e}")
    return results

# 分析结果的函数
def analyze_results(results, titles):
    count = Counter(results)
    sorted_results = sorted(count.items(), key=lambda x: x[1], reverse=True)
    analysis = [
        (freq, titles[index - 1]) for index, freq in sorted_results if index - 1 < len(titles)
    ]
    return analysis


# Streamlit 界面逻辑
st.title("学术文章推荐助手")
search_output = "感谢使用学术文章推荐助手\n"
analyse_output = "感谢使用学术文章推荐助手\n"

# 初始化 session_state 以保存标题和分析结果
if "titles" not in st.session_state:
    st.session_state.titles = []
if "analysis" not in st.session_state:
    st.session_state.analysis = []

# 输入设置
st.sidebar.header("设置")
conference = st.sidebar.text_input("会议或期刊名称")
year = st.sidebar.text_input("年份")

# 获取文章标题
if st.sidebar.button("获取文章标题"):
    if not conference or not year:
        st.error("请输入会议或期刊名称和年份")
    else:
        with st.spinner("正在获取文章标题..."):
            st.session_state.titles = fetch_dblp_titles(conference, year)
            search_output += "\n".join(st.session_state.titles)
        if st.session_state.titles:
            st.success(f"成功获取 {len(st.session_state.titles)} 篇文章标题！")
        else:
            st.warning("未找到相关的文章标题，请检查输入信息。")

st.sidebar.download_button(
        label="下载原始搜索文件",
        data=search_output,
        file_name=f"{conference}_{year}_origin.txt",
        mime="text/plain"
    )

if st.session_state.titles:
    # 使用列表生成式将标题格式化为带序号的字符串
    formatted_titles = "\n".join([f"{i}. {title}" for i, title in enumerate(st.session_state.titles, 1)])
    # 将格式化后的内容放入 text_area 的 value 参数
    st.text_area("获取到的文章标题：", value=formatted_titles, height=200, disabled=True)

# 上下文输入和查询相关性
context = st.text_area("请输入上下文描述")
analyse_output += "您输入的上下文是：\n"
analyse_output += context
analyse_output += "\n"

if st.button("查询相关性"):
    if not context.strip():
        st.error("请输入上下文描述")
    elif not st.session_state.titles:
        st.error("请先获取文章标题")
    else:
        with st.spinner("正在调用 OpenAI 接口分析相关性..."):
            results = concurrent_query(st.session_state.titles, context)
        if results:
            st.session_state.analysis = analyze_results(results, st.session_state.titles)
            st.success("成功完成查询！")
        else:
            st.warning("未能获取相关结果，请稍后再试。")

# 显示分析结果
if st.session_state.analysis:
    # 使用列表生成式将分析结果格式化为带序号的字符串
    formatted_analysis = "\n".join(
        [f"{i}. 热力值：{freq}, 标题：{title}" for i, (freq, title) in enumerate(st.session_state.analysis, 1)]
    )
    analyse_output += formatted_analysis
    # 使用 text_area 显示推荐结果
    st.text_area("推荐结果：", value=formatted_analysis, height=400, disabled=True)

# 翻译标题
if st.checkbox("翻译标题"):
    if st.session_state.analysis:
        if st.button("翻译"):
            with st.spinner("正在翻译标题..."):
                translations = [
                    (title, translate_title(title))
                    for _, title in st.session_state.analysis
                ]
            if translations:
                # 使用列表生成式将翻译结果格式化为带序号的字符串
                formatted_translations = "\n".join(
                    [f"{i}. {original} ==> {translation}" for i, (original, translation) in enumerate(translations, 1)]
                )
                analyse_output += formatted_translations
                # 使用 text_area 显示翻译结果
                st.text_area("翻译结果：", value=formatted_translations, height=400, disabled=True)
    else:
        st.warning("请先进行相关性查询以获得分析结果。")

st.sidebar.download_button(
        label="下载分析结果文件",
        data=analyse_output,
        file_name=f"{conference}_{year}_ai.txt",
        mime="text/plain"
    )