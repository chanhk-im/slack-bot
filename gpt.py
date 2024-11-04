import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "안녕하세요! 오늘 날씨는 어떤가요?"}]
)
print(response.choices[0].message["content"])
