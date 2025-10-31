# 进京证自动续签工具

一个基于Python的进京证自动续签工具，支持多用户、自动登录、状态监控和消息推送。

## 免责声明

本工具仅供学习和研究使用，请遵守相关法律法规。使用本工具产生的任何后果由使用者自行承担。

## 功能特性

- 🚗 **自动续签**：自动检查进京证状态，在到期前自动续签
- 🔐 **自动登录**：通过北京通账号自动获取认证token
- 👥 **多用户支持**：支持配置多个用户，批量处理
- 📱 **消息推送**：支持多种推送方式（Apprise支持的所有平台），及时通知续签结果
- 🔒 **安全存储**：敏感信息加密存储，保护用户隐私
- 📊 **状态监控**：实时监控进京证状态、剩余天数和申请次数
- 🛡️ **错误处理**：完善的异常处理和重试机制


## 安装说明

### 1. 克隆项目

```bash
git clone https://github.com/fichas/cross_beijing.git
cd cross_beijing
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 下载密钥文件

项目使用加密存储敏感信息，需要下载密钥文件：

```bash
# 下载密钥文件到项目根目录
curl -L -o url_key.key https://github.com/fichas/cross_beijing/releases/download/v0.0.1/url_key.key
```

## 配置说明

### 1. 编辑配置文件

编辑 `config.json` 文件，配置用户信息：

```json
{
    "url": "Z0FBQUFBQnBBUlhCSFFYZmwyazlObTFmMldZZFpBMW5NU2JxRl9BZDd4cC1paDdUMXVYZkNITlhERDZOZmZmbUtKWFZlalhCSjRqVFlXUWNJeUd1VjFUMnR3dmZhMmJCdk9XVWdqUGtTOW04Y1ZlNXdsZ01EelE2SFo1b2pXV2wyR2syQ21kSkRRSko=",
    "users": [
        {
            "name": "张三",
            "auth": "",
            "bjt_phone": "你的北京通手机号",
            "bjt_pwd": "你的北京通密码",
            "entry_type": "六环内",
            "notify_urls": [
                "bark://api.day.app/your_bark_token",
                "tgram://bottoken/ChatID"
            ]
        },
        {
            "name": "李四",
            "auth": "",
            "bjt_phone": "另一个北京通手机号",
            "bjt_pwd": "另一个北京通密码",
            "entry_type": "六环外",
            "notify_urls": [
                "email://user:pass@gmail.com",
                "slack://TokenA/TokenB/TokenC/"
            ]
        }
    ]
}
```

### 2. 配置参数说明

- `name`: 用户名称（用于日志标识）
- `auth`: 认证token（程序会自动获取，无需手动填写）
- `bjt_phone`: 北京通手机号
- `bjt_pwd`: 北京通密码
- `notify_urls`: 推送服务URL列表（支持多种推送方式）
- `entry_type`: 进京证类型（六环内/六环外）
### 3. 推送服务配置

#### 3.1 支持的推送方式

项目支持多种推送方式，通过 `notify_urls` 配置：

- **Bark**: `bark://api.day.app/your_token` 或 `barks://api.day.app/your_token`
- **Telegram**: `tgram://bottoken/ChatID`
- **Email**: `email://user:pass@smtp.gmail.com:587`
- **Slack**: `slack://TokenA/TokenB/TokenC/` 或 `slack://TokenA/TokenB/TokenC/Channel`
- **Discord**: `discord://webhook_id/webhook_token`
- **Webhook**: `webhook://your_webhook_url`
- **钉钉**: `dingtalk://token/`
- **企业微信**: `wxteams://Token`
- **更多方式**: 详见 [Apprise官方文档](https://github.com/caronc/apprise)

#### 3.2 配置示例

```json
"notify_urls": [
    "barks://api.day.app/your_bark_token",
    "email://your_email@gmail.com:your_app_password@smtp.gmail.com:587",
    "discord://webhook_id/webhook_token"
]
```

#### 3.3 获取推送Token

**Bark推送**:
1. 在App Store下载Bark应用
2. 打开应用，复制推送地址中的Token
3. 使用格式: `bark://api.day.app/your_token`


## 使用方法

### 1. 直接运行

```bash
python cross_bj.py
```

### 2. 定时任务

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天上午9点执行）
0 9 * * * cd /path/to/cross_beijing && python cross_bj.py
```

## 工作原理

### 1. 自动登录流程

1. 程序启动时检查用户是否已有认证token
2. 如果没有token，使用北京通账号密码自动登录
3. 获取认证token并保存到配置文件
4. 使用token调用交管局API

### 2. 续签判断逻辑

程序会检查以下条件决定是否需要续签：

- **新车**：没有任何申请记录，直接申请
- **审核通过(生效中)**：剩余天数 ≤ 1天时，提前申请明天的进京证
- **审核中/审核通过(待生效)**：无需申请
- **其他状态**：直接申请当天的进京证

### 3. 申请流程

1. 获取车辆信息
2. 获取用户信息
3. 创建申请表单
4. 提交申请
5. 发送推送通知

## 支持的进京证类型

- **六环内**：适用于六环内行驶的车辆
- **六环外**：适用于六环外行驶的车辆

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 免责声明

本工具仅供学习和研究使用，请遵守相关法律法规。使用本工具产生的任何后果由使用者自行承担。

---

如有问题或建议，请提交 [Issue](https://github.com/fichas/cross_beijing/issues)。

