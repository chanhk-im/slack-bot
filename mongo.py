from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np

# MongoDB Atlas 클러스터 연결
import os
client = MongoClient(f"mongodb+srv://22100766:YZKIx8PDmEI6i3pe@cluster0.bhjnj.mongodb.net/Cluster0?retryWrites=true&w=majority&appName=Cluster0")

db = client["support_db"]
collection = db["queries"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def add_query_to_db(query, response):
    
    query_vector = model.encode(query).tolist()
    collection.insert_one({"query": query, "response": response, "query_vector": query_vector})

add_query_to_db("서버 다운 문제", "서버를 재시작해 주세요.")
add_query_to_db("로그인 오류", "쿠키와 캐시를 삭제한 후 다시 시도해 보세요.")

def search_exact_query(user_query):
    
    result = collection.find_one({"query": user_query})
    if result:
        return result["response"]
    else:
        return "죄송합니다. 관련 답변을 찾을 수 없습니다."

#Example
user_query = "서버 다운 문제"
response = search_exact_query(user_query)
print(response)
