import json
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta

import random
import requests
import os

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
# TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')


async def delay_time(ms):
    await asyncio.sleep(ms / 1000)


# 全局浏览器实例
browser = None

# telegram消息
message = 'serv00&ct8自动化脚本运行\n'

async def login(username, password, panel, browser): # 接收 browser 参数
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        # 页面操作直接使用传入的 browser 对象创建
        page = await browser.new_page()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        # 关键修改：使用更精确的 locator
        username_input = page.locator('#id_username')
        if await username_input.count() > 0:  # 确保元素存在
            await username_input.fill("")  # 清空内容
        else:
            print(f"警告：未找到用户名输入框 #id_username")

        await page.fill('#id_username', username)
        await page.fill('#id_password', password)

        # 使用类名定位登录按钮
        login_button = page.locator('.button--primary').nth(1)  # 假设登录按钮是第二个匹配到的元素
        if await login_button.count() > 0:  # 确保元素存在
            await login_button.click()
        else:
            raise Exception('无法找到登录按钮')

        await page.wait_for_load_state() # 使用 wait_for_load_state 替代 waitForNavigation

        # 检查登录状态
        is_logged_in = await page.locator('a[href="/logout/"]').count() > 0
        await page.close()  # 操作结束后关闭页面

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 {username} 登录时出现错误: {e}')
        try:
            await page.close()  # 发生错误时也要关闭页面，确保page对象存在
        except Exception as close_error:
            print(f"关闭页面时出错: {close_error}")
        return False



async def main():
    global message
    message = 'serv00&ct8自动化脚本运行\n'

    accounts = [
        {'username': 'user1', 'password': 'passwd1', 'panel': 'panelx.serv00.com'},
        {'username': 'user2', 'password': 'passwd2', 'panel': 'panelx.serv00.com'}
        # 可以添加更多账号
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        for account in accounts:
            username = account['username']
            password = account['password']
            panel = account['panel']

            serviceName = 'ct8' if 'ct8' in panel else 'serv00'
            is_logged_in = await login(username, password, panel, browser) # 传递 browser 对象

            if is_logged_in:
                now_utc = format_to_iso(datetime.utcnow())
                now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
                success_message = f'{serviceName}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！'
                message += success_message + '\n'
                print(success_message)
            else:
                message += f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。\n'
                print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

            delay = random.randint(1000, 8000)
            await delay_time(delay)

        await browser.close() # 任务完成关闭浏览器

    message += f'所有{serviceName}账号登录完成！'
    # await send_telegram_message(message)
    print(f'所有{serviceName}账号登录完成！')


# async def send_telegram_message(message):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {
#         'chat_id': TELEGRAM_CHAT_ID,
#         'text': message,
#         'reply_markup': {
#             'inline_keyboard': [
#                 [
#                     {
#                         'text': '问题反馈❓',
#                         'url': 'https://bing.com'
#                     }
#                 ]
#             ]
#         }
#     }
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         if response.status_code != 200:
#             print(f"发送消息到Telegram失败: {response.text}")
#     except Exception as e:
#         print(f"发送消息到Telegram时出错: {e}")


if __name__ == '__main__':
    asyncio.run(main())
