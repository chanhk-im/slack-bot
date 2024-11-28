from flask import Flask, request, jsonify
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
import certifi

app = Flask(__name__)

# MongoDB Atlas 클러스터 연결
import os

username = "Cluster61605"
password = "1234"
clusterName = "cluster61605"

connectionString = "mongodb+srv://{}:{}@{}.njaly.mongodb.net/?retryWrites=true&w=majority&appName={}".format(username, password, clusterName, username)

client = MongoClient(connectionString)

db = client["slack_bot_db"]
collection = db["queries"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@app.route('/add_query', methods=['POST'])
def add_query_to_db():
    data = request.get_json()
    query = data.get("query")
    response = data.get("response")

    if not query or not response:
        return jsonify({"error": "query와 response를 모두 제공해야 합니다."}), 400
    
    result = collection.find_one({"query": query})
    if result:
        return jsonify({"error": "이미 존재하는 쿼리입니다."}), 400
    
    query_vector = model.encode(query).tolist()
    collection.insert_one({"query": query, "response": response, "query_vector": query_vector})

    return jsonify({"message": "데이터가 성공적으로 추가되었습니다."}), 201

# add_query_to_db("서버 다운 문제", "서버를 재시작해 주세요.")
# add_query_to_db("로그인 오류", "쿠키와 캐시를 삭제한 후 다시 시도해 보세요.")

@app.route('/search_query', methods=['GET'])
def search_exact_query():
    user_query = request.args.get("query")
    
    if not user_query:
        return jsonify({"error": "쿼리를 제공해야 합니다."}), 400
    
    result = collection.find_one({"query": user_query})
    if result:
        return jsonify({"response": result["response"]})
    else:
        return jsonify({"message": "관련 답변을 찾을 수 없습니다."}), 404

#Example
# user_query = "서버 다운 문제"
# response = search_exact_query(user_query)
# print(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
