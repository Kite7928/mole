#!/usr/bin/env python3
"""
wechat-draft-publisher - 一键推送到草稿箱
支持微信公众号API集成、Token智能缓存、封面图上传
"""

import os
import json
import time
import requests
from typing import Dict, Optional, List
from bs4 import BeautifulSoup


class WeChatPublisher:
    """微信公众号草稿发布器"""
    
    # 错误码映射
    ERROR_CODES = {
        40001: "AppSecret错误或者AppSecret不属于这个AppID",
        40002: "不合法的凭证类型",
        40003: "不合法的AppID",
        40164: "调用接口的IP地址不在白名单中",
        41001: "缺少access_token参数",
        42001: "access_token超时，请检查缓存是否正常",
        42002: "refresh_token超时",
        43001: "需要GET请求",
        43002: "需要POST请求",
        43003: "需要HTTPS请求",
        44001: "多媒体文件为空",
        44002: "POST的数据包为空",
        44003: "图文消息内容为空",
        45001: "多媒体文件大小超过限制",
        45002: "消息内容超过限制",
        45003: "标题字段超过限制",
        45004: "描述字段超过限制",
        45005: "链接字段超过限制",
        45006: "图片链接字段超过限制",
        45007: "语音播放时间超过限制",
        45008: "图文消息超过限制",
        45009: "接口调用超过限制",
        45010: "创建菜单个数超过限制",
        45015: "回复时间超过限制",
        45016: "系统分组，不允许修改",
        45017: "分组名字过长",
        45018: "分组数量超过上限",
        45021: "未授权的第三方账号",
        45022: "未授权的第三方账号",
        45024: "账号数量超过限制",
        45025: "未授权的第三方账号",
        45026: "未授权的第三方账号",
        45027: "未授权的第三方账号",
        45028: "未授权的第三方账号",
        45029: "未授权的第三方账号",
        45031: "未授权的第三方账号",
        45032: "未授权的第三方账号",
        45033: "未授权的第三方账号",
        45034: "未授权的第三方账号",
        45035: "未授权的第三方账号",
        45036: "未授权的第三方账号",
        45037: "未授权的第三方账号",
        45038: "未授权的第三方账号",
        45039: "未授权的第三方账号",
        45040: "未授权的第三方账号",
        45041: "未授权的第三方账号",
        45042: "未授权的第三方账号",
        45043: "未授权的第三方账号",
        45044: "未授权的第三方账号",
        45045: "未授权的第三方账号",
        45046: "未授权的第三方账号",
        45047: "未授权的第三方账号",
        45048: "未授权的第三方账号",
        45049: "未授权的第三方账号",
        45050: "未授权的第三方账号",
        45051: "未授权的第三方账号",
        45052: "未授权的第三方账号",
        45053: "未授权的第三方账号",
        45054: "未授权的第三方账号",
        45055: "未授权的第三方账号",
        45056: "未授权的第三方账号",
        45057: "未授权的第三方账号",
        45058: "未授权的第三方账号",
        45059: "未授权的第三方账号",
        45060: "未授权的第三方账号",
        45061: "未授权的第三方账号",
        45062: "未授权的第三方账号",
        45063: "未授权的第三方账号",
        45064: "未授权的第三方账号",
        45065: "未授权的第三方账号",
        45066: "未授权的第三方账号",
        45067: "未授权的第三方账号",
        45068: "未授权的第三方账号",
        45069: "未授权的第三方账号",
        45070: "未授权的第三方账号",
        45071: "未授权的第三方账号",
        45072: "未授权的第三方账号",
        45073: "未授权的第三方账号",
        45074: "未授权的第三方账号",
        45075: "未授权的第三方账号",
        45076: "未授权的第三方账号",
        45077: "未授权的第三方账号",
        45078: "未授权的第三方账号",
        45079: "未授权的第三方账号",
        45080: "未授权的第三方账号",
        45081: "未授权的第三方账号",
        45082: "未授权的第三方账号",
        45083: "未授权的第三方账号",
        45084: "未授权的第三方账号",
        45085: "未授权的第三方账号",
        45086: "未授权的第三方账号",
        45087: "未授权的第三方账号",
        45088: "未授权的第三方账号",
        45089: "未授权的第三方账号",
        45090: "未授权的第三方账号",
        45091: "未授权的第三方账号",
        45092: "未授权的第三方账号",
        45093: "未授权的第三方账号",
        45094: "未授权的第三方账号",
        45095: "未授权的第三方账号",
        45096: "未授权的第三方账号",
        45097: "未授权的第三方账号",
        45098: "未授权的第三方账号",
        45099: "未授权的第三方账号",
        45100: "未授权的第三方账号",
        45101: "未授权的第三方账号",
        45102: "未授权的第三方账号",
        45103: "未授权的第三方账号",
        45104: "未授权的第三方账号",
        45105: "未授权的第三方账号",
        45106: "未授权的第三方账号",
        45107: "未授权的第三方账号",
        45108: "未授权的第三方账号",
        45109: "未授权的第三方账号",
        45110: "未授权的第三方账号",
        -1: "系统繁忙，请稍后重试"
    }
    
    # Token缓存文件路径
    TOKEN_CACHE_FILE = os.path.expanduser("~/.wechat-publisher/token_cache.json")
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化发布器
        
        Args:
            app_id: 微信公众号AppID
            app_secret: 微信公众号AppSecret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
        
        # 确保缓存目录存在
        cache_dir = os.path.dirname(self.TOKEN_CACHE_FILE)
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_access_token(self) -> str:
        """
        获取access_token（带缓存）
        
        Returns:
            access_token字符串
        """
        # 1. 尝试从缓存读取
        if os.path.exists(self.TOKEN_CACHE_FILE):
            try:
                with open(self.TOKEN_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                
                # 检查是否过期（提前5分钟刷新）
                if cache['expire_time'] > time.time() + 300:
                    print(f"使用缓存的access_token")
                    return cache['access_token']
            except Exception as e:
                print(f"读取缓存失败: {e}")
        
        # 2. 缓存失效，重新获取
        print("获取新的access_token...")
        return self._fetch_access_token()
    
    def _fetch_access_token(self) -> str:
        """
        从微信API获取新的access_token
        
        Returns:
            access_token字符串
        """
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'errcode' in data and data['errcode'] != 0:
            error_msg = self.ERROR_CODES.get(data['errcode'], f"未知错误: {data['errcode']}")
            raise Exception(f"获取access_token失败: {error_msg}")
        
        # 保存到缓存
        cache = {
            'access_token': data['access_token'],
            'expire_time': time.time() + data['expires_in']
        }
        
        # 原子写入（防止并发问题）
        temp_file = self.TOKEN_CACHE_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        
        os.replace(temp_file, self.TOKEN_CACHE_FILE)
        
        return data['access_token']
    
    def upload_image(self, image_path: str) -> str:
        """
        上传图片到微信素材库
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            media_id字符串
        """
        access_token = self.get_access_token()
        url = f"{self.base_url}/material/add_material?access_token={access_token}&type=image"
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, files=files)
            data = response.json()
        
        if 'errcode' in data and data['errcode'] != 0:
            error_msg = self.ERROR_CODES.get(data['errcode'], f"未知错误: {data['errcode']}")
            raise Exception(f"上传图片失败: {error_msg}")
        
        print(f"✓ 图片上传成功: {data['media_id']}")
        return data['media_id']
    
    def parse_html(self, html_path: str) -> Dict:
        """
        解析HTML文件，提取标题、摘要、正文
        
        Args:
            html_path: HTML文件路径
            
        Returns:
            包含标题、摘要、正文的字典
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.get_text().strip()
        else:
            title = soup.title.get_text().strip() if soup.title else "未命名文章"
        
        # 限制标题长度（32字节）
        title = title[:32]
        
        # 提取摘要（取前120字节）
        paragraphs = soup.find_all('p')
        if paragraphs:
            summary = paragraphs[0].get_text().strip()
        else:
            summary = soup.get_text().strip()[:120]
        
        # 限制摘要长度（120字节）
        summary = summary[:120]
        
        # 提取正文（去除script和style标签）
        for script in soup(['script', 'style']):
            script.decompose()
        
        content = str(soup)
        
        return {
            'title': title,
            'digest': summary,
            'content': content
        }
    
    def create_draft(self, html_path: str, cover_image_path: Optional[str] = None) -> Dict:
        """
        创建草稿文章
        
        Args:
            html_path: HTML文件路径
            cover_image_path: 封面图片路径（可选）
            
        Returns:
            创建结果
        """
        # 解析HTML
        article_data = self.parse_html(html_path)
        
        # 上传封面图
        thumb_media_id = None
        if cover_image_path and os.path.exists(cover_image_path):
            thumb_media_id = self.upload_image(cover_image_path)
        
        # 构建文章数据
        article = {
            "title": article_data['title'],
            "author": "",  # 可选，限制20字节
            "digest": article_data['digest'],
            "content": article_data['content'],
            "content_source_url": "",  # 可选
            "thumb_media_id": thumb_media_id,
            "show_cover_pic": 1 if thumb_media_id else 0,
            "need_open_comment": 1,  # 是否打开评论
            "only_fans_can_comment": 0  # 是否只有粉丝可以评论
        }
        
        # 调用API创建草稿
        access_token = self.get_access_token()
        url = f"{self.base_url}/draft/add?access_token={access_token}"
        
        payload = {
            "articles": [article]
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if 'errcode' in data and data['errcode'] != 0:
            error_msg = self.ERROR_CODES.get(data['errcode'], f"未知错误: {data['errcode']}")
            raise Exception(f"创建草稿失败: {error_msg}")
        
        print(f"✓ 草稿创建成功！")
        print(f"  媒体ID: {data['media_id']}")
        
        return data
    
    def publish_draft(self, html_path: str, cover_image_path: Optional[str] = None) -> Dict:
        """
        发布文章到草稿箱（完整流程）
        
        Args:
            html_path: HTML文件路径
            cover_image_path: 封面图片路径（可选）
            
        Returns:
            发布结果
        """
        print(f"开始发布文章...")
        
        # 解析HTML
        article_data = self.parse_html(html_path)
        print(f"  标题: {article_data['title']}")
        print(f"  摘要: {article_data['digest']}")
        
        # 创建草稿
        result = self.create_draft(html_path, cover_image_path)
        
        return result


def main():
    """主函数 - 演示用法"""
    # 配置微信公众号信息
    # 需要在微信公众平台获取
    APP_ID = "your_app_id"
    APP_SECRET = "your_app_secret"
    
    # 初始化发布器
    publisher = WeChatPublisher(app_id=APP_ID, app_secret=APP_SECRET)
    
    # 发布文章
    html_file = "./articles/Claude_Sonnet_4.html"
    cover_image = "./articles/Claude_Sonnet_4_cover.png"
    
    if os.path.exists(html_file):
        try:
            result = publisher.publish_draft(html_file, cover_image)
            print(f"\n发布成功！")
        except Exception as e:
            print(f"\n发布失败: {e}")
    else:
        print(f"文件不存在: {html_file}")
        print("请先生成并格式化文章")


if __name__ == "__main__":
    main()