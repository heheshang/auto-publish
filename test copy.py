import asyncio

from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)

    context = await browser.new_context()
    page = await context.new_page()
    await page.get_by_placeholder("手机号").click()
    await page.get_by_placeholder("手机号").fill("18201552650")
    await page.get_by_text("发送验证码").click()
    await page.get_by_placeholder("验证码").click()
    await page.get_by_placeholder("验证码").fill("926774")
    await page.get_by_role("button", name="登 录").click()
    await page.get_by_text("发布笔记").click()
    await page.get_by_text("上传图文").nth(1).click()
    await page.get_by_role("textbox").click()
    await page.get_by_role("textbox").set_input_files("20250811.png")
    await page.get_by_text("智能标题").click()
    await page.get_by_text("无损转有损真的不会失真吗？？？").click()
    await page.get_by_placeholder("填写标题会有更多赞哦～").click()
    await page.get_by_placeholder("填写标题会有更多赞哦～").click()
    await page.get_by_role("textbox").nth(1).click()
    await page.get_by_role("textbox").nth(1).fill("sfgsfgsfgsdfg")
    await page.get_by_text("#无后顾之忧").first.click()
    await page.get_by_text("#数据恢复#小白也能懂#要具体问题具体分析#完美解决方案 展开 #数据恢复#小白也能懂#要具体问题具体分析#完美解决方案#希望大数据推给有需要的人#谁来教教我#").click()
    await page.get_by_text("#希望大数据推给有需要的人").first.click()
    await page.get_by_role("button", name="发布").click()
    await page.goto("https://creator.xiaohongshu.com/publish/success?source&bind_status=not_bind&__debugger__=&proxy=")
    await page.goto("https://creator.xiaohongshu.com/publish/publish?source=&published=true")

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
