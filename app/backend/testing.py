import pandas as pd 
import requests
import json

url = "http://localhost:8000/process-text/"
headers = {"Content-Type": "application/json"}


# 1. Загрузка датасета
df = pd.read_parquet("dataset/ds.parquet")[["text", "is_contains_confidential"]].dropna()
cases_total = 100

right_answers = 0
for i in range(cases_total):
   data = {
    "text": df['text'][i],
    "user_id": "1234567"
   }
   response = requests.post(url, headers=headers, data=json.dumps(data))
   response_json = response.json()  # Преобразуем ответ в словарь
   is_confidential = response_json.get("message", {}).get("is_confidential", None)  # Достаем значение
   if (df['is_contains_confidential'][i] == int(not is_confidential)):
      right_answers += 1
      print('true, case#' + str(i))
   else:
      print('FALSE, case#' + str(i))
   
print(right_answers/cases_total)