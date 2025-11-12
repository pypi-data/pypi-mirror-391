import requests
from bs4 import BeautifulSoup


def get_xiaohongshu_article(note_id):
    """
    Get xiaohongshu's article.
    :param note_id: xiaohongshu's note id, you can get it from share link.
    :return: none
    """

    # configuration parameter
    base_url = "https://www.xiaohongshu.com/"
    article_url = base_url + 'explore/' + note_id

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': "abRequestId=8b30bb9c-2f3a-5427-9363-8273cdd3aab0; xsecappid=xhs-pc-web; a1=190807ce210fx3akmc3ql9vtrb1ikxp68iq997v9e50000971385; webId=8b6f487960b42513e6d748b8979da1ac; gid=yj8Y8Wf84WY8yj8Y8WSdJ3Why8iCq0T6SqA1Ajdjh9FDyj283TCUKj888jWyqY28D8YqiiSS; webBuild=4.25.1; web_session=040069b4c2785d678d4ec755a7344b22e9977a; unread={%22ub%22:%22668223a5000000001e013305%22%2C%22ue%22:%22667f272e000000001f0068e0%22%2C%22uc%22:25}; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=713ab3f9-04b2-46bc-a8b0-3ef1dc2a0399; acw_tc=2a9731a22c64601a2ae0f0f92eefddfaba71eeb8576c9ca5928017173ced5e1e"
    }

    # 获取文章内容
    response = requests.get(url=article_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # 使用find_all方法查找所有的meta标签
    meta_tags = soup.find_all("meta")

    # 遍历meta标签列表，并提取其content属性的值
    for meta in meta_tags:
        if meta.get("content") is not None and meta.get("name") is not None:
            match meta.get("name"):
                case "og:title": print("标题："+meta.get("content"))
                case "keywords": print("关键词："+meta.get("content"))
                case "description": print("描述："+meta.get("content"))
                case "og:xhs:note_comment": print("评论："+meta.get("content"))
                case "og:xhs:note_like": print("喜欢："+meta.get("content"))
                case "og:xhs:note_collect": print("收藏："+meta.get("content"))


def get_xiaohongshu_comment(note_id):
    """
    Get xiaohongshu's article comment.
    :param note_id: xiaohongshu's note id, you can get it from share link.
    :return: none
    """

    # configuration parameter
    comment_url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id=" + note_id + "&cursor=&top_comment_id=&image_formats=jpg,webp,avif"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': "abRequestId=76f237d2-fcbb-5e1d-9fe4-c1dd11fb3d14; a1=1964ce0e88efp7cug36dbia0k83qslj1s19t1yz0550000203684; webId=bdbf795996515e33d51154f1d514ee4c; gid=yjK4Sd8ij2MWyjK4Sd8dYyvuYdiUWS7kqKfDj82308TYq928AM1Vyy888J8qKY48Y42DK0JS; web_session=040069b4c2785d678d4e7804363a4b8d2d29c0; acw_tc=0a00d1a617519577861218875e5733eb0ff6036d9c0ecab40fd3a246974628; webBuild=4.72.0; unread={%22ub%22:%2268634bca000000001c030d46%22%2C%22ue%22:%2268501360000000000f038bcb%22%2C%22uc%22:23}; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=8c748e9e-55af-45dd-9337-c5553ded46f5; xsecappid=ranchi; loadts=1751959542095"
    }

    # 发送GET请求并获取响应
    response = requests.get(url=comment_url, headers=headers)
    # 读取响应数据
    data = response.json()
    if data.get("success"):
        for comment in data.get("data").get("comments"):
            print("评论："+comment.get("content"))

