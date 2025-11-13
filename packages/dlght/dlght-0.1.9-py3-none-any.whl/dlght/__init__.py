
import fire
from .dgx import DGX 

class ENTRY(object):

    def __init__(self):
        self.x = DGX 


def main() -> None:
    fire.Fire(ENTRY)