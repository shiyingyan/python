# -*- coding:UTF-8 -*-
# Created by Shing at 2020/2/22
import os
import sys

'''递归删除文件或目录'''
def recursive_rm_file(dir, *file_name):
    assert file_name, '请输入文件名'
    print('dir:{},file_name:{}'.format(dir, file_name))
    if not dir:
        dir = os.path.curdir
    for dir_name, sub_dirs, files in os.walk(dir):
        if not files:
            if not sub_dirs:
                if file_name.__eq__(dir) or file_name.__contains__(dir):
                    dir_name = os.path.abspath(dir_name)
                    print('删除了文件夹{}'.format(dir_name))
                    os.system('rm -rf {}'.format(dir_name))
            for sub_dir in sub_dirs:
                if sub_dir.__eq__(dir_name):
                    sub_dir = os.path.join(os.path.abspath(dir_name), sub_dir)
                recursive_rm_file(sub_dir, *file_name)
        for file in files:
            if file_name.__contains__(file) or file_name.__eq__(file):
                dir_name = os.path.abspath(dir_name)
                print('删除了文件{}'.format(os.path.join(dir_name, file)))
                os.system('rm -rf {}'.format(os.path.join(dir_name, file)))


if __name__ == '__main__':
    dir = os.path.abspath(os.path.curdir)
    file_name = ''
    print(sys.argv)
    if len(sys.argv) == 1:
        raise Exception('请输入要递归删除的文件名字，如果有扩展名，请包含扩展名')
    if len(sys.argv) == 2:
        file_name = sys.argv[1]
        recursive_rm_file(dir, file_name)
    if len(sys.argv) > 2:
        dir = sys.argv[1]
        file_names = sys.argv[2:]
        recursive_rm_file(dir, *file_names)
