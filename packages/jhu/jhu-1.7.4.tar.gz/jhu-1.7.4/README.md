# 安装
```bash
# 通过uv安装
uv add jhu

# 按需安装依赖包, 目前有 auth,security,orm和webhook
uv add 'jhu[auth]'
```

# 使用
## Auth模块
> [!NOTE]
> Auth模块为第三方应用登录的便捷工具,目前支持飞书和钉钉

```python
from jhu.auth import DingTalk,FeiShu

if __name__ == "__main__":
    ding_ak = "ding_ak"
    ding_sk = "ding_sk"
    d = DingTalk(ding_ak, ding_sk)
    # 设置redirect_uri
    d.create_login_url("http://localhost:9000/")
    # 这里的code从redirect_uri返回的code中获取
    d.get_user_info("968999a21b9b38c794d230c5d80742bc")

    feishu_ak = "feishu_ak"
    feishu_sk = "feishu_sk"
    f = FeiShu(feishu_ak, feishu_sk)
    # 设置redirect_uri
    f.create_login_url("http://localhost:9000/")
    # 这里的code从redirect_uri返回的code中获取
    f.get_user_info("b8ag458bd0f54712be8c6877273ce415")
```