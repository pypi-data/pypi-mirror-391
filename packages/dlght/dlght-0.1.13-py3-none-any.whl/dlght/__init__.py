
import fire
from .dgx import DGX 

class ENTRY(object):
    def x(self, url: str, output: str = None, resume: bool = True, unzip: bool = False, proxy: str = None):
        """下载GitHub文件（支持断点续传和自动解压）"""
        DGX(url, output, resume, unzip, proxy)


    def preset():
        pass 

    def from_file():
        pass


def main() -> None:
    fire.Fire(ENTRY)
