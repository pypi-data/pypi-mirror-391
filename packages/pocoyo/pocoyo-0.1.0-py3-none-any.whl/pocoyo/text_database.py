import json
import os
from typing import Any, Dict, List, Optional

class TextDatabase:
    """
    Простая текстовая база данных на основе JSON
    """
    
    def __init__(self, filename: str = "database.json"):
        self.filename = filename
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Загружает данные из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self):
        """Сохраняет данные в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def set(self, key: str, value: Any):
        """Устанавливает значение по ключу"""
        self.data[key] = value
        self._save_data()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение по ключу"""
        return self.data.get(key, default)
    
    def delete(self, key: str) -> bool:
        """Удаляет ключ"""
        if key in self.data:
            del self.data[key]
            self._save_data()
            return True
        return False
    
    def get_all(self) -> Dict[str, Any]:
        """Возвращает все данные"""
        return self.data.copy()
    
    def clear(self):
        """Очищает базу данных"""
        self.data = {}
        self._save_data()
    
    def keys(self) -> List[str]:
        """Возвращает все ключи"""
        return list(self.data.keys())
    
    def exists(self, key: str) -> bool:
        """Проверяет существование ключа"""
        return key in self.data
    
    def backup(self, backup_file: str = None):
        """Создает резервную копию"""
        if not backup_file:
            import time
            backup_file = f"{self.filename}.backup.{int(time.time())}"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)