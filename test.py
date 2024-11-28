import slack_sdk
import requests
import threading
import time

slack_token = 'xoxb-7877243331284-7872036202357-FujHTyeMyLCGSn3tjokyUUEz'
flask_url = "http://localhost:5000"

channel_id = "C07RAABJCKZ"

client = slack_sdk.WebClient(token=slack_token)

user_id = "U07RMS0PKCM"
admins = [user_id]
customers = [user_id]

# slack_msg = f'<@{user_id}> 파이썬 슬랙 메시지 전송' 

# response = client.chat_postMessage(
#     channel=channel_id,
#     text=slack_msg
# )

# Slack에서 쿼리를 받았다면, Flask API로 HTTP 요청을 보내 쿼리 결과를 받음
def send_query_to_flask(query: str):
    # Flask API의 엔드포인트로 쿼리를 보내기 위한 URL
    flask_url_query = f"{flask_url}/search_query"
    
    # Flask API에 GET 요청을 보내어 쿼리 결과를 받음
    params = {"query": query}
    flask_response = requests.get(flask_url_query, params=params)
    
    if flask_response.status_code == 200:
        return flask_response.json().get("response", "응답을 받을 수 없습니다.")
    else:
        return f"{flask_response.status_code}: 서버에서 문제가 발생했습니다."


def update_chat(oldest_time: str | None):
    while True:
        response = client.conversations_history(
            channel=channel_id,
            oldest=oldest_time
        )

        messages = response["messages"]
        for msg in messages:
            if msg["user"] in customers:
                reply_response = client.conversations_replies(
                    channel=channel_id,
                    ts=msg["ts"],
                )
                admin_replies = []
                is_first = True
                for reply in reply_response["messages"]:
                    print(reply["text"])
                    if reply["user"] in admins and not is_first:
                        admin_replies.append(reply["text"])
                    is_first = False

                if len(admin_replies) >= 1:
                    req_query = {
                        "query": reply_response["messages"][0]["text"],
                        "response": admin_replies[0],
                    }

                    print(req_query)
                    flask_response = requests.post(f"{flask_url}/add_query", json=req_query)
                    print(f"{flask_response.status_code}: add query 완료")

        break


def thread_send_query():
    while True:
        query = input()
        if query == "Quit":
            return
        
        query_response = send_query_to_flask(query)

        # 쿼리 응답을 Slack 채널에 보내기
        slack_msg = f'<@{user_id}> 쿼리에 대한 응답: {query_response}'
        response = client.chat_postMessage(
            channel=channel_id,
            text=slack_msg
        )

thread = threading.Thread(target=thread_send_query)


flask_response = requests.post(f"{flask_url}/add_query", json={
    'query': '서버 다운 문제',
    'response': '서버를 재시작해 주세요.'
})
print(f"{flask_response.status_code}: add query 완료")

# 예시로 Slack 봇에서 쿼리 받기 (예: "서버 다운 문제")
user_query = "서버 다운 문제"
query_response = send_query_to_flask(user_query)

# 쿼리 응답을 Slack 채널에 보내기
slack_msg = f'<@{user_id}> 쿼리에 대한 응답: {query_response}'

response = client.chat_postMessage(
    channel=channel_id,
    text=slack_msg
)

update_chat(None)
thread.start()
thread.join()