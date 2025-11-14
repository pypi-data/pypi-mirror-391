#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/10 22:09
# @Author  : hjl
# @Site    :
# @File    : crudini.py
# @Software: PyCharm
# @Desc    : 使用python实现一个工具 curdini.py，实现对ini或conf文件的put、get、update、delete，使用argparse、configparser
# 类似项目：https://github.com/pixelb/crudini

import configparser


class Curdini:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 保留大小写
        self.config.read(self.config_file)

    def set_param(self, section, param, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, param, value)
        self._save_config()

    def get_param(self, section=None, param=None):
        if section is None:
            sections = self.config.sections()
            for sec in sections:
                print(f"[{sec}]")
                for key, val in self.config.items(sec):
                    print(f"{key} = {val}")
        elif not self.config.has_section(section) or (
                param and not self.config.has_option(section, param)
        ):
            print("Section or parameter not found.")
        elif param:
            print(self.config.get(section, param))
        else:
            print(self.config[section])

    def update_param(self, section, param, value):
        if not self.config.has_section(section):
            print("Section not found.")
            return
        self.config.set(section, param, value)
        self._save_config()

    def delete_param(self, section, param_list):
        if not self.config.has_section(section):
            print("Section not found.")
            return
        for param in param_list:
            if self.config.has_option(section, param):
                self.config.remove_option(section, param)
        self._save_config()

    def merge_configs(self, merge_file):
        merge_config = configparser.ConfigParser()
        merge_config.optionxform = str  # 保留大小写
        merge_config.read(merge_file)
        for section in merge_config.sections():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for option in merge_config.options(section):
                self.config.set(section, option, merge_config.get(section, option))
        self._save_config()

    def _save_config(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)
