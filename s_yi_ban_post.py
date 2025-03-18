import time
from datetime import datetime

from husky_spider_utils import SeleniumSession
from loguru import logger


class SyiBan:
    base_url = "https://www.yiban.cn/login?go=https%3A%2F%2Fwww.yiban.cn%2F"

    def __init__(self, username, password, driver_type="firefox"):
        self.session = SeleniumSession(selenium_init_url=self.base_url, driver_type=driver_type)
        self.username = username
        self.password = password
        self.login()
        time.sleep(1)

    def login(self):
        self.session.send_key("#account-txt", self.username)
        self.session.send_key("#password-txt", self.password)
        self.session.click("#login-btn")
        self.session.on_input("完成验证码后回车继续:")
        self.session.selenium_get("https://www.yiban.cn/")

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

    def post(self, ds_api_key, post_type="学校-西南科技大学", post_board="默认板块",
             title_pre="【计算机科学与技术学院】"):
        from ai_model import AIModel
        logger.info("AI描写文章中...")
        ai = AIModel(ds_api_key)
        res = ai.chat()
        title = title_pre + res['title']
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
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(f"标题: {title}\n时间: {formatted_time}\n链接: {post['url']}")
            return post
        else:
            logger.error(f"{res.json()['message']}")


if __name__ == '__main__':
    # 第一个参数填账号, 第二个参数填密码, 第三个参数填电脑已配的selenium(支持chrome,firefox,edge)
    yiban = SyiBan("", "", driver_type="firefox")
    # 第一个参数填DeepSeek apikey(可去官网申请) post_type使用类型-板块 比如学院发帖(计算机科学与技术学院)就是 学院-计算机科学与技术学院 post_board是类型 比如 默认板块 校园大杂烩 title_pre是标题前缀
    # post_type 和 post_board的填写均需与官网靠齐
    yiban.post("", post_type="学校-西南科技大学", post_board="默认板块",
               title_pre="【计算机科学与技术学院】")
