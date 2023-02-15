# -*- coding:UTF-8 -*-
# Created by Shing at 2020/2/22
import os
import sys

'''递归删除指定文件或目录'''


def recursive_rm_file(*files):
    assert files, '请输入文件'
    dirs = [f for f in files if os.path.isdir(f)]
    for f in set(files).difference(set(dirs)):
        os.remove(f)

    for d in dirs:
        for root, sub_dirs, items in os.walk(d, topdown=False):
            print(root, sub_dirs, items)
            for f in items:
                os.remove(os.path.join(root, f))
            for f in sub_dirs:
                os.rmdir(os.path.join(root, f))


if __name__ == '__main__':
    current_dir = os.path.abspath(os.path.curdir)
    files = [f if f.startswith(os.path.sep) else os.path.join(current_dir, f) for f in sys.argv[1:]]
    recursive_rm_file(*files)
