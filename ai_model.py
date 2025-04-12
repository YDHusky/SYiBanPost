import json
from openai import OpenAI

class AIModel:
    type = "deepseek"
    ds_base_url = "https://api.deepseek.com"
    client: OpenAI
    sys_prompt = """
    你需要以一个大学生的身份，写一篇宣传中国传统节日的文章。请随机选择具体节日（如春节/中秋/端午等），并随机从历史起源、传统习俗、现代意义或文化故事中选取阐述角度。按照json格式给出结果，标题直接写出。
    样例输入:
    帮我写一篇文章
    样例输出:
    {
        "title": "题目",
        "content": "内容"
    }
    """
    message = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": "帮我写一篇文章"}]

    def __init__(self, api_key, ai_type="deepseek"):
        self.init_type(ai_type)
        self.client_init(api_key, ai_type)

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

if __name__ == '__main__':
    ai = AIModel("")
    ai.chat()