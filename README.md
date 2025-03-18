# 易班发帖脚本

## 简介

本脚本通过husky-spider-utils库进行编写, 登录部分基于selenium(点选验证码需要手动操作), 发帖部分基于requests

## 操作教程

1. 下载源代码, 并使用如下命令配置环境:
   ```bash
   pip install -r requirements.txt
   ```
2. 按照selenium要求配置相关driver(默认使用firefox, 也支持chrome和edge). 配置结束后需要在driver_type="firefox"
   中修改成对应driver
3. 申请deepseek apikey, 有能力的也可以自己修改ai_model文件, 输出结果必须严格按照如下:
    ```json
    {
       "title": "",
       "content": "" 
    }
   ```
4. 修改s_yi_ban_post.py 输入自己的用户名与密码
    ```python
    if __name__ == '__main__':
        # 第一个参数填账号, 第二个参数填密码, 第三个参数填电脑已配的selenium(支持chrome,firefox,edge)
        yiban = SyiBan("", "", driver_type="firefox")
        # 第一个参数填DeepSeek apikey(可去官网申请) post_type使用类型-板块 比如学院发帖(计算机科学与技术学院)就是 学院-计算机科学与技术学院 post_board是类型 比如 默认板块 校园大杂烩 title_pre是标题前缀
        # post_type 和 post_board的填写均需与官网靠齐
        yiban.post("", post_type="学校-西南科技大学", post_board="默认板块",
                   title_pre="【计算机科学与技术学院】")
    ```
5. 在验证码跳出后完成点选并在控制台回车
6. 等待进程结束, 打开同目录下output.txt中包含有需要提交的时间、标题、链接