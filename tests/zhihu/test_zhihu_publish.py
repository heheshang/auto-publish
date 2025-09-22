import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import random
import os  # 新增：用于处理存储状态文件


def run(playwright: Playwright) -> None:
    # 新增：使用持久化上下文保存登录状态，减少重复登录
    storage_state_path = "zhihu_storage_state.json"
    context_args = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # 更新为较新版本Chrome UA
        "viewport": {"width": 1920, "height": 1080},
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
    page.goto("https://www.zhihu.com/signin?next=%2Fcreator", wait_until="networkidle")

    # 新增：检查是否已登录，如果已登录则跳过登录流程
    if not page.url.startswith("https://www.zhihu.com/creator"):
        login_button = page.get_by_role("button", name="登录/注册", exact=True)
        human_like_mouse_move(page, login_button)
        login_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(random.uniform(2, 4))

        # 处理登录弹窗 - 这里假设需要手动处理验证码
        modal = page.locator(".Modal")
        if modal.is_visible():
            human_like_mouse_move(page, modal)
            modal.click(position={"x": 85, "y": 127})
            time.sleep(random.uniform(3, 5))

        # 验证码处理提示
        print("请手动处理验证码，完成后按Enter继续...")
        input()  # 等待用户手动处理验证码

        # 等待登录完成并跳转到创作中心
        page.wait_for_url("https://www.zhihu.com/creator", timeout=60000)
        # 保存登录状态
        context.storage_state(path=storage_state_path)

    # 后续发布流程代码...
    page.goto("https://zhuanlan.zhihu.com/write", timeout=60000)
    human_like_mouse_move(page, page.get_by_placeholder("请输入标题（最多 100 个字）"))
    page.get_by_placeholder("请输入标题（最多 100 个字）").click()
    page.get_by_placeholder("请输入标题（最多 100 个字）").fill(
        "标题标题标题标题标题标题标题标题标题标题标题标题"
    )
    human_like_mouse_move(
        page, page.locator("div").filter(has_text=re.compile(r"^请输入正文$")).nth(1)
    )
    page.locator("div").filter(has_text=re.compile(r"^请输入正文$")).nth(1).click()
    human_like_mouse_move(page, page.get_by_role("textbox").nth(1))
    page.get_by_role("textbox").nth(1).fill(
        "内容内容内容内容内容内容内容内容内容内容内容内容内容内容····"
    )
    human_like_mouse_move(page, page.locator("label").filter(has_text="添加文章封面"))
    # page.locator("label").filter(has_text="添加文章封面").click()
    page.locator("label").filter(has_text="添加文章封面").set_input_files(
        "78bb0f81-242c-4388-81fc-4581364efd09-1.png"
    )
    human_like_mouse_move(page, page.locator("label").filter(has_text="开启送礼物"))
    page.locator("label").filter(has_text="开启送礼物").get_by_role("img").click()
    human_like_mouse_move(page, page.get_by_role("button", name="确定"))
    page.get_by_role("button", name="确定").click()
    human_like_mouse_move(page, page.get_by_role("button", name="发布"))
    page.get_by_role("button", name="发布").click()


with sync_playwright() as playwright:
    run(playwright)
