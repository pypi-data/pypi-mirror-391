import requests
import time
from typing import Callable, Dict, Any

class SimpleBot:
    """
    Простой Telegram бот
    """
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.handlers = {}
        self.default_handler = None
        self.running = False
        
    def send_message(self, chat_id: int, text: str) -> Dict[str, Any]:
        """Отправляет сообщение"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_updates(self, offset: int = None) -> Dict[str, Any]:
        """Получает обновления"""
        url = f"{self.base_url}/getUpdates"
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
        response = requests.get(url, params=params)
        return response.json()
    
    def message_handler(self, command: str = None):
        """Декоратор для обработки сообщений"""
        def decorator(func: Callable):
            if command:
                self.handlers[command] = func
            else:
                self.default_handler = func
            return func
        return decorator
    
    def _process_update(self, update: Dict[str, Any]):
        """Обрабатывает одно обновление"""
        if 'message' in update:
            message = update['message']
            text = message.get('text', '')
            chat_id = message['chat']['id']
            
            # Ищем обработчик для команды
            for command, handler in self.handlers.items():
                if text.startswith(command):
                    handler(self, message)
                    return
            
            # Используем обработчик по умолчанию
            if self.default_handler:
                self.default_handler(self, message)
    
    def poll(self):
        """Запускает опрос сервера"""
        self.running = True
        offset = None
        
        print("Бот запущен...")
        
        while self.running:
            try:
                updates = self.get_updates(offset)
                if updates.get('ok'):
                    for update in updates['result']:
                        self._process_update(update)
                        offset = update['update_id'] + 1
                time.sleep(1)
            except Exception as e:
                print(f"Ошибка: {e}")
                time.sleep(5)