import requests
import json
import random
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import openai
import os

# 配置 OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.base_url = os.getenv("OPENAI_BASE_URL")
openai.default_headers = {"x-foo": "true"}

def fetch_dblp_titles(conference, year):
    query = f"{conference} {year}"
    url = f"https://dblp.org/search/publ/api?q={query}&format=json&h=400"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        filename = f"./origin/{query}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        filtered_titles = []
        for hit in hits:
            info = hit.get("info", {})
            title = info.get("title", "No Title")
            venue = info.get("venue", "")
            publication_year = info.get("year", "")
            
            if str(year) == str(publication_year) and conference.lower() in venue.lower():
                filtered_titles.append(title)
        filename = f"./title/{query}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(filtered_titles, file, ensure_ascii=False, indent=4)
        return filtered_titles
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except json.JSONDecodeError:
        print("解析 JSON 数据失败")
        return []


def query_openai(titles, context):
    indexed_titles = list(enumerate(titles, 1))  # (序号, 标题)
    shuffled_titles = random.sample(indexed_titles, len(indexed_titles))
    
    prompt = f"以下是一些文章标题，请根据上下文选择你认为相关的文章序号，每个一行：\n\n上下文：{context}\n\n文章标题：\n"
    for index, title in shuffled_titles:
        prompt += f"{index}. {title}\n"
    prompt += "\n相关的文章序号："

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        content = completion.choices[0].message.content
        selected_indices = []
        for line in content.splitlines():
            line = line.strip()
            if line.isdigit():
                selected_indices.append(int(line))
        return selected_indices
    except Exception as e:
        print(f"请求 OpenAI 接口失败: {e}")
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


def translate_title(title):
    completion =  openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"请将以下学术论文标题翻译成中文，并确保翻译准确：{title}"}
        ]
    )
    return completion.choices[0].message.content


def analyze_results(results, titles):
    count = Counter(results)
    sorted_results = sorted(count.items(), key=lambda x: x[1], reverse=True)
    print("\n文章被选中的频次统计：")
    for index, freq in sorted_results:
        title = titles[index - 1]
        translated_title = translate_title(title)
        print(f"{freq} {title} \n(翻译：{translated_title})")


if __name__ == "__main__":
    conference = input("请输入会议名称: ")
    year = input("请输入年份: ")
    titles = fetch_dblp_titles(conference, year)
    
    if not titles:
        print("未找到相关的文章标题。")
    else:
        print("\n获取到文章")
        context = input("请输入你期望的上下文")

        # 并发查询
        print("\n正在调用 OpenAI 接口并统计结果，请稍候...")
        results = concurrent_query(titles, context, num_iterations=10, max_workers=5)

        # 分析结果
        analyze_results(results, titles)