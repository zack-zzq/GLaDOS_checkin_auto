"""Gotify 消息推送模块"""

import logging
import os

import requests

logger = logging.getLogger(__name__)


def send_notification(content: str, status: str = "结果") -> None:
    """通过 Gotify 发送消息推送。

    如果未配置 GOTIFY_URL 或 GOTIFY_TOKEN，则跳过推送，仅输出日志。

    Args:
        content: 推送消息内容
        status: 状态字符串，用于标题格式化中的 {status} 占位符
    """
    gotify_url = os.environ.get("GOTIFY_URL", "").rstrip("/")
    gotify_token = os.environ.get("GOTIFY_TOKEN", "")

    if not gotify_url or not gotify_token:
        logger.info("未配置 Gotify，跳过消息推送")
        return

    title_format = os.environ.get("GOTIFY_TITLE_FORMAT", "GLaDOS签到 - {status}")
    priority = int(os.environ.get("GOTIFY_PRIORITY", "5"))

    try:
        title = title_format.format(status=status)
    except (KeyError, IndexError):
        title = f"GLaDOS签到 - {status}"
        logger.warning("GOTIFY_TITLE_FORMAT 格式化失败，使用默认标题: %s", title)

    api_url = f"{gotify_url}/message"
    payload = {
        "title": title,
        "message": content,
        "priority": priority,
    }

    try:
        resp = requests.post(
            api_url,
            params={"token": gotify_token},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Gotify 推送成功")
    except requests.RequestException as e:
        logger.error("Gotify 推送失败: %s", e)
