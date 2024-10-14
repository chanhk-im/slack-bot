import slack_sdk

slack_token = 'xoxb-7877243331284-7872036202357-c3Tv1PhOcReRblhQWcEeA70G'

client = slack_sdk.WebClient(token=slack_token)

user_id = "U07RMS0PKCM"
slack_msg = f'<@{user_id}> 파이썬 슬랙 메시지 전송' 

response = client.chat_postMessage(
    channel="C07RAABJCKZ",
    text=slack_msg
)