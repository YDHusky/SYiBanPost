import json
from openai import OpenAI


class AIModel:
    type = "deepseek"
    ds_base_url = "https://api.deepseek.com"
    client: OpenAI

    def __init__(self, api_key, topic, ai_type="deepseek"):
        self.init_type(ai_type)
        self.client_init(api_key, ai_type)
        self.sys_prompt = """
    你需要以一个大学生的身份，写一篇文章，内容必须正能量。请根据""" + topic + """为主题写一篇文章。按照json格式给出结果，标题直接写出(标题5-15字)。
    样例输入:
    帮我写一篇文章
    样例输出:
    {
        "title": "题目",
        "content": "内容"
    }
    """
        self.message = [{"role": "system", "content": self.sys_prompt}, {"role": "user", "content": "帮我写一篇文章"}]

    def init_type(self, ai_type="deepseek"):
        if self.type == "deepseek":
            match ai_type:
                case "deepseek":
                    self.type = "deepseek"
                case _:
                    self.type = "deepseek"

    def client_init(self, api_key, ai_type="deepseek"):
        match ai_type:
            case "deepseek":
                self.client = OpenAI(api_key=api_key, base_url=self.ds_base_url)
            case _:
                self.client = OpenAI(api_key=api_key, base_url=self.ds_base_url)

    def chat(self):
        res = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.message,
            response_format={
                'type': 'json_object'
            },
            temperature=0.9
        )
        return json.loads(res.choices[0].message.content)
