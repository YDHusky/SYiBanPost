import json

from openai import OpenAI


class AIModel:
    type = "deepseek"
    ds_base_url = "https://api.deepseek.com"
    client: OpenAI
    sys_prompt = """
    你需要以一个大学生的身份,写一篇贴近当前实事的文章,需要正能量的文章,文章中心内容随机,需要按照json格式给出结果,标题部分直接给出结果
    样例输入:
    帮我写一篇文章
    样例输出:
    {
        "title": "青春正能量·与时代同行",
        "content": "——2025年大学生书写奋斗篇章站在2025年的春天回望，我们这一代青年正以蓬勃的姿态拥抱时代。无论是返乡实践的热忱、创新创业的激情，还是平凡生活中的点滴坚持，都在诠释着“正能量”的深刻内涵。作为大学生，我们不仅是时代的见证者，更应成为正能量的传播者与践行者。以下结合当前热点与青年行动，分享几点感悟：一、在实践中扎根：用脚步丈量家乡，以行动传递温暖2025年寒假，全国多地开展大学生“返家乡”社会实践，如松原市组织650名学子深入基层，参与政务实践、乡村振兴等活动。他们在社区服务中感受基层治理的温度，在乡村调研中见证发展的脉搏，用实际行动为家乡注入活力11。这种“象牙塔”与“燕归巢”的双向奔赴，正是当代青年责任感的缩影。正如古语所言：“不登高山，不知天之高也；不临深溪，不知地之厚也。”唯有躬身实践，才能将理想化为现实的力量。二、在创新中突破：以智慧点亮未来，用创业书写担当今年3月，湖南省启动首届“金种子杯”大学生创业大赛，面向全球青年发出邀请。赛事设置四大产业赛道，精准对接国家战略需求，为创业者提供资金支持、导师指导和成果转化平台1213。这让我们看到，青春正能量的另一面是敢想敢为的创新精神。正如苏格拉底所说：“世界上最快乐的事，莫过于为理想而奋斗。”无论是攻克技术难题，还是探索商业模式，青年创业者的每一次尝试都在为社会发展注入新鲜血液。三、在平凡中闪光：以微笑传递善意，用坚持铸就品格正能量并非遥不可及，它藏在日常的细节里：对他人多一份关怀：一个真诚的微笑、一次主动的帮助，如网页1所述，“给老师一份赞许，给父母一个拥抱”，便能驱散冷漠的阴霾1。对自己多一份坚持：面对学业压力或生活挫折，铭记网页4中的箴言：“人生的高度，不是你看清了多少事，而是你看轻了多少事”4。保持豁达心态，将困难视为成长的阶梯。对时代多一份信念：如网页2所言，“人生没有多走的路，脚下的每一步都算数”2，每一份努力终将汇成时代的洪流。四、在社会中聚力：政策护航青春，多方共筑梦想当前，从国家到地方，支持青年发展的政策不断加码。例如湖南省推出《支持大学生留湘来湘创业政策指南》，通过创业基金、孵化基地和导师体系为青年铺路12；松原市成立大学生联盟，搭建校地合作桥梁11。这些举措让我们感受到，个人的奋斗离不开社会的托举，而青年的成长也将反哺社会的进步。结语：青春无问西东，奋斗自成芳华2025年的我们，站在科技飞跃与文明交融的时代节点。无论是投身乡村振兴的田野，还是驰骋创新创业的赛场，亦或在平凡岗位上默默耕耘，我们都在用行动定义青春的意义。正如鲁迅先生所言：“愿中国青年都摆脱冷气，只是向上走。”让我们以正能量为帆，以奋斗为桨，在时代的浪潮中破浪前行！"
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
            }
        )
        return json.loads(res.choices[0].message.content)


if __name__ == '__main__':
    ai = AIModel("sk-a18fd3a55eb74a189720403e49f96e0e")
    ai.chat()
