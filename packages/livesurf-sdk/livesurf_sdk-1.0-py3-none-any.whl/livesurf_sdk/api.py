"""
LiveSurf API Python SDK
=======================
Клиент для работы с API https://api.livesurf.ru/

Возможности:
 - Авторизация по API ключу
 - Поддержка всех HTTP методов (GET, POST, PATCH, DELETE)
 - Контроль лимита скорости (10 запросов/сек)
 - Повтор при ошибках 429/5xx с экспоненциальной задержкой
 - Удобные методы и понятные исключения

Пример использования: см. examples/example.py
Автор: DecPro
Версия: 1.0.0
"""

import time
import random
import json
from typing import Any, Dict, Optional
import requests


class LiveSurfApi:
    """
    Клиент LiveSurf API.

    :param api_key: API-ключ для заголовка Authorization
    :param options: Дополнительные параметры:
        - base_url (str): базовый URL (по умолчанию https://api.livesurf.ru/)
        - timeout (int): таймаут запроса в секундах (по умолчанию 15)
        - rate_limit (int): лимит запросов в секунду (по умолчанию 10)
        - max_retries (int): количество повторов при ошибках (по умолчанию 3)
        - initial_backoff_ms (int): начальная задержка для backoff в миллисекундах (по умолчанию 500)
    """

    def __init__(self, api_key: str, **options):
        self.api_key = api_key
        self.base_url = options.get("base_url", "https://api.livesurf.ru/").rstrip("/") + "/"
        self.timeout = options.get("timeout", 15)
        self.rate_limit = options.get("rate_limit", 10)
        self.max_retries = options.get("max_retries", 3)
        self.initial_backoff_ms = options.get("initial_backoff_ms", 500)
        self._timestamps = []  # для контроля лимита запросов

    # ---- Внутренние методы ----
    def _apply_rate_limit(self) -> None:
        """Контроль лимита запросов (N в секунду)."""
        now = time.time()
        self._timestamps = [t for t in self._timestamps if t > now - 1]
        if len(self._timestamps) >= self.rate_limit:
            earliest = min(self._timestamps)
            sleep_time = 1 - (now - earliest)
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._timestamps.append(time.time())

    def _sleep_for_retry(self, attempt: int) -> None:
        """Экспоненциальная задержка с джиттером перед повтором."""
        base = self.initial_backoff_ms * (2 ** (attempt - 1))
        jitter = int(base * 0.2)
        delay_ms = base + random.randint(-jitter, jitter)
        time.sleep(delay_ms / 1000.0)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Универсальный метод HTTP-запроса с повторной попыткой при ошибках."""
        url = self.base_url + endpoint.lstrip("/")
        headers = {
            "Accept": "application/json",
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        attempt = 0
        while True:
            attempt += 1
            self._apply_rate_limit()

            try:
                resp = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    timeout=self.timeout,
                    data=json.dumps(data, ensure_ascii=False) if data is not None else None
                )
            except requests.RequestException as exc:
                if attempt <= self.max_retries:
                    self._sleep_for_retry(attempt)
                    continue
                raise ConnectionError(f"Ошибка соединения: {exc}") from exc

            # Попытка распарсить JSON, иначе оставить текст
            try:
                parsed = resp.json()
            except ValueError:
                parsed = resp.text

            # Успешный ответ
            if 200 <= resp.status_code < 300:
                return parsed

            # Повторяем при 429 или 5xx
            if (resp.status_code == 429 or (500 <= resp.status_code < 600)) and attempt <= self.max_retries:
                self._sleep_for_retry(attempt)
                continue

            # Иначе выбрасываем исключение с сообщением от API (если есть)
            msg = parsed.get("error") if isinstance(parsed, dict) and "error" in parsed else parsed
            raise Exception(f"Ошибка API ({resp.status_code}): {msg}")

    # ---- Универсальные методы ----
    def get(self, endpoint: str) -> Any:
        return self._request("GET", endpoint)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self._request("POST", endpoint, data)

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return self._request("PATCH", endpoint, data)

    def delete(self, endpoint: str) -> Any:
        return self._request("DELETE", endpoint)

    # ---- Методы API (те же, что в PHP и Node версии) ----

    # Общие
    def get_categories(self) -> Any:
        return self.get("categories/")

    def get_countries(self) -> Any:
        return self.get("countries/")

    def get_languages(self) -> Any:
        return self.get("languages/")

    # Источники
    def get_sources_ad(self) -> Any:
        return self.get("sources/ad/")

    def get_sources_messengers(self) -> Any:
        return self.get("sources/messengers/")

    def get_sources_search(self) -> Any:
        return self.get("sources/search/")

    def get_sources_social(self) -> Any:
        return self.get("sources/social/")

    # Пользователь
    def get_user(self) -> Any:
        return self.get("user/")

    def set_auto_mode(self) -> Any:
        return self.post("user/automode/")

    def set_manual_mode(self) -> Any:
        return self.post("user/manualmode/")

    # Группы
    def get_groups(self) -> Any:
        return self.get("group/all/")

    def get_group(self, id: int) -> Any:
        return self.get(f"group/{id}/")

    def create_group(self, data: Dict) -> Any:
        return self.post("group/create/", data)

    def update_group(self, id: int, data: Dict) -> Any:
        return self.patch(f"group/{id}/", data)

    def delete_group(self, id: int) -> Any:
        return self.delete(f"group/{id}/")

    def clone_group(self, id: int, data: Optional[Dict] = None) -> Any:
        return self.post(f"group/{id}/clone/", data or {})

    def add_group_credits(self, id: int, credits: int) -> Any:
        return self.post(f"group/{id}/add_credits/", {"credits": credits})

    # Страницы
    def get_page(self, id: int) -> Any:
        return self.get(f"page/{id}/")

    def create_page(self, data: Dict) -> Any:
        return self.post("page/create/", data)

    def update_page(self, id: int, data: Dict) -> Any:
        return self.patch(f"page/{id}/", data)

    def delete_page(self, id: int) -> Any:
        return self.delete(f"page/{id}/")

    def clone_page(self, id: int) -> Any:
        return self.post(f"page/{id}/clone/")

    def move_page_up(self, id: int) -> Any:
        return self.post(f"page/{id}/up/")

    def move_page_down(self, id: int) -> Any:
        return self.post(f"page/{id}/down/")

    def start_page(self, id: int) -> Any:
        return self.post(f"page/{id}/start/")

    def stop_page(self, id: int) -> Any:
        return self.post(f"page/{id}/stop/")

    # Статистика
    def get_stats(self, params: Dict) -> Any:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return self.get(f"pages-compiled-stats/?{query}")
