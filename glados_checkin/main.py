"""GLaDOS 自动签到主程序"""

import json
import logging
import os
import time

import requests
import schedule
from dotenv import load_dotenv

from glados_checkin.notifier import send_notification

# 加载 .env 文件
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def get_base_url() -> str:
    """根据环境变量构建 GLaDOS 基础 URL"""
    domain = os.environ.get("GLADOS_DOMAIN", "glados.one")
    return f"https://{domain}"


def checkin() -> None:
    """执行签到逻辑"""
    cookie_str = os.environ.get("GLADOS_COOKIE", "")
    if not cookie_str:
        logger.error("未设置 GLADOS_COOKIE 环境变量")
        return

    cookies = cookie_str.split("&")
    base_url = get_base_url()

    checkin_url = f"{base_url}/api/user/checkin"
    status_url = f"{base_url}/api/user/status"
    referer = f"{base_url}/console/checkin"
    origin = base_url

    domain = os.environ.get("GLADOS_DOMAIN", "glados.one")
    payload = json.dumps({"token": domain})
    results: list[str] = []
    has_failure = False

    for i, cookie in enumerate(cookies, 1):
        logger.info("正在处理第 %d 个账号...", i)
        headers = {
            "cookie": cookie.strip(),
            "referer": referer,
            "origin": origin,
            "user-agent": USER_AGENT,
            "content-type": "application/json;charset=UTF-8",
        }

        try:
            checkin_resp = requests.post(
                checkin_url, headers=headers, data=payload, timeout=30
            )
            status_resp = requests.get(
                status_url, headers=headers, timeout=30
            )

            status_data = status_resp.json().get("data", {})
            left_days = str(status_data.get("leftDays", "未知")).split(".")[0]
            email = status_data.get("email", f"账号{i}")

            if "message" in checkin_resp.text:
                message = checkin_resp.json().get("message", "")
                result = f"{email} - {message} - 剩余 {left_days} 天"
                logger.info(result)
                results.append(result)
            else:
                result = f"{email} - Cookie 已失效"
                logger.warning(result)
                results.append(result)
                has_failure = True

        except requests.RequestException as e:
            result = f"账号{i} - 请求失败: {e}"
            logger.error(result)
            results.append(result)
            has_failure = True

    # 推送结果
    if results:
        content = "\n".join(results)
        status = "失败" if has_failure else "成功"
        send_notification(content, status=status)


def main() -> None:
    """主函数：执行一次签到后按 cron 定时执行"""
    logger.info("GLaDOS 自动签到启动")
    logger.info("当前域名: %s", os.environ.get("GLADOS_DOMAIN", "glados.one"))

    # 启动时立即执行一次
    checkin()

    # 读取 cron 时间配置（简化为 HH:MM 格式，默认 09:00）
    checkin_time = os.environ.get("CHECKIN_TIME", "09:00")
    logger.info("定时签到时间: 每天 %s", checkin_time)

    schedule.every().day.at(checkin_time).do(checkin)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
