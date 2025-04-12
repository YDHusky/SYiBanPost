import json
import os.path
import time
from datetime import datetime

import requests
from husky_spider_utils import SeleniumSession
from loguru import logger


class SyiBan:
    base_url = "https://www.yiban.cn/login?go=https%3A%2F%2Fwww.yiban.cn%2F"

    def __init__(self, username, password, driver_type="firefox"):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.yiban.cn",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        self.session = SeleniumSession(selenium_init_url=self.base_url, driver_type=driver_type, headers=headers)
        self.username = username
        self.password = password
        self.login()
        time.sleep(1)

    def login(self):

        captcha_res = self.get_captcha()
        url = "https://www.yiban.cn/login/doLoginAjax"
        keys = self.session.get_element_selector(".login-pr").css("::attr(data-keys)").get()
        key_times = self.session.get_element_selector(".login-pr").css("::attr(data-keys-time)").get()
        self.session.headers.update({
            "smdid": captcha_res['yt']
        })

        def encrypt(password):
            import base64
            from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
            from Crypto.PublicKey import RSA

            rsakey = RSA.importKey(keys)
            cipher = Cipher_pksc1_v1_5.new(rsakey)
            cipher_text = base64.b64encode(cipher.encrypt(password.encode()))
            return cipher_text.decode()

        password = encrypt(self.password)
        payload = {
            "account": self.username,
            "password": password,
            "keysTime": key_times,
            "captcha": "",
            **captcha_res
        }
        res = self.session.post(url=url, data=payload)
        logger.info(res.text)

    def get_captcha(self):
        # 打开新的标签页
        self.session.driver.switch_to.new_window('tab')
        captcha_html_path = os.path.abspath("html/captcha.html")
        self.session.driver.get(f"file:///{captcha_html_path}")
        data = self.session.get_element_selector("#data")
        res = json.loads(data.css("::text").extract_first())
        self.session.driver.switch_to.window(self.session.driver.window_handles[0])
        return res

    def get_token(self):
        res = self.session.post("https://s.yiban.cn/api/security/getToken")
        if res.json()["code"] == "200":
            logger.info(f"{res.json()['message']}")
            return True
        else:
            logger.error(f"{res.json()['message']}")
            logger.error(res.json())
            return False

    def get_token_value(self):
        res = self.session.post("https://s.yiban.cn/api/security/getToken")
        if res.json()["code"] == "200":
            logger.info(f"{res.json()['message']}")
            return res.json()["data"]["csrfToken"]
        else:
            self.login()
            return self.get_token_value()

    def get_post_list(self, offset=0, count=10):
        params = {
            "offset": offset,
            "count": count,
        }
        res = self.session.get("https://s.yiban.cn/api/my/postListForWeb", params=params)
        if res.json()["code"] == "200":
            logger.info(f"{res.json()['message']}")
            logger.debug(res.json())
            return res.json()["data"]
        else:
            logger.error(f"{res.json()['message']}")
            logger.error(res.json())

    def get_all_post_list(self):
        if not self.get_token():
            self.login()
        post_list = []
        data = self.get_post_list()
        post_list.extend(data["list"])
        while data['hasNext']:
            data = self.get_post_list(offset=data['next'])
        return post_list

    def get_post_name(self, title):
        payload = {
            "title": title,
        }
        res = self.session.post("https://s.yiban.cn/api/index/getPostByName", data=payload)
        if res.json()["code"] == "200":
            logger.info(f"{res.json()['message']}")
            return res.json()["data"]['exist']
        else:
            logger.error(f"{res.json()['message']}")
            return False

    def get_my_orgs(self, post_type):
        res = self.session.get("https://s.yiban.cn/api/org/getMyOrgs")
        if res.json()['code'] == "200":
            logger.info(f"{res.json()['message']}")
            args = post_type.split("-")
            for item in res.json()['data']:
                if item['orgTypeName'] == args[0]:
                    for org in item['list']:
                        if org['name'] == args[1]:
                            return org['orgId']
            return res.json()['data'][0]['list'][0]['orgId']
        else:
            logger.error(f"{res.json()['message']}")
            self.login()
            return self.get_my_orgs(post_type)

    def get_board(self, org_id, post_board):
        params = {
            "orgId": org_id,
        }
        res = self.session.get("https://s.yiban.cn/api/board/list", params=params)
        if res.json()["code"] == "200":
            logger.info(f"{res.json()['message']}")
            for item in res.json()['data']:
                if item['name'] == post_board:
                    return item['id']
            return res.json()['data'][0]['id']
        else:
            logger.error(f"{res.json()['message']}")
            self.login()
            return self.get_board(org_id, post_board)

    def get_topic(self):
        url = "https://v1.hitokoto.cn/?c=d"
        res = requests.get(url)
        if res.status_code == 200:
            topic = res.json()["hitokoto"]
        else:
            topic = "随机挑选一个中国节日"
        logger.info(f"文章主题: {topic}")
        return topic

    def post(self, ds_api_key, post_type="学校-西南科技大学", post_board="默认板块",
             title_pre="【计算机科学与技术学院】"):
        from ai_model import AIModel
        logger.info("AI描写文章中...")
        ai = AIModel(ds_api_key, self.get_topic())
        res = ai.chat()
        title = title_pre + res['title']
        if len(title) >= 30:
            title = title[:30]
        content = res['content']
        logger.info(f"文章标题: {title}")
        logger.info(f"文章内容: {content}")
        org_id = self.get_my_orgs(post_type)
        board_id = self.get_board(org_id, post_board)
        while self.get_post_name(title):
            res = ai.chat()
            title = title_pre + res['title']
            content = res['content']
        payload = {
            "channel": [
                {
                    "boardId": board_id,
                    "orgId": org_id
                }
            ],
            "attach": [],
            "content": content,
            "csrfToken": self.get_token_value(),
            "hasVLink": 0,
            "isWeb": 1,
            "summary": "",
            "thumbType": 1,
            "title": title
        }
        res = self.session.post("https://s.yiban.cn/api/post/web", json=payload)
        if res.json()["ncode"] == "6011007":
            logger.warning("[6011007]标题为5-30个字")
            payload['title'] = payload['title'][:25]
            res = self.session.post("https://s.yiban.cn/api/post/web", json=payload)

        if res.json()["ncode"] == "6012042":
            logger.warning("由于发帖频繁，账号被风控，请在浏览器中完成验证码操作!")
            captcha = self.get_captcha()
            ticket = {
                "pass": True,
                "mode": "spatial_select",
                **captcha
            }
            self.session.headers.update({
                "ybticket": json.dumps(ticket, separators=(',', ':')),
                "platform": "yiban_web"
            })
            res = self.session.post("https://s.yiban.cn/api/post/web", json=payload)

        if res.json()['code'] == "200":
            logger.success(f"{res.json()['message']}")
            posts = self.get_post_list(offset=0, count=10)
            post = posts['list'][0]
            logger.success(f"{post['title']}")
            logger.success(f"{post['url']}")
            post_time = float(post['updateTime'])
            dt = datetime.fromtimestamp(post_time)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            logger.success(f"{formatted_time}")
            if not os.path.exists("output.txt"):
                with open("output.txt", "w", encoding="utf-8") as f:
                    f.write("")
            with open("output.txt", "a", encoding="utf-8") as f:
                f.write(f"""
------------------------------------------------------------------------
标题: {title}\n时间: {formatted_time}\n链接: {post['url']}
------------------------------------------------------------------------""")
            return post
        else:
            logger.error(f"{res.json()['message']}")


if __name__ == '__main__':
    # 运行控制逻辑
    try:
        run_times = int(input("请输入脚本运行次数（1-3，默认1）: ") or 1)
        run_times = max(1, min(run_times, 10))  # 强制限制在1-3范围内
    except ValueError:
        run_times = 1
        logger.warning("输入无效，使用默认值1")

    yiban = SyiBan("", "", driver_type="chrome")
    # 带延时的执行循环
    for i in range(run_times):
        logger.info(f"开始第 {i + 1}/{run_times} 次发帖操作")
        yiban.post(
            "",
            post_type="学院-计算机科学与技术学院",
            post_board="默认板块",
            title_pre="【计算机科学与技术学院】"
        )

        # 最后一次不等待
        if i < run_times - 1:
            logger.warning("由于易班发帖限制，70秒后继续下一次发帖...")
            for remaining in range(70, 0, -1):
                logger.info(f"剩余等待时间: {remaining}秒")
                time.sleep(1)
            logger.success("等待结束，继续执行下一个任务")

    logger.success("所有发帖任务已完成！")
