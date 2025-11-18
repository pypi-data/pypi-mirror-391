#!/usr/bin/env python3
"""
MCP Server для Rodin Gen-2 API
Предоставляет инструменты для генерации 3D моделей через Rodin Gen-2 API
"""

import os
import logging
import asyncio
import uuid
from typing import Any, Optional
from pathlib import Path

import httpx
import aiofiles
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования (используем stderr, не stdout для STDIO транспорта)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

download_tasks: dict[str, dict[str, Any]] = {}
download_tasks_lock = asyncio.Lock()

# Инициализация FastMCP сервера
mcp = FastMCP("rodin-gen2")

# Константы
RODIN_API_BASE_URL = "https://api.hyper3d.com/api/v2"
RODIN_API_KEY = os.getenv("RODIN_API_KEY")

if not RODIN_API_KEY:
    logger.warning("RODIN_API_KEY не установлен в переменных окружения")


async def make_rodin_request(
    endpoint: str,
    method: str = "GET",
    files: Optional[dict] = None,
    data: Optional[dict] = None,
    timeout: float = 60.0
) -> dict[str, Any]:
    """
    Выполняет запрос к Rodin API с обработкой ошибок
    
    Args:
        endpoint: Конечная точка API (например, "/rodin")
        method: HTTP метод (GET, POST и т.д.)
        files: Файлы для multipart/form-data запроса
        data: Данные формы
        timeout: Таймаут запроса в секундах
        
    Returns:
        Ответ API в формате JSON
        
    Raises:
        Exception: При ошибках API или сети
    """
    if not RODIN_API_KEY:
        raise ValueError("RODIN_API_KEY не установлен. Установите его в .env файле")
    
    headers = {
        "Authorization": f"Bearer {RODIN_API_KEY}"
    }
    
    url = f"{RODIN_API_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            if method.upper() == "POST" and files:
                # Для multipart/form-data запросов
                response = await client.post(url, headers=headers, files=files, data=data)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, data=data)
            elif method.upper() == "GET":
                response = await client.get(url, headers=headers)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"HTTP ошибка {e.response.status_code}: {error_detail}")
            raise Exception(f"Rodin API ошибка ({e.response.status_code}): {error_detail}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {str(e)}")
            raise Exception(f"Ошибка сети при обращении к Rodin API: {str(e)}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {str(e)}")
            raise


@mcp.tool()
async def generate_3d_text_to_3d(
    prompt: str,
    seed: Optional[int] = None,
    geometry_file_format: str = "glb",
    material: str = "PBR",
    mesh_simplify: bool = False,
    quality_override: Optional[int] = None,
    bbox_condition: Optional[list[int]] = None
) -> str:
    """
    Генерирует 3D модель из текстового описания (Text-to-3D)
    
    Args:
        prompt: Текстовое описание 3D модели для генерации
        seed: Seed для воспроизводимости (0-65535). Опционально
        geometry_file_format: Формат файла (glb, usdz, fbx, obj, stl). По умолчанию glb
        material: Тип материала (PBR, Shaded, All). По умолчанию PBR
        mesh_simplify: Упростить меш. По умолчанию False
        quality_override: Переопределение качества (количество полигонов). Опционально
        bbox_condition: Условие bounding box [width, height, length]. Опционально
        
    Returns:
        UUID задачи для проверки статуса и загрузки результата
    """
    logger.info(f"Запуск Text-to-3D генерации с промптом: {prompt}")
    
    # Подготовка данных формы
    form_data = {
        "tier": "Gen-2",
        "prompt": prompt,
        "geometry_file_format": geometry_file_format,
        "material": material,
        "mesh_simplify": str(mesh_simplify)
    }
    
    if seed is not None:
        if not (0 <= seed <= 65535):
            raise ValueError("Seed должен быть в диапазоне 0-65535")
        form_data["seed"] = str(seed)
    
    if quality_override is not None:
        form_data["quality_override"] = str(quality_override)
    
    if bbox_condition:
        if len(bbox_condition) != 3:
            raise ValueError("bbox_condition должен содержать 3 элемента [width, height, length]")
        form_data["bbox_condition"] = str(bbox_condition)
    
    try:
        result = await make_rodin_request(
            endpoint="/rodin",
            method="POST",
            data=form_data,
            timeout=120.0
        )
        
        uuid = result.get("uuid")
        jobs = result.get("jobs", {})
        subscription_key = jobs.get("subscription_key")
        
        if not uuid:
            raise Exception("API не вернул UUID задачи")
        
        logger.info(f"Задача создана успешно. UUID: {uuid}")
        
        message = f"✅ Задача генерации создана успешно!\n\n"
        message += f"📋 UUID задачи: {uuid}\n"
        
        if subscription_key:
            message += f"🔑 Subscription Key: {subscription_key}\n\n"
            message += "Рекомендуемый сценарий:\n"
            message += f"  1) Проверяйте прогресс через tool check_task_status с subscription_key '{subscription_key}'.\n"
            message += f"  2) Когда все подзадачи в статусе done, вызовите start_download_result с UUID '{uuid}' (и при необходимости output_dir).\n"
            message += "  3) Отслеживайте ход загрузки через check_download_result_status по ID задачи загрузки.\n\n"
            message += "Альтернатива: можно использовать download_result с UUID задачи, но этот инструмент выполняет загрузку синхронно и может занимать больше времени."
        else:
            message += f"\n⚠️ Внимание: subscription_key не найден в ответе API. Вы сможете сразу вызвать start_download_result с UUID задачи для загрузки результата."
        
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при генерации: {str(e)}")
        return f"❌ Ошибка при создании задачи генерации: {str(e)}"


@mcp.tool()
async def generate_3d_image_to_3d(
    image_paths: list[str],
    prompt: Optional[str] = None,
    use_original_alpha: bool = False,
    seed: Optional[int] = None,
    geometry_file_format: str = "glb",
    material: str = "PBR",
    mesh_simplify: bool = False,
    quality_override: Optional[int] = None,
    condition_mode: str = "concat",
    bbox_condition: Optional[list[int]] = None
) -> str:
    """
    Генерирует 3D модель из изображения(й) (Image-to-3D)
    
    Args:
        image_paths: Список путей к изображениям (до 5 файлов)
        prompt: Текстовое описание. Опционально (если не указано, будет сгенерировано AI)
        use_original_alpha: Использовать оригинальный альфа-канал. По умолчанию False
        seed: Seed для воспроизводимости (0-65535). Опционально
        geometry_file_format: Формат файла (glb, usdz, fbx, obj, stl). По умолчанию glb
        material: Тип материала (PBR, Shaded, All). По умолчанию PBR
        mesh_simplify: Упростить меш. По умолчанию False
        quality_override: Переопределение качества. Опционально
        condition_mode: Режим для множественных изображений (concat). По умолчанию concat
        bbox_condition: Условие bounding box [width, height, length]. Опционально
        
    Returns:
        UUID задачи для проверки статуса и загрузки результата
    """
    logger.info(f"Запуск Image-to-3D генерации с {len(image_paths)} изображением(ями)")
    
    if not image_paths:
        return "❌ Необходимо указать хотя бы одно изображение"
    
    if len(image_paths) > 5:
        return "❌ Максимум 5 изображений разрешено"
    
    # Подготовка файлов
    files = []
    data = {
        "tier": "Gen-2",
        "geometry_file_format": geometry_file_format,
        "material": material,
        "mesh_simplify": str(mesh_simplify),
        "use_original_alpha": str(use_original_alpha)
    }
    
    # Открываем и читаем файлы изображений
    try:
        for image_path in image_paths:
            path = Path(image_path)
            if not path.exists():
                return f"❌ Файл не найден: {image_path}"
            
            with open(path, 'rb') as f:
                image_data = f.read()
                # Определяем MIME тип на основе расширения
                ext = path.suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')
                
                files.append(('images', (path.name, image_data, mime_type)))
        
        if prompt:
            data["prompt"] = prompt
        
        if seed is not None:
            if not (0 <= seed <= 65535):
                return "❌ Seed должен быть в диапазоне 0-65535"
            data["seed"] = str(seed)
        
        if quality_override is not None:
            data["quality_override"] = str(quality_override)
        
        if len(image_paths) > 1:
            data["condition_mode"] = condition_mode
        
        if bbox_condition:
            if len(bbox_condition) != 3:
                return "❌ bbox_condition должен содержать 3 элемента [width, height, length]"
            data["bbox_condition"] = str(bbox_condition)
        
        result = await make_rodin_request(
            endpoint="/rodin",
            method="POST",
            files=files,
            data=data,
            timeout=120.0
        )
        
        uuid = result.get("uuid")
        jobs = result.get("jobs", {})
        subscription_key = jobs.get("subscription_key")
        
        if not uuid:
            raise Exception("API не вернул UUID задачи")
        
        logger.info(f"Задача создана успешно. UUID: {uuid}")
        
        message = f"✅ Задача генерации создана успешно!\n\n"
        message += f"📋 UUID задачи: {uuid}\n"
        
        if subscription_key:
            message += f"🔑 Subscription Key: {subscription_key}\n\n"
            message += "Рекомендуемый сценарий:\n"
            message += f"  1) Проверяйте прогресс через tool check_task_status с subscription_key '{subscription_key}'.\n"
            message += f"  2) Когда все подзадачи в статусе done, вызовите start_download_result с UUID '{uuid}' (и при необходимости output_dir).\n"
            message += "  3) Отслеживайте ход загрузки через check_download_result_status по ID задачи загрузки.\n\n"
            message += "Альтернатива: можно использовать download_result с UUID задачи, но этот инструмент выполняет загрузку синхронно и может занимать больше времени."
        else:
            message += f"\n⚠️ Внимание: subscription_key не найден в ответе API. Вы сможете сразу вызвать start_download_result с UUID задачи для загрузки результата."
        
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при генерации: {str(e)}")
        return f"❌ Ошибка при создании задачи генерации: {str(e)}"


@mcp.tool()
async def check_task_status(subscription_key: str) -> str:
    """
    Проверяет статус задачи генерации
    
    Args:
        subscription_key: Subscription key задачи (jobs.subscription_key из ответа generate_3d_*)
        
    Returns:
        Текущий статус всех подзадач
    """
    logger.info(f"Проверка статуса задачи с subscription_key: {subscription_key}")
    
    try:
        result = await make_rodin_request(
            endpoint="/status",
            method="POST",
            data={"subscription_key": subscription_key},
            timeout=5.0
        )
        
        jobs = result.get("jobs", [])
        
        if not jobs:
            return "❌ Задачи не найдены"
        
        message = "📊 Статус задач:\n\n"
        
        for job in jobs:
            uuid = job.get("uuid", "unknown")
            status = job.get("status", "unknown")
            
            status_emoji = {
                "waiting": "⏳",
                "generating": "🔄",
                "done": "✅",
                "failed": "❌"
            }.get(status.lower(), "❓")
            
            message += f"{status_emoji} UUID: {uuid}\n"
            message += f"   Статус: {status}\n\n"
        
        # Проверяем, все ли задачи завершены
        all_done = all(job.get("status", "").lower() == "done" for job in jobs)
        any_failed = any(job.get("status", "").lower() == "failed" for job in jobs)
        
        if all_done:
            message += "✅ Все задачи завершены! Используйте download_result для загрузки файлов."
        elif any_failed:
            message += "❌ Некоторые задачи завершились с ошибкой."
        else:
            message += "🔄 Генерация в процессе. Проверьте статус позже."
        
        logger.info(f"Проверен статус для subscription_key: {subscription_key}")
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса: {str(e)}")
        return f"❌ Ошибка при проверке статуса: {str(e)}"


async def _download_result_background(task_uuid: str, output_dir: Optional[str], task_id: str) -> None:
    try:
        async with download_tasks_lock:
            task_info = download_tasks.get(task_id)
            if task_info is not None:
                task_info["status"] = "running"

        result = await make_rodin_request(
            endpoint="/download",
            method="POST",
            data={"task_uuid": task_uuid},
            timeout=5.0
        )

        file_list = result.get("list", [])

        if not file_list:
            raise Exception("Список файлов пуст. Возможно, задача еще не завершена.")

        if output_dir is None:
            output_dir = "."

        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)

        downloaded_files: list[dict[str, Any]] = []
        total_size = 0

        async with httpx.AsyncClient(timeout=60.0) as client:
            for file_info in file_list:
                file_url = file_info.get("url")
                file_name = file_info.get("name", "unnamed_file")

                if not file_url:
                    logger.warning(f"Пропущен файл без URL: {file_name}")
                    continue

                output_file = output_directory / file_name

                logger.info(f"Загрузка файла: {file_name}")
                response = await client.get(file_url)
                response.raise_for_status()

                async with aiofiles.open(output_file, 'wb') as f:
                    await f.write(response.content)

                file_size = output_file.stat().st_size
                total_size += file_size
                size_mb = file_size / (1024 * 1024)

                downloaded_files.append(
                    {
                        "name": file_name,
                        "path": str(output_file.absolute()),
                        "size_mb": round(size_mb, 2),
                    }
                )

                logger.info(f"Файл загружен: {output_file} ({size_mb:.2f} MB)")

        total_size_mb = total_size / (1024 * 1024)

        async with download_tasks_lock:
            task_info = download_tasks.get(task_id)
            if task_info is not None:
                task_info["status"] = "completed"
                task_info["files"] = downloaded_files
                task_info["output_dir"] = str(output_directory.absolute())
                task_info["total_size_mb"] = round(total_size_mb, 2)

    except Exception as e:
        logger.error(f"Ошибка при фоновой загрузке результата: {str(e)}")
        async with download_tasks_lock:
            task_info = download_tasks.get(task_id)
            if task_info is not None:
                task_info["status"] = "failed"
                task_info["error"] = str(e)


@mcp.tool()
async def start_download_result(task_uuid: str, output_dir: Optional[str] = None) -> str:
    logger.info(f"Запуск фоновой загрузки результата задачи: {task_uuid}")

    task_id = str(uuid.uuid4())

    async with download_tasks_lock:
        download_tasks[task_id] = {
            "status": "pending",
            "error": None,
            "files": [],
            "output_dir": output_dir,
            "total_size_mb": 0.0,
            "task_uuid": task_uuid,
        }

    asyncio.create_task(_download_result_background(task_uuid, output_dir, task_id))

    message = "✅ Фоновая загрузка запущена!\n\n"
    message += f"📋 ID задачи загрузки: {task_id}\n"
    message += "Используйте check_download_result_status с этим ID, чтобы проверить статус."
    return message


@mcp.tool()
async def check_download_result_status(task_id: str) -> str:
    async with download_tasks_lock:
        task_info = download_tasks.get(task_id)

    if not task_info:
        return "❌ Задача загрузки не найдена."

    status = task_info.get("status", "unknown")

    if status == "pending":
        return "⏳ Задача загрузки поставлена в очередь."
    if status == "running":
        return "🔄 Загрузка результата выполняется."
    if status == "failed":
        error = task_info.get("error") or "Неизвестная ошибка"
        return f"❌ Задача загрузки завершилась с ошибкой: {error}"
    if status != "completed":
        return f"❓ Неизвестный статус задачи: {status}"

    message = "✅ Загрузка результата завершена!\n\n"
    output_dir = task_info.get("output_dir")
    total_size_mb = task_info.get("total_size_mb", 0.0)

    if output_dir:
        message += f"📁 Директория: {output_dir}\n"
    message += f"💾 Общий размер: {total_size_mb:.2f} MB\n\n"

    files = task_info.get("files") or []
    if files:
        message += "📄 Загруженные файлы:\n"
        for file_info in files:
            name = file_info.get("name", "unknown")
            size_mb = file_info.get("size_mb", 0.0)
            message += f"  • {name} ({size_mb} MB)\n"

    return message


@mcp.tool()
async def download_result(task_uuid: str, output_dir: Optional[str] = None) -> str:
    """
    Загружает результаты генерации 3D модели
    
    Args:
        task_uuid: UUID задачи (получается из generate_3d_* как uuid, не subscription_key)
        output_dir: Директория для сохранения файлов. Если не указана, используется текущая директория
        
    Returns:
        Информация о загруженных файлах или сообщение об ошибке
    """
    logger.info(f"Загрузка результата задачи: {task_uuid}")
    
    try:
        # Получаем список файлов для загрузки
        result = await make_rodin_request(
            endpoint="/download",
            method="POST",
            data={"task_uuid": task_uuid},
            timeout=5.0
        )
        
        file_list = result.get("list", [])
        
        if not file_list:
            return "❌ Список файлов пуст. Возможно, задача еще не завершена. Проверьте статус с помощью check_task_status."
        
        # Определяем директорию для сохранения
        if output_dir is None:
            output_dir = "."
        
        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)
        
        downloaded_files = []
        total_size = 0
        
        # Загружаем каждый файл
        async with httpx.AsyncClient(timeout=60.0) as client:
            for file_info in file_list:
                file_url = file_info.get("url")
                file_name = file_info.get("name", "unnamed_file")
                
                if not file_url:
                    logger.warning(f"Пропущен файл без URL: {file_name}")
                    continue
                
                output_file = output_directory / file_name
                
                logger.info(f"Загрузка файла: {file_name}")
                response = await client.get(file_url)
                response.raise_for_status()
                
                async with aiofiles.open(output_file, 'wb') as f:
                    await f.write(response.content)
                
                file_size = output_file.stat().st_size
                total_size += file_size
                size_mb = file_size / (1024 * 1024)
                
                downloaded_files.append({
                    "name": file_name,
                    "path": str(output_file.absolute()),
                    "size_mb": round(size_mb, 2)
                })
                
                logger.info(f"Файл загружен: {output_file} ({size_mb:.2f} MB)")
        
        # Формируем сообщение о результате
        total_size_mb = total_size / (1024 * 1024)
        message = f"✅ Успешно загружено {len(downloaded_files)} файл(ов)!\n\n"
        message += f"📁 Директория: {output_directory.absolute()}\n"
        message += f"💾 Общий размер: {total_size_mb:.2f} MB\n\n"
        message += "📄 Загруженные файлы:\n"
        
        for file_info in downloaded_files:
            message += f"  • {file_info['name']} ({file_info['size_mb']} MB)\n"
        
        return message
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке результата: {str(e)}")
        return f"❌ Ошибка при загрузке результата: {str(e)}"


def main():
    """Точка входа для запуска MCP сервера"""
    logger.info("Запуск Rodin Gen-2 MCP сервера...")
    
    # Проверяем наличие API ключа
    if not RODIN_API_KEY:
        logger.error(
            "RODIN_API_KEY не установлен! "
            "Пожалуйста, создайте .env файл с RODIN_API_KEY=your_api_key"
        )
    
    # Запускаем сервер
    mcp.run()


if __name__ == "__main__":
    main()
