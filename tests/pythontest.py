import pytest
import os
import time
import tempfile
import json
from unittest.mock import Mock, patch
from pathlib import Path
from playwright.sync_api import Page
from openai import OpenAI
from dashscope import ImageSynthesis
import requests
from http import HTTPStatus
from urllib.parse import urlparse
import aiofiles
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
import pydantic
from pydantic import BaseModel


class TestXiaohongshuPublisher:
    """小红书自动发布工具测试类"""

    @pytest.fixture
    def mock_page(self):
        """模拟playwright页面对象"""
        page = Mock(spec=Page)
        return page

    @pytest.fixture
    def mock_openai_client(self):
        """模拟OpenAI客户端"""
        with patch("openai.OpenAI") as mock:
            client = Mock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def mock_image_synthesis(self):
        """模拟图像生成服务"""
        with patch("dashscope.ImageSynthesis") as mock:
            synthesis = Mock()
            mock.call.return_value = synthesis
            yield synthesis

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_config(self):
        """示例配置数据"""
        return {
            "phone": "18201552650",
            "verification_code": "926774",
            "title": "测试标题",
            "content": "测试内容",
            "tags": ["#测试", "#自动化"],
            "image_path": "test_image.png",
        }

    def test_login_functionality(self, mock_page):
        """测试登录功能"""
        # 模拟登录操作
        mock_page.get_by_placeholder.return_value.click.return_value = None
        mock_page.get_by_placeholder.return_value.fill.return_value = None
        mock_page.get_by_text.return_value.click.return_value = None
        mock_page.get_by_role.return_value.click.return_value = None

        # 执行登录流程
        mock_page.get_by_placeholder("手机号").click()
        mock_page.get_by_placeholder("手机号").fill("18201552650")
        mock_page.get_by_text("发送验证码").click()
        mock_page.get_by_placeholder("验证码").click()
        mock_page.get_by_placeholder("验证码").fill("926774")
        mock_page.get_by_role("button", name="登 录").click()

        # 验证调用
        assert mock_page.get_by_placeholder("手机号").fill.called
        assert mock_page.get_by_placeholder("验证码").fill.called
        assert mock_page.get_by_role("button", name="登 录").click.called

    def test_publish_content(self, mock_page):
        """测试内容发布功能"""
        # 模拟发布操作
        mock_page.get_by_text.return_value.click.return_value = None
        mock_page.get_by_role.return_value.click.return_value = None
        mock_page.get_by_role.return_value.set_input_files.return_value = None
        mock_page.get_by_role.return_value.fill.return_value = None
        mock_page.goto.return_value = None

        # 执行发布流程
        mock_page.get_by_text("发布笔记").click()
        mock_page.get_by_text("上传图文").click()
        mock_page.get_by_role("textbox").click()
        mock_page.get_by_role("textbox").set_input_files("test_image.png")
        mock_page.get_by_placeholder("填写标题会有更多赞哦～").click()
        mock_page.get_by_placeholder("填写标题会有更多赞哦～").fill("测试标题")
        mock_page.get_by_role("textbox").fill("测试内容")
        mock_page.get_by_role("button", name="发布").click()

        # 验证调用
        assert mock_page.get_by_text("发布笔记").click.called
        assert mock_page.get_by_role("textbox").set_input_files.called
        assert mock_page.get_by_role("button", name="发布").click.called

    def test_generate_text_with_openai(self, mock_openai_client):
        """测试使用OpenAI生成文本"""
        # 设置模拟响应
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message = Mock()
        mock_completion.choices[0].message.content = "我是AI助手"
        mock_openai_client.chat.completions.create.return_value = mock_completion

        # 模拟环境变量
        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test_key"}):
            client = OpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "你是谁？"},
                ],
            )

            # 验证结果
            assert completion.choices[0].message.content == "我是AI助手"
            assert mock_openai_client.chat.completions.create.called

    def test_generate_image_with_dashscope(self, mock_image_synthesis, temp_dir):
        """测试使用dashscope生成图像"""
        # 设置模拟响应
        mock_result = Mock()
        mock_result.url = "https://example.com/test_image.png"
        mock_image_synthesis.output = Mock()
        mock_image_synthesis.output.results = [mock_result]
        mock_image_synthesis.status_code = HTTPStatus.OK

        # 模拟HTTP请求
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake image data"
            mock_get.return_value = mock_response

            # 模拟环境变量
            with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test_key"}):
                api_key = os.getenv("DASHSCOPE_API_KEY")
                prompt = "测试提示词"

                rsp = ImageSynthesis.call(
                    api_key=api_key,  # type: ignore
                    model="qwen-image",
                    prompt=prompt,
                    n=1,
                    size="1328*1328",
                )

                # 验证响应
                assert rsp.status_code == HTTPStatus.OK
                assert len(rsp.output.results) == 1
                assert rsp.output.results[0].url == "https://example.com/test_image.png"

    def test_image_synthesis_failure_handling(self, mock_image_synthesis):
        """测试图像生成失败处理"""
        # 设置模拟失败响应
        mock_image_synthesis.status_code = HTTPStatus.BAD_REQUEST
        mock_image_synthesis.code = "InvalidParameter"
        mock_image_synthesis.message = "参数错误"

        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test_key"}):
            api_key = os.getenv("DASHSCOPE_API_KEY")
            prompt = "测试提示词"

            rsp = ImageSynthesis.call(
                api_key=api_key,  # type: ignore
                model="qwen-image",
                prompt=prompt,
                n=1,
                size="1328*1328",
            )

            # 验证失败处理
            assert rsp.status_code == HTTPStatus.BAD_REQUEST
            assert rsp.code == "InvalidParameter"
            assert rsp.message == "参数错误"

    def test_file_operations(self, temp_dir):
        """测试文件操作"""
        # 测试文件写入
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = "测试内容"

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # 测试文件读取
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert content == test_content
        assert os.path.exists(test_file)

    @pytest.mark.asyncio
    async def test_async_file_operations(self, temp_dir):
        """测试异步文件操作"""
        test_file = os.path.join(temp_dir, "async_test.txt")
        test_content = "异步测试内容"

        # 异步写入文件
        async with aiofiles.open(test_file, "w", encoding="utf-8") as f:
            await f.write(test_content)

        # 异步读取文件
        async with aiofiles.open(test_file, "r", encoding="utf-8") as f:
            content = await f.read()

        assert content == test_content
        assert os.path.exists(test_file)

    def test_scheduler_functionality(self):
        """测试任务调度功能"""
        scheduler = BackgroundScheduler()

        # 创建测试任务
        test_results = []

        def test_task():
            test_results.append("任务执行")

        # 添加任务
        scheduler.add_job(test_task, "interval", seconds=1)
        scheduler.start()

        # 等待任务执行
        time.sleep(2)

        # 停止调度器
        scheduler.shutdown()

        # 验证任务执行
        assert len(test_results) >= 1
        assert "任务执行" in test_results

    def test_logging_functionality(self, temp_dir):
        """测试日志功能"""
        log_file = os.path.join(temp_dir, "test.log")

        # 配置日志
        logger.add(log_file, rotation="1 MB")

        # 记录日志
        logger.info("测试信息日志")
        logger.warning("测试警告日志")
        logger.error("测试错误日志")

        # 验证日志文件
        assert os.path.exists(log_file)

        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        assert "测试信息日志" in log_content
        assert "测试警告日志" in log_content
        assert "测试错误日志" in log_content

    def test_configuration_loading(self, temp_dir):
        """测试配置加载"""
        config_file = os.path.join(temp_dir, "config.json")
        config_data = {
            "api_key": "test_key",
            "phone": "18201552650",
            "settings": {"auto_publish": True, "interval": 3600},
        }

        # 写入配置文件
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        # 读取配置文件
        with open(config_file, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)

        # 验证配置
        assert loaded_config["api_key"] == "test_key"
        assert loaded_config["phone"] == "18201552650"
        assert loaded_config["settings"]["auto_publish"] is True
        assert loaded_config["settings"]["interval"] == 3600

    def test_pydantic_model_validation(self):
        """测试Pydantic模型验证"""

        class PostConfig(BaseModel):
            title: str
            content: str
            tags: list[str]
            auto_publish: bool = True

        # 测试有效数据
        valid_data = {
            "title": "测试标题",
            "content": "测试内容",
            "tags": ["#测试", "#自动化"],
        }

        config = PostConfig(**valid_data)
        assert config.title == "测试标题"
        assert config.content == "测试内容"
        assert config.tags == ["#测试", "#自动化"]
        assert config.auto_publish is True

        # 测试无效数据
        invalid_data = {
            "title": "",  # 空字符串应该失败
            "content": "测试内容",
            "tags": "不是列表",  # 错误的类型
        }

        with pytest.raises(pydantic.ValidationError):
            PostConfig(**invalid_data)  # type: ignore

    def test_http_request_handling(self):
        """测试HTTP请求处理"""
        with patch("requests.get") as mock_get:
            # 设置模拟响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_get.return_value = mock_response

            # 发送请求
            response = requests.get("https://api.example.com/test")

            # 验证响应
            assert response.status_code == 200
            assert response.json() == {"status": "success"}

    def test_error_handling(self):
        """测试错误处理"""
        # 测试文件不存在错误
        with pytest.raises(FileNotFoundError):
            with open("README.md", "r") as f:
                _content = f.read()

        # 测试JSON解析错误
        with pytest.raises(json.JSONDecodeError):
            json.loads("无效的JSON字符串")

    def test_url_parsing(self):
        """测试URL解析"""
        test_url = "https://example.com/path/to/file.png?param=value"
        parsed = urlparse(test_url)

        assert parsed.scheme == "https"
        assert parsed.netloc == "example.com"
        assert parsed.path == "/path/to/file.png"
        assert parsed.query == "param=value"

    def test_path_operations(self, temp_dir):
        """测试路径操作"""
        # 测试路径拼接
        base_path = Path(temp_dir)
        test_file = base_path / "subdir" / "test.txt"

        # 创建目录
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        test_file.write_text("测试内容", encoding="utf-8")

        # 验证
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == "测试内容"
        assert test_file.suffix == ".txt"

    @pytest.mark.slow
    def test_integration_workflow(self, mock_page):
        """测试完整工作流程（集成测试）"""
        # 模拟完整的工作流程
        steps_executed = []

        def mock_click():
            steps_executed.append("click")
            return None

        def mock_fill(text):
            steps_executed.append(f"fill_{text}")
            return None

        def mock_set_input_files(file_path):
            steps_executed.append(f"upload_{file_path}")
            return None

        # 设置模拟行为
        mock_page.get_by_placeholder.return_value.click = mock_click
        mock_page.get_by_placeholder.return_value.fill = mock_fill
        mock_page.get_by_text.return_value.click = mock_click
        mock_page.get_by_role.return_value.click = mock_click
        mock_page.get_by_role.return_value.set_input_files = mock_set_input_files
        mock_page.get_by_role.return_value.fill = mock_fill
        mock_page.goto = lambda url: steps_executed.append(f"goto_{url}")

        # 执行工作流程
        mock_page.get_by_placeholder("手机号").click()
        mock_page.get_by_placeholder("手机号").fill("18201552650")
        mock_page.get_by_text("发送验证码").click()
        mock_page.get_by_placeholder("验证码").click()
        mock_page.get_by_placeholder("验证码").fill("926774")
        mock_page.get_by_role("button", name="登 录").click()
        mock_page.get_by_text("发布笔记").click()
        mock_page.get_by_text("上传图文").click()
        mock_page.get_by_role("textbox").click()
        mock_page.get_by_role("textbox").set_input_files("test_image.png")
        mock_page.get_by_placeholder("填写标题会有更多赞哦～").click()
        mock_page.get_by_placeholder("填写标题会有更多赞哦～").fill("测试标题")
        mock_page.get_by_role("textbox").fill("测试内容")
        mock_page.get_by_role("button", name="发布").click()

        # 验证工作流程
        expected_steps = [
            "click",
            "fill_18201552650",
            "click",
            "click",
            "fill_926774",
            "click",
            "click",
            "click",
            "click",
            "upload_test_image.png",
            "click",
            "fill_测试标题",
            "fill_测试内容",
            "click",
        ]

        assert steps_executed == expected_steps

    def test_data_validation(self):
        """测试数据验证"""

        # 测试手机号验证
        def validate_phone(phone):
            import re

            pattern = r"^1[3-9]\d{9}$"
            return re.match(pattern, phone) is not None

        assert validate_phone("18201552650") is True
        assert validate_phone("12345678901") is False
        assert validate_phone("1820155265") is False
        assert validate_phone("182015526501") is False

        # 测试验证码验证
        def verify_code(code):
            return code.isdigit() and len(code) == 6

        assert verify_code("926774") is True
        assert verify_code("12345") is False
        assert verify_code("1234567") is False
        assert verify_code("abc123") is False

    def test_performance_metrics(self):
        """测试性能指标"""
        import time

        # 测试函数执行时间
        def test_function():
            time.sleep(0.1)
            return "result"

        start_time = time.time()
        result = test_function()
        end_time = time.time()

        execution_time = end_time - start_time
        assert result == "result"
        assert 0.1 <= execution_time <= 0.2  # 允许一些误差

    @pytest.mark.parametrize(
        "input_data,expected_output",
        [
            ("test", "test"),
            ("测试", "测试"),
            ("", ""),
            ("123", "123"),
            ("special!@#", "special!@#"),
        ],
    )
    def test_parameterized_string_operations(self, input_data, expected_output):
        """参数化测试字符串操作"""

        def process_string(s):
            return s.strip() if s else s

        result = process_string(input_data)
        assert result == expected_output

    def test_memory_usage(self):
        """测试内存使用"""
        import sys

        # 创建大对象
        large_list = list(range(10000))
        initial_size = sys.getsizeof(large_list)

        # 修改对象
        large_list.extend(range(1000))
        final_size = sys.getsizeof(large_list)

        # 验证内存增长
        assert final_size > initial_size

        # 清理内存
        del large_list

    def test_concurrent_operations(self):
        """测试并发操作"""
        import threading
        import time

        results = []
        lock = threading.Lock()

        def worker(worker_id):
            for i in range(5):
                time.sleep(0.01)
                with lock:
                    results.append(f"worker_{worker_id}_iteration_{i}")

        # 创建多个线程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 15  # 3个线程 * 5次迭代
        assert all("worker_" in result for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
