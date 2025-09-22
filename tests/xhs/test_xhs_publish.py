import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import random
import os  # 新增：用于处理存储状态文件
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("playwright").setLevel(logging.DEBUG)
logger = logging.getLogger()


def run(playwright: Playwright) -> None:
    # 新增：使用持久化上下文保存登录状态，减少重复登录
    storage_state_path = "xhs_storage_state.json"
    context_args = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # 更新为较新版本Chrome UA
        "viewport": {"width": 800, "height": 600},
        "device_scale_factor": 1,
        "is_mobile": False,
        "has_touch": False,
        "accept_downloads": True,
    }

    # 新增：如果存在存储状态文件，则加载它
    if os.path.exists(storage_state_path):
        context_args["storage_state"] = storage_state_path

    browser = playwright.chromium.launch(
        headless=False, slow_mo=100
    )  # 新增：slow_mo放慢操作速度
    context = browser.new_context(**context_args)

    # 新增：模拟真实用户的鼠标移动
    def human_like_mouse_move(page, locator):
        box = locator.bounding_box()
        if box:
            # 随机移动到元素附近，再精确点击
            page.mouse.move(
                box["x"] + random.uniform(-50, 50),
                box["y"] + random.uniform(-20, 20),
                steps=random.randint(3, 8),
            )
            time.sleep(random.uniform(0.3, 0.8))
            page.mouse.move(
                box["x"] + box["width"] / 2,
                box["y"] + box["height"] / 2,
                steps=random.randint(2, 5),
            )
            time.sleep(random.uniform(0.2, 0.5))

    page = context.new_page()

    # 修改：使用更智能的等待方式
    page.goto(
        "https://creator.xiaohongshu.com/login?selfLogout=true",
        wait_until="networkidle",
    )

    # 新增：检查是否已登录，如果已登录则跳过登录流程
    if (
        page.locator("div")
        .filter(has_text=re.compile(r"^发布笔记$"))
        .nth(1)
        .is_visible()
    ):
        logger.info("开始登陆")
        # 处理登录流程
        page.locator("img").click()
        page.goto("https://creator.xiaohongshu.com/login?selfLogout=true")
        # 等待登录完成并跳转到首页
        page.wait_for_url("https://creator.xiaohongshu.com/new/home", timeout=60000)
        # 保存登录状态
        context.storage_state(path=storage_state_path)
    logger.info("已登录")
    # 后续发布流程代码...
    page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
    logger.info("已进入发布页面")
    page.get_by_text("上传图文").nth(1).click()
    logger.info("上传图文")
    # human_like_mouse_move(page, page.locator("div").filter(has_text=re.compile(r"^发布笔记$")).nth(1))
    # page.locator("div").filter(has_text=re.compile(r"^发布笔记$")).nth(1).click()
    human_like_mouse_move(page, page.get_by_role("textbox"))
    page.get_by_role("textbox").set_input_files(
        "eb3de882-8cf6-4830-9307-e3f28888e54e-1.png"
    )
    logger.info("已上传图片")
    human_like_mouse_move(page, page.get_by_placeholder("填写标题会有更多赞哦～"))
    page.get_by_placeholder("填写标题会有更多赞哦～").click()
    page.get_by_placeholder("填写标题会有更多赞哦～").fill("aerqawerqwer")
    logger.info("已填写标题")
    human_like_mouse_move(page, page.get_by_role("textbox").nth(1))
    page.get_by_role("textbox").nth(1).click()
    page.get_by_role("textbox").nth(1).fill("adfadsfadfasdf")
    logger.info("已填写内容")
    human_like_mouse_move(page, page.get_by_role("button", name="发布"))
    page.get_by_role("button", name="发布").click()
    logger.info("已经发布")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
