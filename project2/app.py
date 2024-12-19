#유사도 ChatGPT, LLM
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
import openai

# Flask 애플리케이션 초기화
app = Flask(__name__)

# MongoDB 연결
client = MongoClient(
    "mongodb+srv://22100766:YZKIx8PDmEI6i3pe@cluster0.bhjnj.mongodb.net/Cluster0?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["support_db"]
collection = db["queries"]

# Sentence Transformer 모델
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

openai.api_key = "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"  # OpenAI API 키 입력

# 유사도 계산 함수
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

#ChatGPT 답변 생성
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

# 유사 질문 검색 및 답변 처리
def process_question_with_semantic_search(new_question: str, threshold: float = 70.0):
    similar_questions = []

    for record in collection.find({}, {"_id": 0, "query": 1, "response": 1}):
        existing_question = record.get("query")
        response_question = record.get("response")
        similarity = evaluate_similarity_with_chatgpt(new_question, existing_question)

        if similarity >= threshold:
            similar_questions.append(
                {"query": existing_question, "similarity": similarity, "response": response_question}
            )

    if similar_questions:
        # 유사도가 가장 높은 질문의 답변 반환
        print("유사한 질문을 찾았습니다. ChatGPT를 통해 새로운 질문에 대한 답변을 생성합니다.")
        for q in similar_questions:
            print(f" - 유사 질문: {q['query']} (유사도: {q['similarity']:.2f}) (답변: {q['response']})")
        
        generated_answer = generate_answer_with_chatgpt(new_question, similar_questions)
        print(f"ChatGPT 생성 답변: {generated_answer}")
        return generated_answer
    else:
        return "죄송합니다. 유사한 질문에 대한 답변을 찾을 수 없습니다."

# Flask 라우트
@app.route("/")
def index():
    return render_template("index.html")  

@app.route("/ask", methods=["POST"])
def ask_question():
    user_question = request.form.get("question")  
    if not user_question:
        return jsonify({"answer": "질문이 입력되지 않았습니다. 다시 시도해 주세요."})
    
    # 질문 처리
    response = process_question_with_semantic_search(user_question)
    return jsonify({"answer": response})

# 실행
if __name__ == "__main__":
    app.run(debug=True)
