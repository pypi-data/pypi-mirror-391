# 发布到 PyPI 指南

## 📦 构建完成

你的包已经成功构建！文件位于 `dist/` 目录：
- `dicom_tools_mcp_test-1.0.1.tar.gz` (源码包)
- `dicom_tools_mcp_test-1.0.1-py3-none-any.whl` (wheel包)

---

## 🚀 发布步骤

### 步骤 1: 注册 PyPI 账号

1. 访问 [PyPI 官网](https://pypi.org/) 注册账号
2. 访问 [TestPyPI](https://test.pypi.org/) 注册测试账号（可选，用于测试）

### 步骤 2: 配置 API Token

1. 登录 PyPI 账号
2. 进入 Account Settings → API tokens
3. 点击 "Add API token"
4. 命名你的 token（例如：dicom-tools-mcp-upload）
5. 选择 Scope：可以选择 "Entire account" 或特定项目
6. 复制生成的 token（格式：`pypi-AgEIcHlwaS...`）

⚠️ **重要**：Token 只显示一次，请妥善保存！

### 步骤 3: 配置 ~/.pypirc（可选但推荐）

在你的用户目录创建 `.pypirc` 文件：

**Windows**: `C:\Users\你的用户名\.pypirc`

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS...（你的 token）

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS...（你的 TestPyPI token）
```

### 步骤 4: 上传到 TestPyPI（测试，可选）

先测试上传到 TestPyPI：

```powershell
twine upload --repository testpypi dist/*
```

测试安装：
```powershell
pip install --index-url https://test.pypi.org/simple/ dicom-tools-mcp-test
```

### 步骤 5: 上传到正式 PyPI

确认无误后，上传到正式 PyPI：

```powershell
twine upload dist/*
```

如果没有配置 `.pypirc`，会提示输入：
- Username: `__token__`
- Password: 你的 PyPI token

---

## ✅ 上传后验证

### 1. 检查 PyPI 页面
访问：https://pypi.org/project/dicom-tools-mcp-test/

### 2. 测试安装
```powershell
# 创建新的虚拟环境测试
python -m venv test_env
test_env\Scripts\activate
pip install dicom-tools-mcp-test

# 测试运行
dicom-tools-mcp
```

### 3. 使用 uvx 运行（推荐）
```powershell
uvx dicom-tools-mcp-test
```

---

## 🔄 更新版本

当你需要发布新版本时：

### 1. 更新版本号
编辑 `pyproject.toml`：
```toml
version = "1.0.2"  # 递增版本号
```

### 2. 清理旧构建
```powershell
Remove-Item -Recurse -Force dist, build, *.egg-info
```

### 3. 重新构建
```powershell
python -m build
```

### 4. 上传新版本
```powershell
twine upload dist/*
```

---

## 📝 版本号规范（语义化版本）

格式：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向下兼容的新功能
- **PATCH**: 向下兼容的错误修复

示例：
- `1.0.0` → `1.0.1`：bug 修复
- `1.0.1` → `1.1.0`：新功能
- `1.1.0` → `2.0.0`：破坏性变更

---

## 🛠️ 常见问题

### Q1: 上传失败 - 文件已存在
**问题**：`File already exists`
**解决**：PyPI 不允许覆盖已上传的版本，必须递增版本号

### Q2: 包名已被占用
**问题**：`The name 'xxx' is too similar to an existing project`
**解决**：在 `pyproject.toml` 中修改包名

### Q3: 上传速度慢
**问题**：网络连接慢或超时
**解决**：
- 使用代理
- 或者多次尝试 `twine upload dist/* --verbose`

### Q4: Token 认证失败
**问题**：`Invalid or non-existent authentication information`
**解决**：
- 确保 username 是 `__token__`（两个下划线）
- 检查 token 是否包含完整的 `pypi-` 前缀
- Token 是否已过期或被撤销

---

## 📊 包信息

- **包名**: dicom-tools-mcp-test
- **当前版本**: 1.0.1
- **命令**: `dicom-tools-mcp`
- **Python 要求**: >=3.10

---

## 🎯 快速命令参考

```powershell
# 构建
python -m build

# 检查包
twine check dist/*

# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 上传到 PyPI
twine upload dist/*

# 清理
Remove-Item -Recurse -Force dist, build, *.egg-info
```

---

## 📚 相关链接

- [PyPI 官网](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Twine 文档](https://twine.readthedocs.io/)
- [Python 打包指南](https://packaging.python.org/)
- [语义化版本](https://semver.org/lang/zh-CN/)

---

**准备好后，运行以下命令上传：**

```powershell
twine upload dist/*
```
