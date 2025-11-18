import os
import logging
import requests
from paper_inbox.modules import config
from paper_inbox.modules.utils import retry_on_failure
from paper_inbox.modules.loggers import setup_logger

logger = setup_logger('telegram', logging.INFO, False)

@retry_on_failure()
def send_telegram_notification(msg: str):
    if config.send_telegram_notifications == False:
        return 
    send_msg(msg)

def send_msg(msg: str):
    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    data = {
        'chat_id': config.telegram_chat_id,
        'text': msg,
        'parse_mode': 'html'
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.info("Telegram message sent successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram message: {e}")
        if e.response:
            logger.error(f"Error response from Telegram API: {e.response.text}")
        return None


def send_video(video_path, caption=''):
    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendVideo"

    # Check if the file exists and is readable
    if not os.path.isfile(video_path) or not os.access(video_path, os.R_OK):
        raise FileNotFoundError(f"File {video_path} does not exist or is not readable")

    # Get the file size
    file_size = os.path.getsize(video_path)

    data = {
        'chat_id': config.telegram_chat_id,
        'caption': caption,
    }

    with open(video_path, 'rb') as video_file:
        files = {'video': ('video.mp4', video_file, 'video/mp4')}

        # Print some debug information
        logger.info(f"Uploading file: {video_path}")
        logger.info(f"File size: {file_size} bytes")

        response = requests.post(url, data=data, files=files)

    # Check the response
    if response.status_code != 200:
        logger.error(f"Error response from Telegram API: {response.text}")
        response.raise_for_status()

    result = response.json()

    # Check if the response contains the expected video data
    if 'result' in result and 'video' in result['result']:
        logger.info("Video successfully uploaded")
        return result
    else:
        logger.error(f"Unexpected response from Telegram API: {result}")
        raise ValueError("Failed to upload video")