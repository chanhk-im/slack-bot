#Vector Search를 사용해서 DB안에 있는 질문들과 새로운 질문의 유사도 파악
#유사도가 높은 질문들과 답변을 함께 ChatGPT API에게 다시 질문하고 답변을 받아냄

from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
import openai

# MongoDB 연결
client = MongoClient("mongodb+srv://22100766:YZKIx8PDmEI6i3pe@cluster0.bhjnj.mongodb.net/Cluster0?retryWrites=true&w=majority&appName=Cluster0")
db = client["support_db"]
collection = db["queries"]

# Sentence Transformer 모델
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# OpenAI API 키 설정
openai.api_key = "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"  # OpenAI API 키 입력

def evaluate_similarity_with_semantic_search(question1: str, question2: str) -> float:
    embeddings1 = model.encode(question1, convert_to_tensor=True)
    embeddings2 = model.encode(question2, convert_to_tensor=True)
    cosine_similarity = util.pytorch_cos_sim(embeddings1, embeddings2)
    return float(cosine_similarity)

def generate_answer_with_chatgpt(question: str, similar_questions: list) -> str:
    try:
        prompt = "다음은 유사한 질문과 그 답변들입니다:\n\n"
        for i, item in enumerate(similar_questions):
            prompt += f"{i+1}. 유사 질문: {item['query']}\n   답변: {item['response']}\n\n"
        prompt += f"이를 참고하여 아래 새로운 질문에 답변해 주세요:\n새로운 질문: {question}\n"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"ChatGPT API 호출 중 오류 발생: {str(e)}"

def process_question_with_semantic_search(new_question: str, threshold: float = 0.7):
    similar_questions = []

    for record in collection.find({}, {"_id": 0, "query": 1, "response": 1}):
        existing_question = record.get("query")
        response_question = record.get("response")
        similarity = evaluate_similarity_with_semantic_search(new_question, existing_question)

        if similarity >= threshold:
            similar_questions.append(
                {"query": existing_question, "similarity": similarity, "response": response_question}
            )

    if similar_questions:
        print("유사한 질문을 찾았습니다. ChatGPT를 통해 새로운 질문에 대한 답변을 생성합니다.")
        for q in similar_questions:
            print(f" - 유사 질문: {q['query']} (유사도: {q['similarity']:.2f}) (답변: {q['response']})")
        
        generated_answer = generate_answer_with_chatgpt(new_question, similar_questions)
        print(f"ChatGPT 생성 답변: {generated_answer}")
        return generated_answer
    else:
        print("유사한 질문이 없습니다. ChatGPT를 통해 직접 답변을 생성합니다.")

# 실행
if __name__ == "__main__":
    new_question = input("무엇이든지 물어보세요 : ")
    response = process_question_with_semantic_search(new_question)
    print(f"최종 답변: {response}")
