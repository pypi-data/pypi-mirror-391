# 🚀 Publishing Ready!

你的 `prisma-web3-py` 包已经完全准备好发布到 PyPI！

---

## ✅ 已完成的准备工作

### 1. 包配置文件
- ✅ `setup.py` - 包安装配置
- ✅ `pyproject.toml` - 现代 Python 项目配置
- ✅ `MANIFEST.in` - 包含文件清单
- ✅ `requirements.txt` - 依赖列表
- ✅ `LICENSE` - MIT 许可证
- ✅ `__version__` - 版本号已添加到 `__init__.py`

### 2. 发布工具
- ✅ `publish_to_pypi.sh` - 手动发布脚本
- ✅ `.github/workflows/publish.yml` - GitHub Actions 自动发布

### 3. 发布文档
- ✅ `PYPI_SETUP_GUIDE.md` - PyPI 完整配置指南（**⭐ 从这里开始**）
- ✅ `VERSION_MANAGEMENT.md` - 版本管理指南
- ✅ `PUBLISHING_CHECKLIST.md` - 发布前检查清单
- ✅ `CHANGELOG.md` - 变更日志

### 4. 代码和文档
- ✅ 8 个完整的数据模型
- ✅ Repository 模式实现
- ✅ 完整的使用文档
- ✅ 示例代码

---

## 🎯 接下来的步骤

你已经注册了 PyPI 账号，接下来按照以下步骤发布：

### 方式 1: 手动发布（推荐首次）

#### 第 1 步：创建 PyPI API Token

1. 登录 https://pypi.org
2. 进入 Account settings → API tokens
3. 点击 "Add API token"
4. Token 名称: `prisma-web3-py-publish`
5. 作用域: **Entire account** （首次发布必须选这个）
6. 创建并**立即复制保存** token（格式: `pypi-AgEIcHlwaS5vcmc...`）

**重要**: Token 只显示一次，离开页面后无法再查看！

#### 第 2 步：配置本地认证（可选）

如果想让脚本自动使用 token：

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE
EOF

chmod 600 ~/.pypirc
```

把 `pypi-YOUR-API-TOKEN-HERE` 替换成你的实际 token。

#### 第 3 步：运行发布脚本

```bash
cd /Users/qinghuan/Documents/code/prisma-web3/python

# 运行发布脚本
./publish_to_pypi.sh
```

脚本会引导你完成：
1. 检查 git 状态
2. 清理旧构建
3. 构建包
4. 验证包质量
5. 可选：先发布到 TestPyPI 测试
6. 发布到 PyPI

如果没有配置 `~/.pypirc`，会提示输入：
- Username: `__token__`
- Password: 你的 PyPI token

#### 第 4 步：验证发布

```bash
# 等待几分钟后测试安装
python -m venv test_env
source test_env/bin/activate

pip install prisma-web3-py
python -c "import prisma_web3_py; print(f'✓ Installed version: {prisma_web3_py.__version__}')"

deactivate
rm -rf test_env
```

访问查看你的包: https://pypi.org/project/prisma-web3-py/

---

### 方式 2: 自动发布（GitHub Actions）

自动发布需要配置 GitHub Secret。

#### 第 1 步：创建 PyPI API Token

（与手动发布的第 1 步相同）

#### 第 2 步：添加 GitHub Secret

1. 打开 GitHub 仓库: https://github.com/your-username/prisma-web3
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **"New repository secret"**
4. 配置:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: 粘贴你的 PyPI token（完整的 `pypi-...` 字符串）
5. 点击 **"Add secret"**

#### 第 3 步：推送 Git Tag 触发发布

```bash
cd /Users/qinghuan/Documents/code/prisma-web3/python

# 确保所有更改已提交
git add .
git commit -m "chore: ready for release v0.1.0"
git push origin main

# 创建并推送 tag（自动触发发布）
git tag v0.1.0
git push origin v0.1.0
```

#### 第 4 步：监控发布进度

1. 访问 GitHub Actions: https://github.com/your-username/prisma-web3/actions
2. 查看 "Publish Python Package to PyPI" workflow
3. 等待完成（通常 2-5 分钟）

#### 第 5 步：验证

- PyPI 页面: https://pypi.org/project/prisma-web3-py/
- GitHub Release: https://github.com/your-username/prisma-web3/releases

---

## 📋 发布前检查清单

在运行发布脚本或推送 tag 前，确保：

- [ ] **所有代码已提交**: `git status` 显示干净
- [ ] **在 main 分支**: `git branch --show-current`
- [ ] **版本号正确**: 检查 `setup.py`、`pyproject.toml`、`__init__.py`
- [ ] **CHANGELOG.md 已更新**: 记录了版本变更
- [ ] **文档是最新的**: README.md 等
- [ ] **PyPI Token 已创建**: 并且正确保存
- [ ] **测试通过**: 基本功能可以运行

详细检查清单: [PUBLISHING_CHECKLIST.md](PUBLISHING_CHECKLIST.md)

---

## 🆘 遇到问题？

### 常见问题快速解决

#### 1. 认证错误 `403 Invalid authentication`

**解决**:
- 确认 token 以 `pypi-` 开头
- Username 必须是 `__token__`
- 检查 token 作用域是否正确

#### 2. 包名已存在 `The name is already in use`

**解决**:
- 访问 https://pypi.org/project/prisma-web3-py/ 确认
- 如果不是你的包，需要改名

#### 3. 版本号错误 `File already exists`

**解决**:
- PyPI 不允许重新上传相同版本
- 必须更新版本号后重新发布

#### 4. GitHub Actions 没有触发

**解决**:
- 检查 workflow 文件路径: `.github/workflows/publish.yml`
- 确认 tag 格式: `v0.1.0` （必须以 `v` 开头）
- 确认推送了 tag: `git push origin v0.1.0`

### 完整故障排除指南

查看 [PYPI_SETUP_GUIDE.md](PYPI_SETUP_GUIDE.md) 的第 5 节。

---

## 📚 文档导航

| 文档 | 用途 | 优先级 |
|------|------|--------|
| **PYPI_SETUP_GUIDE.md** | PyPI 完整配置和发布指南 | ⭐⭐⭐ |
| **PUBLISHING_CHECKLIST.md** | 发布前逐项检查清单 | ⭐⭐⭐ |
| **VERSION_MANAGEMENT.md** | 版本号管理和更新流程 | ⭐⭐ |
| **CHANGELOG.md** | 版本变更记录模板 | ⭐⭐ |
| **publish_to_pypi.sh** | 自动化发布脚本 | ⭐⭐⭐ |

---

## 💡 后续版本发布

首次发布成功后，后续发布会更简单：

### 更新项目特定 Token（推荐）

首次发布后，创建项目特定的 token 更安全：

1. 登录 PyPI
2. 创建新 token，作用域选择: **Project: prisma-web3-py**
3. 更新 GitHub Secret `PYPI_API_TOKEN`
4. 更新 `~/.pypirc` (如果有)

### 发布新版本

```bash
# 1. 更新代码和版本号
vim setup.py pyproject.toml prisma_web3_py/__init__.py

# 2. 更新 CHANGELOG.md
vim CHANGELOG.md

# 3. 提交
git add .
git commit -m "chore: bump version to 0.2.0"
git push origin main

# 4. 推送 tag（自动发布）
git tag v0.2.0
git push origin v0.2.0
```

---

## 🎉 准备好了！

你现在有两个选择：

1. **手动发布** - 运行 `./publish_to_pypi.sh`
2. **自动发布** - 推送 git tag `git push origin v0.1.0`

**建议**: 首次发布使用手动方式，熟悉流程后再使用自动发布。

---

## 📖 详细指南

从这里开始: [PYPI_SETUP_GUIDE.md](PYPI_SETUP_GUIDE.md)

这个指南包含：
- PyPI 账号注册详细步骤
- API Token 创建和配置
- GitHub Actions 设置
- 故障排除
- 安全最佳实践
- 所有相关链接

---

**祝发布顺利！** 🚀

有任何问题，查看文档或参考 PyPI 官方文档: https://packaging.python.org/
