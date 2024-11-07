import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_request(number):
    # 随机延迟 0.1 到 1 秒
    time.sleep(random.uniform(1, 10))
    url = f"http://127.0.0.1:8000/item/C{number}"
    try:
        response = requests.get(url)
        if response.status_code == 500:
            return url
    except requests.exceptions.RequestException as e:
        # 可以根据需要打印异常信息
        pass
    return None

def main():
    error_urls = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, number) for number in range(1000, 10001)]
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result)


if __name__ == "__main__":
    main()
