import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def get_secret(key, json_path: str = str(BASE_DIR / "secrets.json")):
    with open(json_path) as file:
        secrets = json.loads(file.read())
        try:
            return secrets[key]
        except:
            raise EnvironmentError(f"There is not {key} in file")


###### SECRET ######
KAKAO_API_KEY = get_secret("KEY")
DB_OPTION = {
    "url": get_secret("DB_URL"),
    "user": get_secret("DB_USER"),
    "pw": get_secret("DB_PW"),
    "database": get_secret("DB_DATABASE"),
}
AUTH_OPTION = {
    "algotithm": get_secret("AUTH_ALGORITHM"),
    "key": get_secret("AUTH_KEY"),
    "exp": get_secret("AUTH_EXP"),
}

###### CONFIG ######

# 카카오 책 검색 API 설정
# Key       :   API 키
# sort      :   결과 문서 정렬 방식, accuracy(정확도순) 또는 latest(발간일순), 기본값 accuracy
# page      :   결과 페이지 번호, 1~50 사이의 값, 기본 값 2
# size      :   한 페이지에 보여질 문서 수, 1~50 사이의 값, 기본 값 10
# target    :	검색 필드 제한 title(제목), isbn (ISBN), publisher(출판사), person(인명)
KAKAO_API_OPTION = {
    "url": "https://dapi.kakao.com/v3/search/book",
    "sort": "accuracy",
    "page": 2,
    "size": 10,
}
