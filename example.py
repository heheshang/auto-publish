import time
import os
from playwright.sync_api import sync_playwright
from openai import OpenAI
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis


def generate_text():
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"), # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': '你是谁？'}
        ]
    )
    print(completion.choices[0].message.content)

def generate_image(prompt:str=""):

    prompt = "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书“义本生知人机同道善思新”，右书“通云赋智乾坤启数高志远”， 横批“智启通义”，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。"

    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key = os.getenv("DASHSCOPE_API_KEY")

    print('----同步调用，请等待任务执行----')
    rsp = ImageSynthesis.call(api_key=api_key,
                            model="qwen-image",
                            prompt=prompt,
                            n=1,
                            size='1328*1328')
    print('response: %s' % rsp)
    if rsp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图片
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open('./%s' % file_name, 'wb+') as f:
                f.write(requests.get(result.url).content)
    else:
        print('同步调用失败, status_code: %s, code: %s, message: %s' %
            (rsp.status_code, rsp.code, rsp.message))




def main():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 导航到目标页面
        page.goto("https://www.xiaohongshu.com/explore")

        # 输入手机号
        # page.get_by_placeholder("输入手机号").click()
        # page.get_by_placeholder("输入手机号").fill("175 0149 3191")
        # page.get_by_text("获取验证码").click()

        # 读取终端输入的验证码
        # input_code = input("请输入验证码或按回车继续:")
        # page.get_by_placeholder("输入验证码").fill(input_code)


        # 登录操作
        # page.locator("form").get_by_role("button", name="登录").click()
        # page.get_by_text("同意并继续").click()


        input_code = input("请扫描二维码")
        if input_code:
        
            # 进入创作中心
            page.get_by_role("button", name="创作中心").click()
            page.locator("#explore-guide-menu use").click()

            # 打开发布页面
            with page.expect_popup() as popup_info:
                page.get_by_role("link", name="发布").click()
            page1 = popup_info.value
            page1.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
            time.sleep(5)

            # 上传图文内容
            page1.get_by_text("上传图文").nth(1).click()
            time.sleep(5)
            page1.get_by_role("textbox").click()
            time.sleep(5)
            page1.screenshot(path="screenshot-webkit.png")
            page1.get_by_role("textbox").set_input_files("screenshot-webkit.png")
            print("setInputFiles")
            time.sleep(5)

            # 填写标题和内容
            page1.get_by_placeholder("填写标题会有更多赞哦～").click()
            print("click placeholder")
            time.sleep(5)
            page1.get_by_placeholder("填写标题会有更多赞哦～").fill("12222")
            print("填写标题会有更多赞哦")
            time.sleep(5)
            page1.get_by_role("textbox").nth(1).click()
            print("click TEXTBOX")
            time.sleep(5)
            page1.get_by_role("textbox").nth(1).fill("11112222")
            print("11112222")
            time.sleep(5)

            # 发布内容
            page1.get_by_role("button", name="发布").click()
            time.sleep(5)

            # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    # main()
    generate_text()
    generate_image()
