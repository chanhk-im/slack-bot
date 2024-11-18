import openai
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np

# OpenAI API 키 설정
openai.api_key = "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"

# MongoDB 연결
client = MongoClient(f"mongodb+srv://22100766:YZKIx8PDmEI6i3pe@cluster0.bhjnj.mongodb.net/Cluster0?retryWrites=true&w=majority&appName=Cluster0")

db = client["support_db"]
collection = db["queries"]

#model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ChatGPT를 사용해 질문 유사도를 평가
def evaluate_similarity_with_chatgpt(question1: str, question2: str) -> float:
    prompt = f"""
    다음 두 질문을 비교하여 얼마나 유사한지 판단해 주세요. 
    유사도를 0에서 100 사이의 점수로 표현하세요:
    
    질문 1: "{question1}"
    질문 2: "{question2}"
    
    답변은 float형 숫자로만 반환해주세요. 문장 형태가 아닌 숫자 단답으로만 대답하세요.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 또는 "gpt-3.5-turbo"
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    similarity_score = response["choices"][0]["message"]["content"].strip()
    return float(similarity_score)

# 새로운 질문을 처리하고 유사한 질문을 검색
def process_question_with_chatgpt(new_question: str, threshold: float = 70.0):
    similar_questions = []

    # DB에서 모든 질문 가져오기 및 유사도 계산
    for record in collection.find({}, {"_id": 0, "query": 1, "response" : 1}):
        #existing_question = record["query"]
        existing_question = record.get("query") 
        response_question = record.get("response")
        similarity = evaluate_similarity_with_chatgpt(new_question, existing_question)
        if similarity >= threshold:
            similar_questions.append({"query": existing_question, "similarity": similarity, "response": response_question})

    # 유사 질문 출력
    if similar_questions:
        print("유사한 질문들:")
        for q in sorted(similar_questions, key=lambda x: x["similarity"], reverse=True):
            print(f" - {q['query']} (유사도: {q['similarity']:.2f}) (답변: {q['response']})")
    else:
        print("유사한 질문이 없습니다.")

    # 새로운 질문 저장
    if not collection.find_one({"query": new_question}):
        collection.insert_one({"query": new_question})
        print("새로운 질문이 저장되었습니다.")
    else:
        print("질문이 이미 존재합니다.")

# 실행 예제
if __name__ == "__main__":
    new_question = "서버 다운 문제"
    process_question_with_chatgpt(new_question)
