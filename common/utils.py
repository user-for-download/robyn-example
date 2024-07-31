import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, Union, List, Callable, TypeVar, Awaitable, Iterable
from urllib.parse import quote

import pytz
import requests
from dateutil import parser
from robyn import logger, Request, Response

from common.constants import HEROES
from config.settings import settings, templates

s_tz = settings.TIME_ZONE

T = TypeVar('T', Dict[str, Any], List[Any])


def now_tz(tz: str = s_tz) -> datetime:
    try:
        return datetime.now(pytz.timezone(tz))
    except Exception as e:
        logger.error(f"now_tz An unexpected error occurred: {str(e)}")
        return datetime.now()


def get_delta_time(last_dt: datetime, tz: str = s_tz) -> str:
    try:
        if last_dt is None:
            return f"ERh:ERm"
        if last_dt.tzinfo is None:
            last_dt = pytz.timezone(tz).localize(last_dt)

        now = now_tz()
        delta = now - last_dt

        if delta.total_seconds() < 3600:
            minutes = delta.total_seconds() // 60
            return f"{int(minutes)}m ago"
        elif delta.total_seconds() < 86400:
            hours = delta.total_seconds() // 3600
            return f"{int(hours)}h ago"
        else:
            return last_dt.strftime('%d.%m.%y')

    except Exception as e:
        logger.error(f"get_delta_time An unexpected error occurred: {str(e)}")
        return f"ERh:ERm"


def date_as_number(dt: datetime = now_tz()) -> int:
    try:
        return int(dt.timestamp())
    except Exception as e:
        logger.error(f"Exception in datetime_to_int: {repr(e)}")
        return 0


def unix_to_datetime(unix_timestamp: Optional[int], tz: str = s_tz) -> Optional[datetime] | None:
    try:
        if unix_timestamp:
            cur_tz = pytz.timezone(tz)
            return datetime.fromtimestamp(unix_timestamp, cur_tz)
    except Exception as e:
        logger.error(f"unix_to_datetime exception: {repr(e)}")
    return None


def unix_to_string(unix_timestamp: Optional[int], tz: str = s_tz) -> str | None:
    try:
        if unix_timestamp:
            cur_tz = pytz.timezone(tz)
            return datetime.fromtimestamp(unix_timestamp, cur_tz).strftime('%d.%m.%Y')
    except Exception as e:
        logger.error(f"unix_to_datetime exception: {repr(e)}")
    return None


def seconds_to_hours_minutes(duration_seconds: Union[int, None]) -> Union[timedelta, int, None]:
    """
    Convert duration in seconds to a timedelta object.

    Args:
        duration_seconds (int): The duration in seconds.

    Returns:
        Union[timedelta, int, None]: The duration as a timedelta object if conversion is successful,
                                     otherwise the original duration.
    """
    try:
        duration_seconds = duration_seconds if isinstance(duration_seconds, int) else 0
        duration_timedelta = timedelta(seconds=duration_seconds)
        return duration_timedelta
    except Exception as e:
        logger.error(f"seconds_to_hours_minutes exception: {repr(e)}")
        return duration_seconds


def convert_to_datetime(date_string: Optional[str], tz: str = s_tz) -> str | None:
    if not date_string:
        return None

    try:
        # Strip any leading or trailing whitespace from the input string
        date_string = date_string.strip()

        # Parse the date string into a naive datetime object
        naive_dt = parser.isoparse(date_string)

        # Get the timezone object
        timezone = pytz.timezone(tz)

        # Localize the naive datetime object to the specified timezone
        aware_dt = timezone.localize(naive_dt)

        return aware_dt.strftime('%d.%m.%Y')
    except ValueError as e:
        # Handle the case where the date string does not match the expected format
        print(f"Invalid date string format: {date_string}: {repr(e)}")
        return None
    except pytz.UnknownTimeZoneError as e:
        # Handle unknown timezone errors
        print(f"Unknown timezone: {tz}: {repr(e)}")
        return None


def response_to_json(url: str) -> Optional[Any]:
    try:
        token = settings.TOKEN_STRATZ
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        if json_data:
            return json_data
        else:
            logger.warning(f"JSON is empty data for URL: {url}")
            return None
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL error occurred: {e}")
    except requests.RequestException as e:
        logger.error(f"RequestException while requesting URL {url}: {repr(e)}")
    except ValueError as e:
        logger.error(f"ValueError while parsing JSON from URL {url}: {repr(e)}")
    except Exception as e:
        logger.error(f"Unexpected exception: {repr(e)}")
    return None


async def fetch_data(url: str, expected_type: Union[type[Dict[str, Any]], type[List[Any]]]) -> Optional[T]:
    try:
        response = response_to_json(url)
        if isinstance(response, expected_type):
            return response
        else:
            logger.error(f"Unexpected response format: {response}")
            return None
    except Exception as e:
        logger.error(f"fetch_data: Error fetching data: {e}")
        return None


def int_to_abs(my_dict: Dict[str, Any], key: str) -> Optional[int]:
    try:
        if my_dict and key in my_dict:
            value = my_dict[key]
            if isinstance(value, int):
                return abs(value)
        return None
    except Exception as e:
        logger.error(f"to_abs An unexpected error occurred: {str(e)}")
        return None


def sum_elements(input_string: List) -> Union[int, str]:
    try:
        # Convert the input string to a list of integers
        if input_string:
            input_list = eval(str(input_string))

            # Ensure the result is a list
            if not isinstance(input_list, list):
                logger.error(ValueError("Input string does not evaluate to a list."))

            # Calculate the sum of the elements in the list
            total_sum = sum(input_list)

            return total_sum
    except Exception as e:
        logger.error(f"sum_elements An unexpected error occurred: {str(e)}")


def get_hero_info(hero_id: int) -> tuple:
    try:
        hero_info = HEROES.get(hero_id, "default.png")  # Replace "default" with your desired default value
        hero_name = hero_info.split(".")[0]
        hero_image_url = f"{settings.URL_IMG_HERO}/npc_dota_hero_{hero_info}"
        return hero_name, hero_image_url
    except Exception as e:
        logger.error(f"get_hero_info An unexpected error occurred: {str(e)}")


def scale_size(count, min_count, max_count, min_size=30, max_size=100):
    if max_count == min_count:
        return (max_size + min_size) / 2
    return min_size + (count - min_count) * (max_size - min_size) / (max_count - min_count)


async def save_data_if_exists(
        data: Optional[Dict[str, Any]],
        key: str,
        func: Union[Callable[[Dict[str, Any]], Awaitable[Optional[Any]]]]
) -> Optional[Any]:
    if isinstance(data, dict) and key in data:
        save_data = data.get(key)
        if save_data is not None and callable(func):
            try:
                return await func(save_data)
            except TypeError as e:
                logger.error("Error in save_data_if_exists with function %s: %s", func, e)
    return None


async def process_related_data(
        data: Optional[Dict[str, Any]],
        key: str,
        save_function: Callable[..., Awaitable[None]],
        *args: Any
) -> Optional[None]:
    try:
        if data and key in data:
            items = data.get(key, [])
            items = items if isinstance(items, list) else [items]

            # Create tasks for each item and await them concurrently
            async with asyncio.TaskGroup() as tg:
                for item in items:
                    tg.create_task(save_function(item, *args))

    except Exception as e:
        logger.error(f"process_related_data: Error processing related data for key '{key}': {e}")


async def process_entities(entity_ids: Iterable[int], task_function: Callable[[int], Any], entity_name: str) -> None:
    """
    Universal function to process entities asynchronously.

    Args:
        entity_ids (Iterable[int]): Iterable to retrieve entity IDs.
        task_function (Callable[[int], Any]): The async task function to be called (e.g., task_get_and_save_player).
        entity_name (str): String representing the entity type (e.g., 'Player' or 'Account').
    """
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {}
            for entity_id in entity_ids:
                task = tg.create_task(task_function(entity_id))
                tasks[task] = entity_id

            for task in tasks:
                entity_id = tasks[task]
                try:
                    await task  # Wait for the task to complete
                    logger.info("%s ID: %s processed successfully", entity_name, entity_id)
                except Exception as e:
                    logger.error("Error processing %s ID: %s, error: %s", entity_name, entity_id, repr(e))
    except Exception as e:
        logger.error("Failed to process %s entities: %s", entity_name, repr(e))


async def parse_int(s: str) -> Optional[int]:
    try:
        return int(s) if isinstance(s, str) else None
    except ValueError:
        logger.error("parse_int ValueError: %s", s)
        return None


def is_valid_email(email: str) -> bool:
    """
    Check if the provided string is a valid email address.

    Args:
        email (str): The email address to check.

    Returns:
        bool: True if the string is a valid email address, False otherwise.
    """
    # Define a regular expression pattern for validating email addresses
    if email:
        email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

        # Use the pattern to match the input email string
        return bool(email_pattern.match(email))
    return False


def is_strong_password(password: str) -> bool:
    """
    Check if the provided password is strong.

    A strong password should meet the following criteria:
    - At least 8 characters long
    - Contains both uppercase and lowercase letters
    - Contains at least one number
    - Contains at least one special character

    Args:
        password (str): The password to check.

    Returns:
        bool: True if the password is strong, False otherwise.
    """
    if len(password) < 8:
        return False

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False

    # Check for at least one special character
    if not re.search(r'[!_@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


def redirect_response(location: str, status_code: int = 302) -> Response:
    return Response(
        status_code=status_code,
        headers={"Location": quote(location, safe=":/%#?=@[]!$&'()*+,;")},
        description="Redirecting..."
    )


def return_response(status_code: int = 302, headers: Dict[str, Any] = Dict, desc: str = "Redirecting...") -> Response:
    return Response(
        status_code=status_code,
        headers=headers,
        description=desc
    )


def not_found_response(request: Request, type_: str = 'type', id_: any = 0) -> Response:
    context = {"request": request, "type_": type_, "id_": id_, "user": {}}
    template = "/404.html"
    template = templates.render_template(template, **context)
    return template
