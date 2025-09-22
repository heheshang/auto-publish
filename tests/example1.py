import re
import time
import os
from playwright.sync_api import sync_playwright
from openai import OpenAI
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis


class Detail:
    def __init__(self, title, left, right, content, file_name):
        self.title = title
        self.left = left
        self.right = right
        self.content = content
        self.file_name = file_name


def generate_text():
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv(
            "DASHSCOPE_API_KEY"
        ),  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {"role": "system", "content": "你是一个具有诗情画意的对联生成器。"},
            {
                "role": "user",
                "content": "请为我生成一副对联，内容要典雅庄重，适合悬挂在大厅之中 输出对联上联 下联和横批 20字以内。",
            },
        ],
    )
    msg1 = completion.choices[0].message.content
    if msg1 is not None:
        print("对联：%s" % msg1)
        left = msg1.split("\n")[0].split("：")[1]
        right = msg1.split("\n")[1].split("：")[1]
        title = msg1.split("\n")[2].split("：")[1]
        detail = Detail(title, left, right, "", "")

    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {"role": "system", "content": "你是一个具有诗情画意的对联生成器。"},
            {
                "role": "user",
                "content": "请根据对联上联：%s下联：%s横批：%s 描述对联具体意境。只写意境不体现对联内容。100字以内。"
                % (detail.left, detail.right, detail.title),
            },
        ],
    )
    msg2 = completion.choices[0].message.content
    detail.content = msg2
    print("意境：%s" % msg2)
    return detail


def generate_image(detail: Detail):

    prompt = """一副典雅庄重的对联悬挂于大厅之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，
    
    上联：%s
    下联：%s
    横批：%s
    字体飘逸，中间挂有一副中国风的画作,根据内容:%s进行创作
      """ % (
        detail.left,
        detail.right,
        detail.title,
        detail.content,
    )

    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key = os.getenv("DASHSCOPE_API_KEY")
    file_name = ""
    print("----同步调用，请等待任务执行----")
    rsp = ImageSynthesis.call(
        api_key=api_key,  # type: ignore
        model="qwen-image",
        prompt=prompt,
        n=1,
        size="1328*1328",  # pyright: ignore[reportArgumentType]
    )
    print("response: %s" % rsp)
    if rsp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图片
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open("./%s" % file_name, "wb+") as f:
                f.write(requests.get(result.url).content)
                print("图片已保存至当前目录，文件名：%s" % file_name)
                print("----同步调用结束----")
                detail.file_name = file_name
    else:
        print(
            "同步调用失败, status_code: %s, code: %s, message: %s"
            % (rsp.status_code, rsp.code, rsp.message)
        )

    return detail


def main(detail: Detail):
    with sync_playwright() as p:
        # 启动浏览器
        # browser = p.chromium.launch(headless=False)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 导航到目标页面
        page.goto("https://creator.xiaohongshu.com/login?selfLogout=true")
        time.sleep(2)
        page.locator("img").click()
        time.sleep(2)
        page.screenshot(path="screenshot-webkit.png")
        # 登录小红书

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
            page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
            time.sleep(5)
            # 上传图文内容
            page.get_by_text("上传图文").nth(1).click()
            time.sleep(5)
            # page1.get_by_role("textbox").click()
            # time.sleep(5)
            # page1.screenshot(path="screenshot-webkit.png")
            page.get_by_role("textbox").set_input_files(detail.file_name)
            print("setInputFiles")
            time.sleep(5)
            # 填写标题和内容
            page.get_by_placeholder("填写标题会有更多赞哦～").click()
            print("click placeholder")
            time.sleep(5)
            page.get_by_placeholder("填写标题会有更多赞哦～").fill(detail.title)
            print("填写标题会有更多赞哦")
            time.sleep(5)
            page.get_by_role("textbox").nth(1).click()
            print("click TEXTBOX")
            time.sleep(5)
            page.get_by_role("textbox").nth(1).fill(detail.content)
            print("11112222")
            time.sleep(5)

            # 发布内容
            page.get_by_role("button", name="发布").click()
            time.sleep(5)
        # ---------------------
        context.close()

        # 关闭浏览器
        browser.close()


if __name__ == "__main__":
    # detail= generate_text()
    # detail = generate_image(detail)
    detail = Detail("1", "2", "3", "3", "4aa4bccc-c197-453b-b034-56b6890a9998-1.png")
    main(detail)
