"""pytest 配置：把仓根目录加入 sys.path。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
