import re
import time
import random
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any
from playwright.sync_api import (
    Playwright,
    sync_playwright,
    expect,
    Page,
    BrowserContext,
)


@dataclass
class ZhihuConfig:
    """知乎发布配置"""

    storage_state_path: str = "zhihu_storage_state.json"
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    viewport: Dict[str, int] = None
    slow_mo: int = 100
    timeout: int = 60000
    headless: bool = False

    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}


class HumanSimulator:
    """人类行为模拟器"""

    @staticmethod
    def random_delay(min_seconds: float = 0.3, max_seconds: float = 1.5) -> None:
        """随机延迟"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    @staticmethod
    def human_like_mouse_move(page: Page, locator) -> None:
        """模拟人类鼠标移动"""
        try:
            box = locator.bounding_box()
            if not box:
                return

            # 先移动到元素附近
            page.mouse.move(
                box["x"] + random.uniform(-50, 50),
                box["y"] + random.uniform(-20, 20),
                steps=random.randint(3, 8),
            )
            HumanSimulator.random_delay(0.3, 0.8)

            # 精确移动到元素中心
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            page.mouse.move(center_x, center_y, steps=random.randint(2, 5))
            HumanSimulator.random_delay(0.2, 0.5)
        except Exception as e:
            print(f"鼠标移动模拟失败: {e}")


class ZhihuPublisher:
    """知乎文章发布器"""

    def __init__(self, config: Optional[ZhihuConfig] = None):
        self.config = config or ZhihuConfig()
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.human_sim = HumanSimulator()

    def setup_browser(self, playwright: Playwright) -> None:
        """设置浏览器环境"""
        browser = playwright.chromium.launch(
            headless=self.config.headless, slow_mo=self.config.slow_mo
        )

        context_args = {
            "user_agent": self.config.user_agent,
            "viewport": self.config.viewport,
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "accept_downloads": True,
        }

        # 加载存储的登录状态
        if os.path.exists(self.config.storage_state_path):
            context_args["storage_state"] = self.config.storage_state_path

        self.context = browser.new_context(**context_args)
        self.page = self.context.new_page()

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.page.url.startswith("https://www.zhihu.com/creator")

    def handle_login(self) -> bool:
        """处理登录流程"""
        try:
            self.page.goto(
                "https://www.zhihu.com/signin?next=%2Fcreator",
                wait_until="networkidle",
                timeout=self.config.timeout,
            )

            if self.is_logged_in():
                return True

            # 点击登录按钮
            login_button = self.page.get_by_role("button", name="登录/注册", exact=True)
            self.human_sim.human_like_mouse_move(self.page, login_button)
            login_button.click()

            self.page.wait_for_load_state("networkidle")
            self.human_sim.random_delay(2, 4)

            # 处理登录弹窗
            self._handle_login_modal()

            # 等待用户处理验证码
            print("请手动处理验证码，完成后按Enter继续...")
            input()

            # 等待登录完成
            self.page.wait_for_url(
                "https://www.zhihu.com/creator", timeout=self.config.timeout
            )

            # 保存登录状态
            self.context.storage_state(path=self.config.storage_state_path)
            return True

        except Exception as e:
            print(f"登录失败: {e}")
            return False

    def _handle_login_modal(self) -> None:
        """处理登录弹窗"""
        try:
            modal = self.page.locator(".Modal")
            if modal.is_visible():
                self.human_sim.human_like_mouse_move(self.page, modal)
                modal.click(position={"x": 85, "y": 127})
                self.human_sim.random_delay(3, 5)
        except Exception as e:
            print(f"处理登录弹窗失败: {e}")

    def fill_title(self, title: str) -> bool:
        """填写标题"""
        try:
            title_input = self.page.get_by_placeholder("请输入标题（最多 100 个字）")
            self.human_sim.human_like_mouse_move(self.page, title_input)
            title_input.click()
            title_input.fill(title)
            return True
        except Exception as e:
            print(f"填写标题失败: {e}")
            return False

    def fill_content(self, content: str) -> bool:
        """填写内容"""
        try:
            content_locator = (
                self.page.locator("div")
                .filter(has_text=re.compile(r"^请输入正文$"))
                .nth(1)
            )
            self.human_sim.human_like_mouse_move(self.page, content_locator)
            content_locator.click()

            content_input = self.page.get_by_role("textbox").nth(1)
            self.human_sim.human_like_mouse_move(self.page, content_input)
            content_input.fill(content)
            return True
        except Exception as e:
            print(f"填写内容失败: {e}")
            return False

    def upload_cover(self, image_path: str) -> bool:
        """上传封面图片"""
        try:
            if not os.path.exists(image_path):
                print(f"封面图片不存在: {image_path}")
                return False

            cover_label = self.page.locator("label").filter(has_text="添加文章封面")
            self.human_sim.human_like_mouse_move(self.page, cover_label)
            cover_label.set_input_files(image_path)
            return True
        except Exception as e:
            print(f"上传封面失败: {e}")
            return False

    def toggle_gift_setting(self) -> bool:
        """切换送礼物设置"""
        try:
            gift_label = self.page.locator("label").filter(has_text="开启送礼物")
            self.human_sim.human_like_mouse_move(self.page, gift_label)
            gift_label.get_by_role("img").click()
            return True
        except Exception as e:
            print(f"切换送礼物设置失败: {e}")
            return False

    def confirm_and_publish(self) -> bool:
        """确认并发布"""
        try:
            confirm_button = self.page.get_by_role("button", name="确定")
            self.human_sim.human_like_mouse_move(self.page, confirm_button)
            confirm_button.click()

            publish_button = self.page.get_by_role("button", name="发布")
            self.human_sim.human_like_mouse_move(self.page, publish_button)
            publish_button.click()
            return True
        except Exception as e:
            print(f"发布失败: {e}")
            return False

    def publish_article(self, title: str, content: str, cover_image_path: str) -> bool:
        """发布文章"""
        try:
            # 跳转到创作页面
            self.page.goto(
                "https://zhuanlan.zhihu.com/write", timeout=self.config.timeout
            )

            # 填写标题
            if not self.fill_title(title):
                return False

            # 填写内容
            if not self.fill_content(content):
                return False

            # 上传封面
            if cover_image_path and os.path.exists(cover_image_path):
                self.upload_cover(cover_image_path)

            # 切换送礼物设置
            self.toggle_gift_setting()

            # 确认并发布
            return self.confirm_and_publish()

        except Exception as e:
            print(f"文章发布失败: {e}")
            return False

    def run(
        self,
playwright: Playwright,
        title: str,
        content: str,
        cover_image_path: str = "",
    ) -> bool:
        """运行发布流程"""
        try:
            self.setup_browser(playwright)

            # 处理登录
            if not self.is_logged_in():
                if not self.handle_login():
                    return False

            # 发布文章
            return self.publish_article(title, content, cover_image_path)

        except Exception as e:
            print(f"运行失败: {e}")
            return False
        finally:
            if self.context:
                self.context.close()


def main():
    """主函数"""
    # 配置参数
    config = ZhihuConfig()

    # 文章内容
    article_title = "标题标题标题标题标题标题标题标题标题标题标题标题"
    article_content = "内容内容内容内容内容内容内容内容内容内容内容内容内容内容····"
    cover_image = "78bb0f81-242c-4388-81fc-4581364efd09-1.png"

    # 创建发布器并运行
    publisher = ZhihuPublisher(config)

    with sync_playwright() as playwright:
        success = publisher.run(playwright, article_title, article_content, cover_image)
        if success:
            print("文章发布成功！")
        else:
            print("文章发布失败！")


if __name__ == "__main__":
    main()
