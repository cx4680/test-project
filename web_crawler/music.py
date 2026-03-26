#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐列表爬虫脚本
访问 cezame.cn 网站并提取歌曲列表信息
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional


class MusicCrawler:
    """音乐列表爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def fetch_page(self, url: str) -> str:
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return ""
    
    def parse_song_list(self, html: str) -> List[Dict[str, str]]:
        """解析歌曲列表"""
        soup = BeautifulSoup(html, 'html.parser')
        songs = []
        download_buttons = self._extract_download_buttons(soup)

        # 查找歌曲列表容器
        # 根据分析，歌曲信息通常在 .content-area 或类似容器中
        content_area = soup.select_one('.content-area')
        if not content_area:
            content_area = soup

        # 获取所有文本内容并按歌曲分割
        text_content = content_area.get_text('\n', strip=True)

        # 根据页面结构，歌曲信息以"曲名 :"开头，每个歌曲块以"曲名 :"分隔
        # 使用正则表达式分割歌曲条目
        song_pattern = r'曲名\s*:'
        song_starts = [m.start() for m in re.finditer(song_pattern, text_content)]

        if song_starts:
            # 从每个匹配的位置提取歌曲信息
            for i, start in enumerate(song_starts):
                end = song_starts[i+1] if i+1 < len(song_starts) else len(text_content)
                song_info = self._extract_song_info(text_content[start:end])
                if song_info:
                    songs.append(song_info)
        else:
            # 如果没有找到标准格式，尝试其他分割方式
            # 按换行分割并过滤空行
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            songs = self._parse_from_lines(lines)

        # 如果仍然没有找到歌曲，尝试更宽松的分割方式
        if not songs:
            # 按空行分割歌曲条目
            song_blocks = re.split(r'\n\s*\n', text_content)
            for block in song_blocks:
                if block.strip():
                    song_info = self._extract_song_info_from_block(block)
                    if song_info:
                        songs.append(song_info)

        if download_buttons:
            self._merge_download_buttons(songs, download_buttons)

        return songs

    def _extract_download_buttons(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """查找下载按钮信息"""
        if soup is None:
            return []

        download_tags = soup.select('.btntoggle.Tl_download')
        download_buttons: List[Dict[str, str]] = []

        for tag in download_tags:
            button_info: Dict[str, str] = {}
            text = tag.get_text(strip=True)
            if text:
                button_info['text'] = text

            for attr in (
                'href',
                'onclick',
                'data-url',
                'data_url',
                'data-id',
                'data_id',
                'data-media',
                'data_media',
                'data-id_media',
                'data-id-media',
            ):
                if attr in tag.attrs:
                    value = tag.attrs.get(attr)
                    if isinstance(value, list):
                        value = ' '.join(value)
                    if isinstance(value, str):
                        button_info[attr.replace('-', '_')] = value.strip()

            onclick_text = button_info.get('onclick', '')
            match = re.search(r"xajax_tip_download\s*\(\s*['\"]?([^'\"\)]+)", onclick_text)
            if match:
                button_info['download_target'] = match.group(1)

            button_info['html'] = str(tag)
            download_buttons.append(button_info)

        return download_buttons

    def _normalize_code(self, value: Optional[str]) -> Optional[str]:
        """归一化代码或标题，便于匹配下载按钮"""
        if not value:
            return None

        cleaned = re.sub(r'[^0-9a-zA-Z]+', '', value)
        return cleaned.lower() if cleaned else None

    def _merge_download_buttons(self, songs: List[Dict[str, str]], buttons: List[Dict[str, str]]):
        """将下载按钮与歌曲信息关联"""
        if not songs or not buttons:
            return

        button_map: Dict[str, List[Dict[str, str]]] = {}

        for button in buttons:
            candidates = [
                button.get('download_target'),
                button.get('data_id'),
                button.get('data_id_media'),
                button.get('data_media'),
                button.get('data_url'),
                button.get('href'),
                button.get('text'),
            ]

            for candidate in candidates:
                normalized = self._normalize_code(candidate)
                if normalized:
                    button_map.setdefault(normalized, []).append(button)

        for song in songs:
            code_candidates = [song.get('code'), song.get('title')]
            for candidate in code_candidates:
                normalized = self._normalize_code(candidate)
                if normalized and normalized in button_map:
                    song['download_buttons'] = button_map[normalized]
                    self._apply_download_button_metadata(song)
                    break

        if not any('download_buttons' in song for song in songs):
            min_len = min(len(songs), len(buttons))
            for idx in range(min_len):
                songs[idx]['download_buttons'] = [buttons[idx]]
                self._apply_download_button_metadata(songs[idx])

    def _apply_download_button_metadata(self, song: Dict[str, str]):
        """根据下载按钮更新歌曲的下载信息"""
        buttons = song.get('download_buttons')
        if not buttons:
            return

        id_media = self._extract_id_media_from_buttons(buttons)
        if id_media:
            song['id_media'] = id_media
            self._compose_play_url(song, id_media_override=id_media)

    def _extract_id_media_from_buttons(self, buttons: List[Dict[str, str]]) -> Optional[str]:
        """从下载按钮集合中提取id_media"""
        priority_keys = [
            'download_target',
            'data_id_media',
            'data_media',
            'data_id',
            'data_url',
            'href',
            'onclick',
            'text',
        ]

        for button in buttons:
            for key in priority_keys:
                value = button.get(key)
                if not value:
                    continue

                if isinstance(value, list):
                    value = ' '.join(value)

                match = re.search(r'(\d+)', str(value))
                if match:
                    return match.group(1)

        return None

    def _compose_play_url(self, song_info: Dict[str, str], id_media_override: Optional[str] = None):
        """根据曲目信息构建播放链接"""
        code = song_info.get('code')
        if not code:
            return

        album_code = code.split('-')[0].strip()
        title = song_info.get('title', 'track')
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'\s+', '-', clean_title).strip('-') or 'track'

        id_media = id_media_override or song_info.get('id_media') or self._extract_id_media_from_code(code)
        if not id_media:
            id_media = '1'

        # 获取序列号中的数字部分，并确保是两位数（一位数前面补0）
        track_num = code.split('-')[1].strip()
        if len(track_num) == 1:
            track_num = f"0{track_num}"

        song_info['id_media'] = id_media
        song_info['play_url'] = f"https://stream.cezame.cn/albums/{album_code}/mp3/128/{track_num}-{clean_title}.mp3?id_media={id_media}"

    def _extract_id_media_from_code(self, code: str) -> Optional[str]:
        """从序列号中推测id_media"""
        if not code:
            return None

        id_part = code.split('-')[1] if '-' in code else code
        digits = re.sub(r'\D', '', id_part)
        return digits or id_part.strip() or None
    
    def _parse_from_lines(self, lines: List[str]) -> List[Dict[str, str]]:
        """从文本行解析歌曲信息"""
        songs = []
        current_song = {}
        
        for line in lines:
            # 检查是否是歌曲标题行
            if re.match(r'^[【\[].*[\]】]', line) or '曲名' in line or '歌曲' in line:
                if current_song:
                    songs.append(current_song)
                    current_song = {}
            
            # 解析键值对
            if ':' in line or '：' in line:
                parts = re.split(r'[:：]', line, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # 标准化键名
                    if '曲名' in key or '歌曲' in key or 'Title' in key:
                        current_song['title'] = value
                    elif '作曲家' in key or 'Composer' in key:
                        current_song['composer'] = value
                    elif '演唱者' in key or 'Singer' in key:
                        current_song['singer'] = value
                    elif '专辑' in key or 'Album' in key:
                        current_song['album'] = value
                    elif '序列号' in key or 'Code' in key:
                        current_song['code'] = value
                    elif '时长' in key or 'Duration' in key:
                        current_song['duration'] = value
                    elif '调性' in key or 'Key' in key:
                        current_song['key'] = value
                    elif 'BPM' in key:
                        current_song['bpm'] = value
        
        # 添加最后一个歌曲
        if current_song:
            songs.append(current_song)
        
        return songs
    
    def _parse_song_container(self, container) -> Optional[Dict[str, str]]:
        """解析单个歌曲容器"""
        song_info = {}

        # 获取容器内所有文本
        text_content = container.get_text('\n', strip=True)

        # 提取标题
        title_match = re.search(r'(曲名|歌曲|Track|Title)[:：]\s*([^\n]+)', text_content)
        if title_match:
            song_info['title'] = title_match.group(2).strip()

        # 提取作曲家
        composer_match = re.search(r'(作曲家|Composer)[:：]\s*([^\n]+)', text_content)
        if composer_match:
            song_info['composer'] = composer_match.group(2).strip()

        # 提取演唱者
        singer_match = re.search(r'(演唱者|Singer)[:：]\s*([^\n]+)', text_content)
        if singer_match:
            song_info['singer'] = singer_match.group(2).strip()

        # 提取专辑
        album_match = re.search(r'(专辑|Album)[:：]\s*([^\n]+)', text_content)
        if album_match:
            song_info['album'] = album_match.group(2).strip()

        # 提取序列号/代码
        code_match = re.search(r'(序列号|Code|代码)[:：]\s*([^\n]+)', text_content)
        if code_match:
            song_info['code'] = code_match.group(2).strip()

        # 提取时长
        duration_match = re.search(r'(时长|Duration)[:：]\s*([^\n]+)', text_content)
        if duration_match:
            song_info['duration'] = duration_match.group(2).strip()

        # 提取调性
        key_match = re.search(r'(调性|Key)[:：]\s*([^\n]+)', text_content)
        if key_match:
            song_info['key'] = key_match.group(2).strip()

        # 提取BPM
        bpm_match = re.search(r'BPM[:：]\s*([^\n]+)', text_content)
        if bpm_match:
            song_info['bpm'] = bpm_match.group(1).strip()

        # 提取许可证号
        license_match = re.search(r'(许可号|许可证)[:：]\s*([^\n]+)', text_content)
        if license_match:
            song_info['license'] = license_match.group(2).strip()

        # 提取发布日期
        date_match = re.search(r'(发布日期|日期)[:：]\s*([^\n]+)', text_content)
        if date_match:
            song_info['release_date'] = date_match.group(2).strip()

        # 提取出版方
        publisher_match = re.search(r'(出版方|出版商)[:：]\s*([^\n]+)', text_content)
        if publisher_match:
            song_info['publisher'] = publisher_match.group(2).strip()

        # 提取国际标准音像制品编码
        isrc_match = re.search(r'(国际标准音像制品编码|ISRC)[:：]\s*([^\n]+)', text_content)
        if isrc_match:
            song_info['isrc'] = isrc_match.group(2).strip()

        # 如果没有找到标题，尝试从专辑标题获取
        if not song_info.get('title'):
            # 查找专辑标题行，通常在顶部
            lines = text_content.split('\n')
            for line in lines:
                if '专辑' in line or 'Album' in line:
                    # 提取专辑标题
                    album_title_match = re.search(r'(专辑|Album)[:：]\s*([^\n]+)', line)
                    if album_title_match:
                        song_info['album'] = album_title_match.group(2).strip()
                        # 尝试从同一行获取标题
                        title_from_album = re.search(r'^(.+?)[\s\[]', line)
                        if title_from_album:
                            song_info['title'] = title_from_album.group(1).strip()
                    break

        return song_info if song_info else None

    def _extract_song_info(self, text: str) -> Optional[Dict[str, str]]:
        """从文本片段提取歌曲信息"""
        song_info = {}

        # 提取标题
        title_match = re.search(r'曲名\s*:\s*([^\n]+)', text)
        if title_match:
            song_info['title'] = title_match.group(1).strip()

        # 提取序列号/代码
        code_match = re.search(r'序列号\s*:\s*([^\n]+)', text)
        if code_match:
            song_info['code'] = code_match.group(1).strip()

        # 提取作曲家
        composer_match = re.search(r'作曲家\s*:\s*([^\n]+)', text)
        if composer_match:
            song_info['composer'] = composer_match.group(1).strip()

        # 提取许可证号
        license_match = re.search(r'许可号\s*:\s*([^\n]+)', text)
        if license_match:
            song_info['license'] = license_match.group(1).strip()

        # 提取专辑
        album_match = re.search(r'专辑\s*:\s*([^\n]+)', text)
        if album_match:
            song_info['album'] = album_match.group(1).strip()

        # 提取发布日期
        date_match = re.search(r'发布日期\s*:\s*([^\n]+)', text)
        if date_match:
            song_info['release_date'] = date_match.group(1).strip()

        # 提取出版方
        publisher_match = re.search(r'出版方\s*:\s*([^\n]+)', text)
        if publisher_match:
            song_info['publisher'] = publisher_match.group(1).strip()

        # 提取播放链接（基于序列号构建）
        # 播放链接格式为：https://stream.cezame.cn/albums/专辑代码/mp3/128/曲目文件名.mp3?id_media=ID
        # 示例：https://stream.cezame.cn/albums/CET9012/mp3/128/Thunderbolt.mp3?id_media=51149
        # 注意：id_media参数的值需要从页面的id_medias_listened变量中获取，这里暂时使用序列号的数字部分作为占位符
        if 'code' in song_info:
            # 从序列号中提取专辑代码（如 CET9012）
            code = song_info['code'].strip()
            # 移除序列号中的空格和连字符后的数字部分
            album_code = code.split('-')[0].strip()

            # 构建播放链接（基于序列号生成，id_media使用序列号的数字部分）
            # 移除序列号中的空格
            clean_code = code.replace(' ', '')
            # 提取数字部分作为id_media（如 7, 17, 3等）
            id_media = code.split('-')[1].strip() if '-' in code else '1'

            # 获取歌曲标题用于文件名
            title = song_info.get('title', 'track')
            # 移除标题中的特殊字符，保留字母、数字和空格
            clean_title = re.sub(r'[^\w\s-]', '', title)
            # 替换空格为连字符
            clean_title = re.sub(r'\s+', '-', clean_title)

            song_info['play_url'] = f"https://stream.cezame.cn/albums/{album_code}/mp3/128/{clean_title}.mp3?id_media={id_media}"

        return song_info if song_info else None

    def _extract_song_info_from_block(self, block: str) -> Optional[Dict[str, str]]:
        """从文本块提取歌曲信息"""
        song_info = {}

        # 提取标题 - 查找可能的标题行
        lines = block.split('\n')
        for line in lines:
            # 标题通常在第一行或包含特定关键词
            if '曲名' in line or '歌曲' in line or 'Track' in line or 'Title' in line:
                title_match = re.search(r'(曲名|歌曲|Track|Title)[:：]\s*([^\n]+)', line)
                if title_match:
                    song_info['title'] = title_match.group(2).strip()
                    break

        # 如果没有找到标题，尝试从第一行获取
        if not song_info.get('title') and lines:
            first_line = lines[0].strip()
            # 如果第一行不是键值对，可能是标题
            if ':' not in first_line and '：' not in first_line and len(first_line) > 0:
                song_info['title'] = first_line

        # 提取其他信息
        text_content = block

        # 提取作曲家
        composer_match = re.search(r'(作曲家|Composer)[:：]\s*([^\n]+)', text_content)
        if composer_match:
            song_info['composer'] = composer_match.group(2).strip()

        # 提取演唱者
        singer_match = re.search(r'(演唱者|Singer)[:：]\s*([^\n]+)', text_content)
        if singer_match:
            song_info['singer'] = singer_match.group(2).strip()

        # 提取专辑
        album_match = re.search(r'(专辑|Album)[:：]\s*([^\n]+)', text_content)
        if album_match:
            song_info['album'] = album_match.group(2).strip()

        # 提取序列号/代码
        code_match = re.search(r'(序列号|Code|代码)[:：]\s*([^\n]+)', text_content)
        if code_match:
            song_info['code'] = code_match.group(2).strip()

        # 提取时长
        duration_match = re.search(r'(时长|Duration)[:：]\s*([^\n]+)', text_content)
        if duration_match:
            song_info['duration'] = duration_match.group(2).strip()

        # 提取调性
        key_match = re.search(r'(调性|Key)[:：]\s*([^\n]+)', text_content)
        if key_match:
            song_info['key'] = key_match.group(2).strip()

        # 提取BPM
        bpm_match = re.search(r'BPM[:：]\s*([^\n]+)', text_content)
        if bpm_match:
            song_info['bpm'] = bpm_match.group(1).strip()

        # 提取许可证号
        license_match = re.search(r'(许可号|许可证)[:：]\s*([^\n]+)', text_content)
        if license_match:
            song_info['license'] = license_match.group(2).strip()

        # 提取发布日期
        date_match = re.search(r'(发布日期|日期)[:：]\s*([^\n]+)', text_content)
        if date_match:
            song_info['release_date'] = date_match.group(2).strip()

        # 提取出版方
        publisher_match = re.search(r'(出版方|出版商)[:：]\s*([^\n]+)', text_content)
        if publisher_match:
            song_info['publisher'] = publisher_match.group(2).strip()

        # 提取国际标准音像制品编码
        isrc_match = re.search(r'(国际标准音像制品编码|ISRC)[:：]\s*([^\n]+)', text_content)
        if isrc_match:
            song_info['isrc'] = isrc_match.group(2).strip()

        # 提取播放链接（基于序列号构建）
        # 播放链接格式为：https://stream.cezame.cn/albums/专辑代码/mp3/128/曲目文件名.mp3?id_media=ID
        # 示例：https://stream.cezame.cn/albums/CET9012/mp3/128/Thunderbolt.mp3?id_media=51149
        # 注意：id_media参数的值需要从页面的id_medias_listened变量中获取，这里暂时使用序列号的数字部分作为占位符
        if 'code' in song_info:
            # 从序列号中提取专辑代码（如 CET9012）
            code = song_info['code'].strip()
            # 移除序列号中的空格和连字符后的数字部分
            album_code = code.split('-')[0].strip()

            # 构建播放链接（基于序列号生成，id_media使用序列号的数字部分）
            # 移除序列号中的空格
            clean_code = code.replace(' ', '')
            # 提取数字部分作为id_media（如 7, 17, 3等）
            id_media = code.split('-')[1].strip() if '-' in code else '1'

            # 获取歌曲标题用于文件名
            title = song_info.get('title', 'track')
            # 移除标题中的特殊字符，保留字母、数字和空格
            clean_title = re.sub(r'[^\w\s-]', '', title)
            # 替换空格为连字符
            clean_title = re.sub(r'\s+', '-', clean_title)

            song_info['play_url'] = f"https://stream.cezame.cn/albums/{album_code}/mp3/128/{clean_title}.mp3?id_media={id_media}"

        return song_info if song_info else None

    def display_songs(self, songs: List[Dict[str, str]]):
        """显示歌曲列表"""
        if not songs:
            print("未找到歌曲信息")
            return

        print(f"\n共找到 {len(songs)} 首歌曲:\n")
        print("=" * 80)

        for i, song in enumerate(songs, 1):
            print(f"\n{i}. {song.get('title', '未知标题')}")
            print("-" * 40)

            # 显示所有可用字段
            field_mapping = {
                'composer': '作曲家',
                'singer': '演唱者',
                'album': '专辑',
                'code': '序列号',
                'duration': '时长',
                'key': '调性',
                'bpm': 'BPM',
                'license': '许可号',
                'release_date': '发布日期',
                'publisher': '出版方',
                'isrc': '国际标准音像制品编码',
                'play_url': '播放链接'
            }

            for field, label in field_mapping.items():
                if field in song and song[field]:
                    print(f"  {label}: {song[field]}")

        print("\n" + "=" * 80)
    
    def run(self, url: str):
        """运行爬虫"""
        print(f"正在访问: {url}")
        html = self.fetch_page(url)
        
        if not html:
            print("无法获取网页内容")
            return
        
        print("正在解析页面...")
        songs = self.parse_song_list(html)
        
        print("解析完成，显示结果...")
        self.display_songs(songs)


def main():
    """主函数"""
    # 目标URL（包含page参数）
    url = "https://www.cezame.cn/liste_resultats.php?mot%5B%5D=%E7%B4%A7%E5%BC%A0%40%40%40%40%E7%B4%A7%E5%BC%A0%40%40%40%40&search_external_recommendation_brief=&search_external_recommendation_youtube=&search_external_recommendation_paroles="

    # 创建爬虫实例并运行
    crawler = MusicCrawler()
    crawler.run(url)


if __name__ == "__main__":
    main()
