"""
整合钉钉,飞书第三方网页登录
"""
from enum import IntEnum
from urllib.parse import quote_plus
from requests import post, get


class AuthType(IntEnum):
    # 钉钉
    DINGTALK = 0
    # 飞书
    FEISHU = 1


def get_dingtalk_user_info(ak: str, sk: str, auth_code: str) -> dict:
    """获取钉钉用户信息

    Args:
        ak: 钉钉应用的AppKey, 如:ding1cincjju0rvrl6c5
        sk: 钉钉应用的SecurityKey,如:w4dkdOyB3iy9lMv7VstUqnVHgj3f-WmbUGiHj2X-HsE4Yp_Fn0pHrQ_deI1oy1Nl
        auth_code: 钉钉扫码得到的auth_code, 如:e8ce805bbd5434168292f75c11832eac
    """
    # 1.获取access_token
    ACCESS_TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
    data = {"clientId": ak, "clientSecret": sk,
            "code": auth_code, "grantType": "authorization_code"}

    with post(ACCESS_TOKEN_URL, json=data) as rsp:
        access_token = rsp.json().get("accessToken", "")

    # 2.获取用户信息
    USER_INFO_URL = "https://api.dingtalk.com/v1.0/contact/users/me"
    headers = {"x-acs-dingtalk-access-token": f"{access_token}"}

    with get(USER_INFO_URL, headers=headers) as rsp:
        result = rsp.json()

    return result


def get_feishu_user_info(ak: str, sk: str, auth_code: str) -> dict:
    """获取飞书的用户信息

    Args:
        ak: 飞书应用的AppKey,如:cli_3a2c007d00da5bdc
        sk: 飞书应用的SecurityKey,如:BZUG0yREh8XJfl14teRZ6rr0HeFhr2I5
        auth_code: 飞书扫码得到的auth_code , 如:5c0t8bf1efe14119a00c5555ee066053
    """
    # 1.获取app_access_token
    app_access_token_data = {"app_id": ak, "app_secret": sk}
    APP_ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    with post(APP_ACCESS_TOKEN_URL, json=app_access_token_data) as rsp:
        app_access_token = rsp.json().get("app_access_token", "")

    # 2.获取access_token
    ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    access_token_headers = {"Authorization": f"Bearer {app_access_token}"}
    access_token_data = {"grant_type": "authorization_code", "code": auth_code}
    with post(ACCESS_TOKEN_URL, headers=access_token_headers, json=access_token_data) as rsp:
        user_access_token = rsp.json()["data"]["access_token"]

    # 3.获取用户信息
    USER_INFO_URL = "https://open.feishu.cn/open-apis/authen/v1/user_info"
    user_access_token_headers = {
        "Authorization": f"Bearer {user_access_token}"}
    with get(USER_INFO_URL, headers=user_access_token_headers) as rsp:
        result = rsp.json()
    return result


class ThridAuthBase:
    def __init__(self, ak: str, sk: str, auth_type: AuthType) -> None:
        """三方扫码登录初始化

        Args:
            ak:str,应用的appkey
            sk:str,应用的secretkey
            auth_type:AuthType,应用类型,当前支持 钉钉:AuthType.DINGTALK,飞书:AuthType.FEISHU
        """
        self._auth_type = auth_type
        self._ak = ak
        self._sk = sk

        # 回调函数注册
        match(auth_type):
            case AuthType.DINGTALK:
                # 钉钉三方登录网页地址拼接
                self._prefix_url = "https://login.dingtalk.com/oauth2/challenge.htm"
                self.get_user_info_fn = get_dingtalk_user_info
            case AuthType.FEISHU:
                # 飞书三方登录网页地址拼接
                self._prefix_url = "https://open.feishu.cn/open-apis/authen/v1/authorize"
                self.get_user_info_fn = get_feishu_user_info
            case _:
                raise TypeError("认证类型类型错误")

    @property
    def ak(self) -> str:
        return self._ak

    @property
    def sk(self) -> str:
        return self._sk

    @property
    def auth_type(self) -> AuthType:
        return self._auth_type

    @property
    def prefix_url(self) -> str:
        return self._prefix_url

    def create_login_url(self, redirect_uri: str, state: str | None = None) -> str:
        """生成三方扫码登录的url地址

        Args:
            redirect_uri: 扫码通过后,回调的地址
            state: 生成地址用的state

        Returns:
            三方扫码登录的url地址
        """

        match(self.auth_type):
            case AuthType.DINGTALK:
                state = state or "JHU_DINGTALK"
                data = {
                    "redirect_uri": quote_plus(redirect_uri),
                    "client_id": self.ak,
                    "response_type": "code",
                    "scope": "openid",
                    "state": state,
                    "prompt": "consent"
                }
            case AuthType.FEISHU:
                state = state or "JHU_FEISHU"
                data = {
                    "redirect_uri": quote_plus(redirect_uri),
                    "app_id": self.ak,
                    "scope": "contact:user.phone:readonly",
                    "state": state
                }
            case _:
                raise TypeError("认证类型类型错误")

        query_params = '&'.join([f"{k}={data[k]}" for k in data])
        url = self.prefix_url+'?'+query_params
        return url

    def get_user_info(self, auth_code: str) -> dict:
        """获取三方扫码得到的用户信息

        Args:
            auth_code:str,三方登录连接返回的auth_code

        Returns:
            用户的json信息
        """
        return self.get_user_info_fn(self.ak, self.sk, auth_code)


class DingTalk(ThridAuthBase):
    def __init__(self, ak: str, sk: str) -> None:
        """钉钉三方登录

        Args:
            ak: 钉钉应用的AppKey, 如:ding1cincjju0rvrl6c5
            sk: 钉钉应用的SecurityKey,如:w4dkdOyB3iy9lMv7VstUqnVHgj3f-WmbUGiHj2X-HsE4Yp_Fn0pHrQ_deI1oy1Nl
        """
        super().__init__(ak, sk, AuthType.DINGTALK)


class FeiShu(ThridAuthBase):
    def __init__(self, ak: str, sk: str) -> None:
        """飞书三方登录

        Args:
            ak: 飞书应用的AppKey,如:cli_3a2c007d00da5bdc
            sk: 飞书应用的SecurityKey,如:BZUG0yREh8XJfl14teRZ6rr0HeFhr2I5
        """
        super().__init__(ak, sk, AuthType.FEISHU)


if __name__ == "__main__":
    ding_ak = "ding_ak"
    ding_sk = "ding_sk"
    d = DingTalk(ding_ak, ding_sk)
    d.create_login_url("http://localhost:9000/")
    # 这里的code从redirect_url返回的code中获取
    d.get_user_info("968999a21b9b38c794d230c5d80742bc")

    feishu_ak = "feishu_ak"
    feishu_sk = "feishu_sk"
    f = FeiShu(feishu_ak, feishu_sk)
    f.create_login_url("http://localhost:9000/")
    # 这里的code从redirect_url返回的code中获取
    f.get_user_info("b8ag458bd0f54712be8c6877273ce415")
