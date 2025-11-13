
import fire
from .dgx import DGX 

class ENTRY(object):
    def x(self, url: str, output: str = None, resume: bool = True, unzip: bool = False):
        """下载GitHub文件（支持断点续传和自动解压）"""
        DGX(url, output, resume, unzip)


    def preset():
        pass 

    def from_file():
        pass


def main() -> None:
    fire.Fire(ENTRY)
