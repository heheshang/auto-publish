# Makefile for xiaohongshu-auto-publisher

.PHONY: help install-dev format lint clean test

help: ## 显示帮助信息
	@echo "可用的命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev: ## 安装开发依赖
	pip install -e ".[dev]"

format: ## 代码格式化
	ruff format .
	ruff check . --fix

lint: ## 代码检查（不自动修复）
	ruff check .

check: ## 运行所有检查（格式化 + lint）
	ruff format . --check
	ruff check .

clean: ## 清理缓存文件
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .ruff_cache/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

test: ## 运行测试
	pytest

test-coverage: ## 运行测试并生成覆盖率报告
	pytest --cov=src --cov-report=html --cov-report=term

setup: ## 初始化项目环境
	pip install -e ".[dev]"
	@echo "项目环境初始化完成！"

all: format lint test ## 运行完整的检查流程（格式化 + lint + 测试）