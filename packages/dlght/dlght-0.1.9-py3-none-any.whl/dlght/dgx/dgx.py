

import urllib.request
import urllib.error
import os
from pathlib import Path
import re
import sys
import time


class DGX:


    def __init__(self, url: str, output: str = None, resume: bool = True) -> None:
        """
        这个函数的作用是下载github上的任意文件（支持断点续传）
        
        Args:
            url: GitHub文件的URL (支持普通URL和raw URL)
            output: 输出文件路径 (可选，默认使用原文件名保存到当前目录)
            resume: 是否启用断点续传 (默认: True)
        
        Examples:
            dlght x https://github.com/user/repo/blob/main/file.txt
            dlght x https://raw.githubusercontent.com/user/repo/main/file.txt
            dlght x https://github.com/user/repo/blob/main/file.txt --output=myfile.txt
            dlght x https://github.com/user/repo/blob/main/file.txt --resume=False
        """
        try:
            # 将GitHub URL转换为raw URL
            raw_url = self._convert_to_raw_url(url)
            
            # 确定输出文件名
            if output is None:
                # 从URL中提取文件名
                filename = self._extract_filename(raw_url)
                output = filename
            
            # 创建输出目录（如果需要）
            output_path = Path(output)
            if output_path.parent != Path('.'):
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查是否存在未完成的下载
            existing_size = 0
            if resume and os.path.exists(output):
                existing_size = os.path.getsize(output)
                if existing_size > 0:
                    print(f"发现未完成的下载，已下载: {self._format_size(existing_size)}")
            
            # 下载文件（带断点续传和进度条）
            print(f"正在下载: {raw_url}")
            print(f"保存到: {output}")
            
            self._download_with_resume(raw_url, output, existing_size if resume else 0)
            
            # 换行，结束进度条
            print()
            
            # 获取文件大小
            file_size = os.path.getsize(output)
            print(f"✓ 下载成功! 文件大小: {self._format_size(file_size)}")
            
        except urllib.error.HTTPError as e:
            print(f"\n✗ HTTP错误: {e.code} - {e.reason}")
            print(f"请检查URL是否正确: {url}")
        except urllib.error.URLError as e:
            print(f"\n✗ 网络错误: {e.reason}")
        except KeyboardInterrupt:
            print(f"\n⚠ 下载已暂停，下次运行将从断点继续")
        except Exception as e:
            print(f"\n✗ 下载失败: {str(e)}")
    
    def _convert_to_raw_url(self, url: str) -> str:
        """
        将GitHub URL转换为raw URL
        
        支持的格式:
        - https://github.com/user/repo/blob/branch/path/file.txt
        - https://raw.githubusercontent.com/user/repo/branch/path/file.txt
        """
        # 如果已经是raw URL，直接返回
        if 'raw.githubusercontent.com' in url:
            return url
        
        # 转换 github.com/user/repo/blob/branch/path 为 raw.githubusercontent.com/user/repo/branch/path
        pattern = r'https://github\.com/([^/]+)/([^/]+)/blob/(.+)'
        match = re.match(pattern, url)
        
        if match:
            user, repo, path = match.groups()
            raw_url = f'https://raw.githubusercontent.com/{user}/{repo}/{path}'
            return raw_url
        
        # 如果不匹配已知格式，尝试直接使用原URL
        return url
    
    def _extract_filename(self, url: str) -> str:
        """从URL中提取文件名"""
        # 从URL中获取最后一部分作为文件名
        filename = url.split('/')[-1]
        # 移除可能的查询参数
        filename = filename.split('?')[0]
        return filename if filename else 'downloaded_file'
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _download_with_resume(self, url: str, output: str, start_pos: int = 0) -> None:
        """
        支持断点续传的下载函数
        
        Args:
            url: 下载URL
            output: 输出文件路径
            start_pos: 起始位置（字节）
        """
        # 创建请求
        req = urllib.request.Request(url)
        
        # 如果有起始位置，添加Range头
        if start_pos > 0:
            req.add_header('Range', f'bytes={start_pos}-')
        
        # 打开URL连接
        with urllib.request.urlopen(req) as response:
            # 获取文件总大小
            if start_pos > 0:
                # 断点续传时，从Content-Range获取总大小
                content_range = response.headers.get('Content-Range')
                if content_range:
                    total_size = int(content_range.split('/')[-1])
                else:
                    # 服务器不支持断点续传，重新下载
                    print("⚠ 服务器不支持断点续传，将重新下载")
                    start_pos = 0
                    total_size = int(response.headers.get('Content-Length', 0))
            else:
                total_size = int(response.headers.get('Content-Length', 0))
            
            # 打开文件（追加或新建）
            mode = 'ab' if start_pos > 0 else 'wb'
            with open(output, mode) as f:
                # 分块下载
                chunk_size = 8192
                downloaded = start_pos
                start_time = time.time()
                
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 显示进度
                    self._show_progress(downloaded, total_size, start_time)
    
    def _show_progress(self, downloaded: int, total_size: int, start_time: float) -> None:
        """
        显示下载进度
        
        Args:
            downloaded: 已下载字节数
            total_size: 总字节数
            start_time: 开始时间
        """
        if total_size > 0:
            # 计算百分比
            percent = min(100, (downloaded / total_size) * 100)
            
            # 计算进度条长度
            bar_length = 40
            filled_length = int(bar_length * downloaded // total_size)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # 格式化已下载和总大小
            downloaded_str = self._format_size(downloaded)
            total_str = self._format_size(total_size)
            
            # 计算下载速度
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                speed = downloaded / elapsed_time
                speed_str = self._format_size(speed) + '/s'
                
                # 计算剩余时间
                if speed > 0:
                    remaining_bytes = total_size - downloaded
                    remaining_time = remaining_bytes / speed
                    eta_str = self._format_time(remaining_time)
                else:
                    eta_str = '--:--'
            else:
                speed_str = '--'
                eta_str = '--:--'
            
            # 打印进度条
            sys.stdout.write(f'\r进度: |{bar}| {percent:.1f}% ({downloaded_str}/{total_str}) {speed_str} ETA: {eta_str}')
            sys.stdout.flush()
        else:
            # 如果无法获取总大小，只显示已下载大小和速度
            downloaded_str = self._format_size(downloaded)
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                speed = downloaded / elapsed_time
                speed_str = self._format_size(speed) + '/s'
            else:
                speed_str = '--'
            sys.stdout.write(f'\r已下载: {downloaded_str} {speed_str}')
            sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}时{minutes}分"
    
    def _download_progress(self, block_num: int, block_size: int, total_size: int) -> None:
        """
        下载进度回调函数
        
        Args:
            block_num: 当前下载的块编号
            block_size: 每个块的大小（字节）
            total_size: 文件总大小（字节）
        """
        downloaded = block_num * block_size
        
        if total_size > 0:
            # 计算百分比
            percent = min(100, (downloaded / total_size) * 100)
            
            # 计算进度条长度
            bar_length = 50
            filled_length = int(bar_length * downloaded // total_size)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # 格式化已下载和总大小
            downloaded_str = self._format_size(downloaded)
            total_str = self._format_size(total_size)
            
            # 打印进度条（使用\r回到行首实现覆盖效果）
            sys.stdout.write(f'\r进度: |{bar}| {percent:.1f}% ({downloaded_str}/{total_str})')
            sys.stdout.flush()
        else:
            # 如果无法获取总大小，只显示已下载大小
            downloaded_str = self._format_size(downloaded)
            sys.stdout.write(f'\r已下载: {downloaded_str}')
            sys.stdout.flush()
