from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
import numpy as np

# MongoDB 연결
client = MongoClient(f"mongodb+srv://22100766:YZKIx8PDmEI6i3pe@cluster0.bhjnj.mongodb.net/Cluster0?retryWrites=true&w=majority&appName=Cluster0")
db = client["support_db"]
collection = db["queries"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def evaluate_similarity_with_semantic_search(question1: str, question2: str) -> float:
    embeddings1 = model.encode(question1, convert_to_tensor=True)
    embeddings2 = model.encode(question2, convert_to_tensor=True)
    cosine_similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
    return float(cosine_similarity)

def process_question_with_semantic_search(new_question: str, threshold: float = 0.7):
    similar_questions = []

    for record in collection.find({}, {"_id": 0, "query": 1, "response": 1}):
        existing_question = record.get("query")
        response_question = record.get("response")
        similarity = evaluate_similarity_with_semantic_search(new_question, existing_question)

        if similarity >= threshold:
            similar_questions.append({"query": existing_question, "similarity": similarity, "response": response_question})

    if similar_questions:
        print("유사한 질문들:")
        for q in sorted(similar_questions, key=lambda x: x["similarity"], reverse=True):
            print(f" - {q['query']} (유사도: {q['similarity']:.2f}) (답변: {q['response']})")
    else:
        print("유사한 질문이 없습니다.")

# 예제
if __name__ == "__main__":
    new_question = input("무엇이든지 물어보세요 : ")
    process_question_with_semantic_search(new_question)
