# PyPI Setup Guide

完整的 PyPI 发布配置指南

---

## 目录

1. [PyPI 账号设置](#1-pypi-账号设置)
2. [API Token 配置](#2-api-token-配置)
3. [GitHub Actions 配置](#3-github-actions-配置)
4. [首次发布](#4-首次发布)
5. [故障排除](#5-故障排除)

---

## 1. PyPI 账号设置

### 1.1 注册 PyPI 账号

1. **访问 PyPI**
   - 生产环境: https://pypi.org/account/register/
   - 测试环境: https://test.pypi.org/account/register/

2. **填写注册信息**
   - Username (用户名)
   - Email (邮箱)
   - Password (密码)

3. **验证邮箱**
   - 检查收件箱
   - 点击验证链接
   - 完成邮箱验证

4. **启用双因素认证 (2FA) - 强烈推荐**
   - Settings → Account security → 2FA
   - 使用 Google Authenticator 或类似应用
   - 保存恢复代码

### 1.2 TestPyPI 账号 (可选但推荐)

TestPyPI 是独立的测试环境，强烈建议注册用于测试发布：

1. 访问 https://test.pypi.org/account/register/
2. 使用与 PyPI 相同或不同的用户名注册
3. 验证邮箱

**注意**: TestPyPI 和 PyPI 是完全独立的系统，需要分别注册。

---

## 2. API Token 配置

### 2.1 创建 PyPI API Token

API Token 比密码更安全，是推荐的认证方式。

#### 步骤：

1. **登录 PyPI**
   - 访问 https://pypi.org

2. **进入 API tokens 页面**
   - 点击右上角用户名
   - Account settings
   - API tokens (左侧菜单)
   - 或直接访问: https://pypi.org/manage/account/token/

3. **创建新 Token**
   - 点击 "Add API token"

   **Token 名称**: `prisma-web3-py-github-actions` (或其他描述性名称)

   **作用域选择**:
   - **Entire account** - 所有项目（首次发布必选，因为项目还不存在）
   - **Project: prisma-web3-py** - 仅此项目（项目存在后可用，更安全）

4. **保存 Token**
   - 点击 "Add token"
   - **立即复制并保存 token**（格式: `pypi-AgEIcHlwaS5vcmc...`）
   - ⚠️ **重要**: Token 只显示一次，离开页面后无法再查看！
   - 保存到安全的地方（密码管理器）

#### Token 作用域说明

| 作用域 | 适用场景 | 安全性 | 首次发布 |
|--------|----------|--------|----------|
| Entire account | 发布多个包 | 较低 | ✅ 必须 |
| Project: prisma-web3-py | 仅此包 | 高 | ❌ 项目已存在后才能使用 |

**建议流程**:
1. 首次发布使用 "Entire account" token
2. 发布成功后，创建 "Project: prisma-web3-py" token
3. 替换 GitHub Secret 中的 token

### 2.2 创建 TestPyPI API Token (可选)

如果要在 TestPyPI 测试：

1. 登录 https://test.pypi.org
2. 进入 https://test.pypi.org/manage/account/token/
3. 创建 token（作用域选择 "Entire account"）
4. 保存 token

---

## 3. GitHub Actions 配置

### 3.1 添加 PyPI Token 到 GitHub Secrets

1. **打开你的 GitHub 仓库**
   - 访问 https://github.com/your-username/prisma-web3

2. **进入 Settings**
   - 点击仓库页面的 "Settings" 标签

3. **进入 Secrets 设置**
   - 左侧菜单: Secrets and variables → Actions

4. **添加新 Secret**
   - 点击 "New repository secret"

   **配置项:**
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: 粘贴你的 PyPI token (完整的 `pypi-...` 字符串)

   - 点击 "Add secret"

5. **（可选）添加 TestPyPI Token**
   - 点击 "New repository secret"
   - **Name**: `TEST_PYPI_API_TOKEN`
   - **Value**: 你的 TestPyPI token

### 3.2 验证 GitHub Actions Workflow

确认以下文件存在并配置正确：

**`.github/workflows/publish.yml`**

```yaml
name: Publish Python Package to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    # ... 其他步骤 ...

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

**关键配置:**
- `TWINE_USERNAME: __token__` - 固定值，使用 token 认证
- `TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}` - 引用 GitHub Secret

### 3.3 GitHub Actions 权限设置

确保 GitHub Actions 有正确的权限：

1. **Settings** → **Actions** → **General**
2. **Workflow permissions**:
   - 选择 "Read and write permissions"
   - 勾选 "Allow GitHub Actions to create and approve pull requests"
3. 点击 "Save"

---

## 4. 首次发布

### 4.1 手动发布 (推荐首次使用)

手动发布可以更好地控制流程，适合首次发布：

```bash
cd /Users/qinghuan/Documents/code/prisma-web3/python

# 1. 确保代码已提交
git status

# 2. 运行发布脚本
./publish_to_pypi.sh
```

脚本会：
1. ✅ 检查 git 分支和状态
2. 🧹 清理旧的构建文件
3. 📦 构建包
4. ✔️ 验证包质量
5. 🧪 可选: 上传到 TestPyPI 测试
6. 🚀 上传到 PyPI

**首次运行时的认证:**
- 如果配置了 `~/.pypirc`，会自动使用
- 否则会提示输入:
  - Username: `__token__`
  - Password: 你的 PyPI token

### 4.2 自动发布 (GitHub Actions)

配置完成后，自动发布非常简单：

```bash
cd /Users/qinghuan/Documents/code/prisma-web3/python

# 1. 确保所有更改已提交
git add .
git commit -m "chore: prepare release 0.1.0"
git push origin main

# 2. 创建并推送 tag
git tag v0.1.0
git push origin v0.1.0
```

推送 tag 后，GitHub Actions 会自动：
1. 🏗️ 构建包
2. ✅ 验证包
3. 📤 上传到 PyPI
4. 📝 创建 GitHub Release

### 4.3 验证发布成功

1. **检查 PyPI**
   ```
   https://pypi.org/project/prisma-web3-py/
   ```

2. **测试安装**
   ```bash
   python -m venv test_env
   source test_env/bin/activate

   pip install prisma-web3-py
   python -c "import prisma_web3_py; print(prisma_web3_py.__version__)"

   deactivate
   rm -rf test_env
   ```

3. **检查 GitHub Release**
   ```
   https://github.com/your-username/prisma-web3/releases
   ```

---

## 5. 故障排除

### 5.1 认证问题

#### 错误: `403 Invalid or non-existent authentication information`

**可能原因:**
1. Token 不正确或已过期
2. Token 作用域不够
3. GitHub Secret 配置错误

**解决方案:**
```bash
# 1. 验证 token 格式
echo $PYPI_API_TOKEN | head -c 20
# 应该显示: pypi-AgEIcHlwaS5vcmc

# 2. 创建 ~/.pypirc 测试
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-YOUR-ACTUAL-TOKEN-HERE
EOF

chmod 600 ~/.pypirc

# 3. 测试上传
twine upload dist/*
```

#### 错误: `Username/Password authentication is no longer supported`

**解决方案:**
- 确保使用 token 认证
- Username 必须是 `__token__`
- Password 是完整的 token (以 `pypi-` 开头)

### 5.2 包名问题

#### 错误: `The name 'prisma-web3-py' is already in use`

**可能原因:**
1. 包名已被其他人注册
2. 你之前已经上传过

**解决方案:**
```bash
# 1. 检查 PyPI 是否存在
open https://pypi.org/project/prisma-web3-py/

# 2. 如果是你的包，使用新版本号
# 3. 如果不是，需要更改包名
```

#### 错误: `File already exists`

**原因**: 尝试重新上传相同版本

**解决方案:**
```bash
# 1. 更新版本号
vim setup.py pyproject.toml

# 2. 清理并重新构建
rm -rf dist/
python -m build

# 3. 重新上传
twine upload dist/*
```

### 5.3 版本号问题

#### 错误: `Version mismatch! setup.py has 0.1.0 but tag is v0.2.0`

**解决方案:**
```bash
# 确保所有文件版本一致
grep "version" setup.py pyproject.toml prisma_web3_py/__init__.py

# 更新不一致的文件
vim setup.py
vim pyproject.toml
```

### 5.4 GitHub Actions 问题

#### Workflow 没有触发

**检查清单:**
1. Workflow 文件路径正确: `.github/workflows/publish.yml`
2. Tag 格式正确: `v0.1.0` (以 `v` 开头)
3. GitHub Actions 已启用
4. 推送 tag 到远程: `git push origin v0.1.0`

#### Secret 未找到

**错误**: `Error: secrets.PYPI_API_TOKEN is not defined`

**解决方案:**
1. 确认 Secret 名称完全匹配 (区分大小写)
2. 重新添加 Secret
3. 删除并重新推送 tag:
   ```bash
   git tag -d v0.1.0
   git push origin :refs/tags/v0.1.0
   git tag v0.1.0
   git push origin v0.1.0
   ```

### 5.5 构建问题

#### 错误: `ModuleNotFoundError: No module named 'setuptools'`

**解决方案:**
```bash
pip install --upgrade pip setuptools wheel build
python -m build
```

#### 错误: `error: invalid command 'bdist_wheel'`

**解决方案:**
```bash
pip install wheel
python -m build
```

### 5.6 权限问题

#### 错误: `Permission denied`

**解决方案:**
```bash
# 检查文件权限
ls -la ~/.pypirc
# 应该是 -rw------- (600)

# 修复权限
chmod 600 ~/.pypirc
```

---

## 6. 本地 PyPI 配置

### 创建 ~/.pypirc (可选)

如果你想在本地保存 PyPI 凭据（不推荐在共享环境）：

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN
EOF

chmod 600 ~/.pypirc
```

**安全提示:**
- 不要将 `.pypirc` 提交到 git
- 在 `.gitignore` 中添加:
  ```
  .pypirc
  ```

---

## 7. 发布流程总结

### 首次发布流程

```bash
# 1. 准备
cd /Users/qinghuan/Documents/code/prisma-web3/python
git status  # 确保无未提交更改

# 2. 检查配置
- [ ] PyPI 账号已注册
- [ ] PyPI token 已创建
- [ ] GitHub Secret PYPI_API_TOKEN 已添加
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新

# 3. 运行检查清单
# 参考 PUBLISHING_CHECKLIST.md

# 4. 手动发布 (首次推荐)
./publish_to_pypi.sh

# 5. 验证
pip install prisma-web3-py
python -c "import prisma_web3_py; print(prisma_web3_py.__version__)"

# 6. 创建 git tag
git tag v0.1.0
git push origin v0.1.0
```

### 后续发布流程

```bash
# 1. 更新代码和版本号
# 2. 测试
# 3. 推送 tag - 自动触发发布
git tag v0.2.0
git push origin v0.2.0

# 4. 等待 GitHub Actions 完成
# 5. 验证发布
```

---

## 8. 安全最佳实践

### ✅ 推荐做法

1. **使用 API Token** - 不要使用密码
2. **项目级别 Token** - 发布后创建项目特定 token
3. **GitHub Secrets** - 使用 Secrets 存储 token，不要硬编码
4. **启用 2FA** - PyPI 账号启用双因素认证
5. **定期轮换 Token** - 每 3-6 个月更新 token
6. **限制权限** - 使用最小权限原则

### ❌ 避免做法

1. **不要分享 Token** - Token 等同于密码
2. **不要提交 Token** - 检查 `.pypirc` 不在版本控制中
3. **不要在日志输出 Token** - 配置 GitHub Actions 时注意
4. **不要使用账号密码** - 已废弃且不安全

---

## 9. 相关文档

- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - 版本管理指南
- [PUBLISHING_CHECKLIST.md](PUBLISHING_CHECKLIST.md) - 发布检查清单
- [CHANGELOG.md](CHANGELOG.md) - 变更日志
- [publish_to_pypi.sh](publish_to_pypi.sh) - 发布脚本

---

## 10. 快速参考

### PyPI 相关链接

- **PyPI Production**: https://pypi.org
- **PyPI Test**: https://test.pypi.org
- **Token Management**: https://pypi.org/manage/account/token/
- **Package Page**: https://pypi.org/project/prisma-web3-py/

### 常用命令

```bash
# 构建
python -m build

# 检查
twine check dist/*

# 上传到 PyPI
twine upload dist/*

# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    prisma-web3-py

# 从 PyPI 安装
pip install prisma-web3-py

# 查看版本
pip show prisma-web3-py
```

---

**准备好发布了吗？按照上面的步骤开始吧！** 🚀
