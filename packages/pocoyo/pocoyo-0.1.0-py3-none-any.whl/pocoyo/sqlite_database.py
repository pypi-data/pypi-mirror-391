import sqlite3
import json
from typing import Any, Dict, List, Optional

class SQLiteDatabase:
    """
    Простая база данных на основе SQLite
    """
    
    def __init__(self, filename: str = "database.sqlite"):
        self.filename = filename
        self._create_table()
    
    def _create_table(self):
        """Создает таблицу если она не существует"""
        with sqlite3.connect(self.filename) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            conn.commit()
    
    def _serialize_value(self, value: Any) -> str:
        """Сериализует значение в JSON строку"""
        return json.dumps(value, ensure_ascii=False)
    
    def _deserialize_value(self, value: str) -> Any:
        """Десериализует значение из JSON строки"""
        if value is None:
            return None
        return json.loads(value)
    
    def set(self, key: str, value: Any):
        """Устанавливает значение по ключу"""
        serialized_value = self._serialize_value(value)
        
        with sqlite3.connect(self.filename) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)',
                (key, serialized_value)
            )
            conn.commit()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение по ключу"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute(
                'SELECT value FROM data WHERE key = ?',
                (key,)
            )
            result = cursor.fetchone()
            
            if result is None:
                return default
            
            return self._deserialize_value(result[0])
    
    def delete(self, key: str) -> bool:
        """Удаляет ключ"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute(
                'DELETE FROM data WHERE key = ?',
                (key,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_all(self) -> Dict[str, Any]:
        """Возвращает все данные"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute('SELECT key, value FROM data')
            results = cursor.fetchall()
            
            data = {}
            for key, value in results:
                data[key] = self._deserialize_value(value)
            
            return data
    
    def clear(self):
        """Очищает базу данных"""
        with sqlite3.connect(self.filename) as conn:
            conn.execute('DELETE FROM data')
            conn.commit()
    
    def keys(self) -> List[str]:
        """Возвращает все ключи"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute('SELECT key FROM data')
            return [row[0] for row in cursor.fetchall()]
    
    def exists(self, key: str) -> bool:
        """Проверяет существование ключа"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute(
                'SELECT 1 FROM data WHERE key = ?',
                (key,)
            )
            return cursor.fetchone() is not None
    
    def count(self) -> int:
        """Возвращает количество записей"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM data')
            return cursor.fetchone()[0]
    
    def search(self, pattern: str) -> Dict[str, Any]:
        """Ищет ключи по шаблону (LIKE)"""
        with sqlite3.connect(self.filename) as conn:
            cursor = conn.execute(
                'SELECT key, value FROM data WHERE key LIKE ?',
                (f'%{pattern}%',)
            )
            results = cursor.fetchall()
            
            data = {}
            for key, value in results:
                data[key] = self._deserialize_value(value)
            
            return data
    
    def backup(self, backup_file: str = None):
        """Создает резервную копию базы данных"""
        if not backup_file:
            import time
            backup_file = f"{self.filename}.backup.{int(time.time())}"
        
        import shutil
        shutil.copy2(self.filename, backup_file)