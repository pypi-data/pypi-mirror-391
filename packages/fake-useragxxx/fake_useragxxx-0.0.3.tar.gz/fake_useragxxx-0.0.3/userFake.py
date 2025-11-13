import json
import logging
import random
import urllib.request
import urllib.error
from pathlib import Path
from typing import TypedDict, Optional, Union, List, Dict, Any
import importlib.resources
import time
import re
from dataclasses import dataclass
from collections import deque

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('fake_useragent_generator')

class BrowserUserAgentData(TypedDict):
    """Структура данных для User-Agent из browsers.jsonl"""
    useragent: str
    percent: float
    type: str
    browser_version: str
    browser_version_major_minor: float
    platform: str
    # Опциональные поля для обратной совместимости
    browser: Optional[str]
    os: Optional[str]
    os_version: Optional[str]
    device_brand: Optional[str]

@dataclass
class GrayRandomizationConfig:
    """Конфигурация серой рандомизации"""
    # Вероятность мутации User-Agent (0.0 - 1.0)
    mutation_probability: float = 0.3
    # Максимальное изменение версии браузера
    max_version_change: int = 5
    # Максимальное изменение версии ОС
    max_os_version_change: int = 2
    # История последних User-Agent'ов для избежания повторов
    history_size: int = 10
    # Вероятность добавления случайных пробелов
    space_mutation_prob: float = 0.1
    # Вероятность изменения регистра
    case_mutation_prob: float = 0.2

class FakeUserAgentGenerator:
    """Основной класс для генерации фейковых User-Agent'ов"""
    
    # Кеш загруженных данных
    _cached_data: Optional[List[BrowserUserAgentData]] = None
    _last_load_time: float = 0
    _cache_ttl: int = 3600  # 1 час в секундах
    
    def __init__(self, config: Optional[GrayRandomizationConfig] = None):
        self.config = config or GrayRandomizationConfig()
        self.user_agent_history = deque(maxlen=self.config.history_size)
        self._fallback_url = "https://raw.githubusercontent.com/hellysmile/fake-useragent/master/fake_useragent/data/browsers.jsonl"
        
    def _download_fallback_data(self) -> List[BrowserUserAgentData]:
        """
        Скачивание данных с GitHub репозитория как fallback
        """
        logger.info("Скачивание browsers.jsonl с GitHub...")
        try:
            with urllib.request.urlopen(self._fallback_url, timeout=30) as response:
                content = response.read().decode('utf-8')
                
            # Сохраняем файл локально для будущего использования
            local_path = Path("browsers.jsonl")
            local_path.write_text(content, encoding='utf-8')
            logger.info(f"Файл сохранен локально: {local_path.absolute()}")
            
            return self._parse_jsonl_content(content)
            
        except urllib.error.URLError as e:
            logger.error(f"Ошибка скачивания файла: {e}")
            raise RuntimeError(f"Не удалось скачать browsers.jsonl: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при скачивании: {e}")
            raise
    
    def _parse_jsonl_content(self, content: str) -> List[BrowserUserAgentData]:
        """
        Парсинг содержимого JSONL файла
        """
        data = []
        empty_lines = 0
        invalid_lines = 0
        
        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line:
                empty_lines += 1
                continue
                
            try:
                record = json.loads(line)
                
                # Проверка обязательных полей
                required_fields = ['useragent', 'percent', 'type', 
                                 'browser_version', 'browser_version_major_minor', 'platform']
                missing_fields = [field for field in required_fields if field not in record]
                
                if missing_fields:
                    logger.warning(f"Строка {line_num}: отсутствуют поля {missing_fields}")
                    invalid_lines += 1
                    continue
                
                # Приведение типов
                record['percent'] = float(record['percent'])
                record['browser_version_major_minor'] = float(record['browser_version_major_minor'])
                
                # Добавление опциональных полей
                record.setdefault('browser', None)
                record.setdefault('os', None)
                record.setdefault('os_version', None)
                record.setdefault('device_brand', None)
                
                data.append(record)
                
            except json.JSONDecodeError as e:
                logger.warning(f"Строка {line_num}: ошибка JSON - {e}")
                invalid_lines += 1
                continue
            except (ValueError, TypeError) as e:
                logger.warning(f"Строка {line_num}: ошибка данных - {e}")
                invalid_lines += 1
                continue
        
        if empty_lines > 0:
            logger.info(f"Пропущено пустых строк: {empty_lines}")
        if invalid_lines > 0:
            logger.warning(f"Пропущено некорректных строк: {invalid_lines}")
            
        if not data:
            raise RuntimeError("Не удалось загрузить корректные данные из JSONL")
            
        logger.info(f"Успешно загружено записей: {len(data)}")
        return data
    
    def _load_local_file(self, file_path: Path) -> List[BrowserUserAgentData]:
        """
        Загрузка данных из локального файла
        """
        logger.info(f"Загрузка локального файла: {file_path}")
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._parse_jsonl_content(content)
        except Exception as e:
            logger.warning(f"Ошибка загрузки локального файла {file_path}: {e}")
            raise
    
    def load_browsers_data(self, force_reload: bool = False) -> List[BrowserUserAgentData]:
        """
        Загрузка данных о браузерах с кешированием
        """
        current_time = time.time()
        
        # Проверка кеша
        if (not force_reload and self._cached_data and 
            current_time - self._last_load_time < self._cache_ttl):
            logger.debug("Использование кешированных данных")
            return self._cached_data
        
        try:
            # Попытка 1: Загрузка через importlib.resources из пакета
            try:
                with importlib.resources.files('fake_useragent.data').joinpath('browsers.jsonl').open('r', encoding='utf-8') as f:
                    content = f.read()
                self._cached_data = self._parse_jsonl_content(content)
                logger.info("Данные загружены через importlib.resources")
                
            except (FileNotFoundError, ImportError, Exception) as e:
                logger.warning(f"Ошибка загрузки через importlib: {e}")
                
                # Попытка 2: Локальный файл в текущей директории
                local_path = Path("browsers.jsonl")
                if local_path.exists():
                    self._cached_data = self._load_local_file(local_path)
                else:
                    # Попытка 3: Скачивание с GitHub
                    self._cached_data = self._download_fallback_data()
                    
        except Exception as e:
            logger.error(f"Все методы загрузки данных провалились: {e}")
            raise RuntimeError(f"Не удалось загрузить данные браузеров: {e}")
        
        self._last_load_time = current_time
        return self._cached_data
    
    def _mutate_user_agent(self, user_agent: str) -> str:
        """
        Легкая мутация строки User-Agent для большей реалистичности
        """
        if random.random() > self.config.mutation_probability:
            return user_agent
            
        mutations = []
        ua = user_agent
        
        # Мутация 1: Изменение регистра случайных символов
        if random.random() < self.config.case_mutation_prob:
            chars = list(ua)
            for _ in range(max(1, len(chars) // 100)):  # Мутируем ~1% символов
                if chars and random.random() < 0.3:
                    idx = random.randint(0, len(chars) - 1)
                    if chars[idx].isalpha():
                        chars[idx] = chars[idx].lower() if chars[idx].isupper() else chars[idx].upper()
            ua = ''.join(chars)
            mutations.append("case_change")
        
        # Мутация 2: Добавление/удаление пробелов
        if random.random() < self.config.space_mutation_prob:
            if ' ' in ua and random.random() < 0.3:
                # Удаление случайного пробела
                parts = ua.split(' ')
                if len(parts) > 1:
                    join_idx = random.randint(0, len(parts) - 2)
                    parts[join_idx] = parts[join_idx] + parts[join_idx + 1]
                    parts.pop(join_idx + 1)
                    ua = ' '.join(parts)
                    mutations.append("space_remove")
            else:
                # Добавление случайного пробела
                if len(ua) > 10 and random.random() < 0.2:
                    insert_pos = random.randint(5, len(ua) - 5)
                    ua = ua[:insert_pos] + ' ' + ua[insert_pos:]
                    mutations.append("space_add")
        
        # Мутация 3: Небольшие изменения в версиях
        version_pattern = r'(\d+\.\d+(?:\.\d+(?:\.\d+)?)?)'
        versions = re.findall(version_pattern, ua)
        
        if versions:
            for version in set(versions):  # Уникальные версии
                if random.random() < 0.4:
                    parts = version.split('.')
                    if len(parts) >= 3:  # Патч-версия
                        parts[-1] = str(random.randint(0, 99))
                        new_version = '.'.join(parts)
                        ua = ua.replace(version, new_version, 1)
                        mutations.append("patch_version_change")
                    elif len(parts) == 2 and random.random() < 0.2:  # Minor-версия
                        parts[1] = str(random.randint(0, 20))
                        new_version = '.'.join(parts)
                        ua = ua.replace(version, new_version, 1)
                        mutations.append("minor_version_change")
        
        if mutations:
            logger.debug(f"Мутации применены: {mutations}")
            
        return ua
    
    def _generate_browser_version_variation(self, base_version: str) -> str:
        """
        Генерация вариаций версии браузера
        """
        try:
            parts = base_version.split('.')
            if len(parts) >= 3:
                # Изменение патч-версии
                parts[-1] = str(random.randint(0, 99))
            elif len(parts) == 2:
                # Добавление патч-версии
                parts.append(str(random.randint(0, 99)))
            
            # Небольшое изменение minor-версии
            if len(parts) >= 2 and random.random() < 0.3:
                minor = int(parts[1])
                parts[1] = str(max(0, minor + random.randint(-2, 2)))
                
            return '.'.join(parts)
        except (ValueError, IndexError):
            return base_version
    
    def _get_random_accept_language(self) -> str:
        """
        Генерация случайного заголовка Accept-Language
        """
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9,en-US;q=0.8',
            'ru-RU,ru;q=0.9,en;q=0.8',
            'de-DE,de;q=0.9,en;q=0.8',
            'fr-FR,fr;q=0.9,en;q=0.8',
            'es-ES,es;q=0.9,en;q=0.8',
            'ja-JP,ja;q=0.9,en;q=0.8',
            'zh-CN,zh;q=0.9,en;q=0.8',
        ]
        return random.choice(languages)
    
    def _get_random_accept_encoding(self) -> str:
        """
        Генерация случайного заголовка Accept-Encoding
        """
        encodings = [
            'gzip, deflate, br',
            'gzip, deflate',
            'gzip, br',
            'deflate, gzip',
            'br, gzip, deflate',
        ]
        return random.choice(encodings)
    
    def _get_random_connection_header(self) -> str:
        """
        Генерация случайного заголовка Connection
        """
        return random.choice(['keep-alive', 'close'])
    
    def _select_random_user_agent(self, device_type: Optional[str] = None) -> BrowserUserAgentData:
        """
        Выбор случайного User-Agent с учетом истории и типа устройства
        """
        data = self.load_browsers_data()
        
        # Фильтрация по типу устройства если указан
        if device_type:
            filtered_data = [ua for ua in data if ua.get('type', '').lower() == device_type.lower()]
            if filtered_data:
                data = filtered_data
            else:
                logger.warning(f"Не найдено User-Agent для типа {device_type}, используем все доступные")
        
        # Исключение недавно использованных User-Agent'ов
        recent_agents = set(self.user_agent_history)
        available_data = [ua for ua in data if ua['useragent'] not in recent_agents]
        
        # Если все доступные агенты были использованы, очищаем историю
        if not available_data and recent_agents:
            logger.debug("Все User-Agent'ы были использованы, очищаем историю")
            self.user_agent_history.clear()
            available_data = data
        
        # Взвешенный выбор на основе процента использования
        if available_data:
            weights = [ua.get('percent', 1.0) for ua in available_data]
            selected_ua = random.choices(available_data, weights=weights, k=1)[0]
        else:
            selected_ua = random.choice(data)
        
        # Добавляем в историю
        self.user_agent_history.append(selected_ua['useragent'])
        
        return selected_ua
    
    def get_fake_useragent(self, device_type: Optional[str] = None, 
                          mutate: bool = True) -> str:
        """
        Получение случайного фейкового User-Agent с серой рандомизацией
        
        Args:
            device_type: Тип устройства ('desktop', 'mobile', None - любой)
            mutate: Применять ли мутации для реалистичности
            
        Returns:
            Строка User-Agent
        """
        ua_data = self._select_random_user_agent(device_type)
        user_agent = ua_data['useragent']
        
        if mutate:
            user_agent = self._mutate_user_agent(user_agent)
            
        logger.debug(f"Сгенерирован User-Agent: {user_agent}")
        return user_agent
    
    def get_headers(self, device_type: Optional[str] = None) -> Dict[str, str]:
        """
        Получение полного набора HTTP-заголовков для requests
        
        Args:
            device_type: Тип устройства ('desktop', 'mobile', None - любой)
            
        Returns:
            Словарь с HTTP-заголовками
        """
        user_agent = self.get_fake_useragent(device_type, mutate=True)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': self._get_random_accept_language(),
            'Accept-Encoding': self._get_random_accept_encoding(),
            'Connection': self._get_random_connection_header(),
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Дополнительные заголовки для мобильных устройств
        if device_type and device_type.lower() == 'mobile':
            headers.update({
                'Sec-Fetch-User': '?1',
            })
        
        return headers

# Глобальный экземпляр для удобства использования
_default_generator: Optional[FakeUserAgentGenerator] = None

def get_fake_useragent(device_type: Optional[str] = None, 
                      mutate: bool = True) -> str:
    """
    Основная функция для получения фейкового User-Agent
    
    Args:
        device_type: Тип устройства ('desktop', 'mobile', None - любой)
        mutate: Применять ли мутации для реалистичности
        
    Returns:
        Строка User-Agent
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = FakeUserAgentGenerator()
    
    return _default_generator.get_fake_useragent(device_type, mutate)

def get_headers(device_type: Optional[str] = None) -> Dict[str, str]:
    """
    Основная функция для получения полного набора HTTP-заголовков
    
    Args:
        device_type: Тип устройства ('desktop', 'mobile', None - любой)
        
    Returns:
        Словарь с HTTP-заголовками, готовый для использования в requests
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = FakeUserAgentGenerator()
    
    return _default_generator.get_headers(device_type)

def clear_cache() -> None:
    """Очистка кеша данных"""
    global _default_generator
    if _default_generator:
        _default_generator._cached_data = None
        _default_generator.user_agent_history.clear()

class FakeUserAgent:
    def __init__(self, use_cache_server=True, fallback=None, **kwargs):
        self.generator = FakeUserAgentGenerator()
    
    def __getattr__(self, name):
        if name in ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']:
            return lambda: self.generator.get_fake_useragent()
        raise AttributeError(f"Attribute {name} not found")
    
    def random(self):
        return self.generator.get_fake_useragent()

class UserAgent:
    def __init__(self, *args, **kwargs):
        self.generator = FakeUserAgentGenerator()
    
    def __getattr__(self, name):
        if name in ['chrome', 'firefox', 'safari', 'edge', 'opera', 'ie']:
            return lambda: self.generator.get_fake_useragent()
        raise AttributeError(f"Attribute {name} not found")
    
    def random(self):
        return self.generator.get_fake_useragent()