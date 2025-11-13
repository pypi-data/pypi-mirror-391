#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil


def check_directory_exists(path):
    return os.path.exists(path) and os.path.isdir(path)


def copy_file(source, destination):
    try:
        shutil.copy2(source, destination)
    except Exception as e:
        print(f"Error copying file: {e}")


def mkdirs(path, exist_ok=True):
    try:
        os.makedirs(path, exist_ok=exist_ok)
    except Exception as e:
        print(f"Error creating directory: {e}")


def readable_size(size):
    orders = ['K', 'KB', 'MB', 'GB', 'TB']
    order_index = 0
    while size > 1024 and order_index < len(orders):
        size /= 1024.0
        order_index += 1

    return "{:.1f} %s".format(size) % orders[order_index]
