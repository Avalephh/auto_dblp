import requests
import json
import random
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import openai
import os

# 配置 OpenAI API
# openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.base_url = os.getenv("OPENAI_BASE_URL")
openai.api_key = "sk-FCG2SnikRxW6O6XoBf791390C2Ac4aEf86B471984dB8BdFa"

openai.base_url = "https://api.gpt.ge/v1/"

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
            if isinstance(venue, list):
                venue = ", ".join(venue)  
            else:
                venue = str(venue) 
            publication_year = info.get("year", "")
            
            if str(year) == str(publication_year) : #todo and conference.lower() in venue.lower():
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


def analyze_results(results, titles, translate=False, filename="default.txt"):
    
    count = Counter(results)
    sorted_results = sorted(count.items(), key=lambda x: x[1], reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        print("\n文章被选中的频次统计(从高到低)：")
        f.write("文章被选中的频次统计(从高到低)：\n")
        for index, freq in sorted_results:
            try:
                title = titles[index - 1]
                if translate:
                    translated_title = translate_title(title)
                    output_line = f"热力值为：{freq} , {title} \n(翻译：{translated_title})"
                else:
                    output_line = f"热力值为：{freq} , {title}"
                
                print(output_line)
                f.write(output_line + '\n')
            except:
                output_line = f"热力值为：{freq} , {title}"
                print(output_line)
                f.write(output_line + '\n')
                print("获取翻译错误")


if __name__ == "__main__":
    conference = input("请输入会议或期刊名称: ")
    year = input("请输入年份: ")
    titles = fetch_dblp_titles(conference, year)
    
    if not titles:
        print("未找到相关的文章标题。")
    else:
        print("\n获取到文章")
        context = """
        随着云计算技术的快速发展和数据处理需求的日益复杂化，传统的单体数据库系统架构在面对现代应用场景时显现出诸多局限性。
        数据库系统服务化（Database Componentization）作为一种新型架构范式，正在重新定义数据管理系统的设计和实现方式。
        传统的一体化数据库设计难以适应这种复杂多变的环境。数据库系统服务化通过将系统解耦为独立的服务组件，
        不仅提供了更高的灵活性和可扩展性，还能更好地适应云环境下的资源调度和管理需求。这种转变使得数据库系统能够更好地满足现代应用的需求，同时降低开发和维护成本。
        服务化解耦已成为解决上述挑战的关键途径。通过组件化管理，将数据库核心功能（如查询处理、优化器、存储引擎等）解耦为独立服务，
        实现了组件的独立演进和优化，同时便于功能复用和标准化。
        我需要设计一个数据库内存服务(Cache Service)的解耦合方案。
        """

        # 并发查询
        print("\n正在调用 OpenAI 接口并统计结果，请稍候...")
        results = concurrent_query(titles, context, num_iterations=10, max_workers=5)

        user_input = input("是否需要翻译标题？(y/n): ").strip().lower()

        # 根据用户输入设置翻译参数
        translate = user_input == 'y'

        # 分析结果
        filename = f"./ans/{conference}{year}.json"
        analyze_results(results, titles, translate, filename)