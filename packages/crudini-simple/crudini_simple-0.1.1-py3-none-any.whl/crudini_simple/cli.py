#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright: (c)  : @Time 2025/11/13 18  @Author  : hjl
# @Site    : 
# @File    : cli.py
# @Project: crudini_sample
# @Software: PyCharm
# @Desc    :
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
import argparse
from .core import Curdini


def main():
    parser = argparse.ArgumentParser(
        description="INI/CONF file manipulation tool,supporting documents crud "
    )
    subparsers = parser.add_subparsers(title="actions", dest="action", help="commands")

    set_parser = subparsers.add_parser("set", help="Set a parameter")
    set_parser.add_argument("section", help="Section name")
    set_parser.add_argument("param", help="Parameter name")
    set_parser.add_argument("value", help="Value to set")

    get_parser = subparsers.add_parser("get", help="Get a parameter")
    get_parser.add_argument("section", help="Section name")
    get_parser.add_argument("param", help="Parameter name")

    update_parser = subparsers.add_parser("update", help="Update a parameter")
    update_parser.add_argument("section", help="Section name")
    update_parser.add_argument("param", help="Parameter name")
    update_parser.add_argument("value", help="Value to set")

    del_parser = subparsers.add_parser("del", help="Delete a parameter")
    del_parser.add_argument("section", help="Section name")
    del_parser.add_argument("list", nargs="+", help="List of parameter names to delete")

    merge_parser = subparsers.add_parser(
        "merge", help="Merge with another configuration file"
    )
    merge_parser.add_argument(
        "merge_file", help="File to merge with base configuration", nargs="?"
    )

    parser.add_argument("config_file", help="Configuration file")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    curdini_tool = Curdini(args.config_file)

    if args.action == "set":
        curdini_tool.set_param(args.section, args.param, args.value)
    elif args.action == "get":
        if args.section is None or args.param is None:
            print("Both section and param must be provided for the 'get' action.")
        else:
            curdini_tool.get_param(args.section, args.param)
    elif args.action == "update":
        curdini_tool.update_param(args.section, args.param, args.value)
    elif args.action == "del":
        curdini_tool.delete_param(args.section, args.list)
    elif args.action == "merge":
        curdini_tool.merge_configs(args.merge_file)
