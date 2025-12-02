import os
from dotenv import load_dotenv

load_dotenv()  # .env 불러오기

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("OPENAI_API_KEY가 잘 불려왔습니다.")
    print("키 길이:", len(api_key))
else:
    print("OPENAI_API_KEY를 찾지 못했습니다. .env 파일을 확인하세요.")
