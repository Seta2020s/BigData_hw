import csv
from pathlib import Path
from functools import reduce
import time


def mapper(chunk):
    scores = []
    for row in chunk:
        rating_str = row.get("Rating", "")
        try:
            score = float(rating_str)
            scores.append(score)
        except ValueError:
            print(f"Ошибка преобразования значения в число: {rating_str}")
            continue

    n = len(scores)
    mean = sum(scores) / n if n > 0 else 0
    M2 = sum((x - mean) ** 2 for x in scores)
    return n, mean, M2


def reducer(score_data1, score_data2):
    n1, mean1, M2_1 = score_data1
    n2, mean2, M2_2 = score_data2

    n = n1 + n2
    if n == 0:
        return 0, 0.0, 0.0

    delta = mean2 - mean1
    mean = (n1 * mean1 + n2 * mean2) / n
    M2 = M2_1 + M2_2 + delta ** 2 * n1 * n2 / n

    return n, mean, M2


initial = (0, 0.0, 0.0)
file_path = Path("IMDB.csv")
if not file_path.exists():
    raise FileNotFoundError(f"Файл {file_path} не найден")

chunk_size = 1000

start_time = time.time()

with open(file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    chunk = []
    for i, row in enumerate(reader):
        chunk.append(row)
        if i > 0 and i % chunk_size == 0:
            scores = mapper(chunk)
            initial = reducer(initial, scores)
            chunk = []

    if chunk:
        scores = mapper(chunk)
        initial = reducer(initial, scores)

n, mean, M2 = initial
variance = M2 / n if n > 0 else 0
std_dev = variance ** 0.5

end_time = time.time()
execution_time = end_time - start_time

print(f"Среднее: {mean}, Стандартное отклонение: {std_dev}")
print(f"Время выполнения: {execution_time} секунд")
