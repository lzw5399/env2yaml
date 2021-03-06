#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- author: lzw5399 -*-
import os
import sys

import yaml

if len(sys.argv) < 2:
    print("Must specify the YAML file path. e.g. [ python env2yaml.py appsettings.yaml ]")
    exit(-1)

main_dir = os.path.split(os.path.realpath(__file__))[0]
yaml_path = os.path.join(main_dir, sys.argv[1])

PREFIX = ""
if len(sys.argv) > 2:
    PREFIX = sys.argv[2]

scalar_list = [str, bool, int, float, None]


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


def gen_env_key(current, dependencies):
    if dependencies is None:
        dependencies = []

    if '__'.join(dependencies) == '':
        return '{}_{}'.format(PREFIX, current).lstrip('_')
    else:
        return '{}_{}__{}'.format(PREFIX, '__'.join(dependencies), current).lstrip('_')


# 针对list的env_key
def gen_list_env_key(current, index, dependencies):
    if dependencies is None:
        dependencies = []
    if '__'.join(dependencies) == '':
        return '{}_{}{}'.format(PREFIX, current, index).lstrip('_')
    else:
        return '{}_{}__{}{}'.format(PREFIX, '__'.join(dependencies), current, index).lstrip('_')


# load setting from env recursively
def load_env_to_content(content, level=0, dependencies=None):
    for key in content.keys():
        if level == 0 or dependencies is None:
            dependencies = []

        env_key = gen_env_key(key, dependencies)
        if type(content[key]) in scalar_list and os.getenv(env_key) is not None:
            content.__setitem__(key, os.getenv(env_key))

        # 对象
        elif type(content[key]) == dict:
            dependencies.append(key)
            load_env_to_content(content[key], level=level + 1, dependencies=dependencies)

        # 基本类型数组
        elif type(content[key]) == list and type(content[key][0]) in scalar_list:
            new_list = content[key][:]
            for i, v in enumerate(content[key]):
                env_key = gen_list_env_key(key, index=i, dependencies=dependencies)
                if os.getenv(env_key) is not None:
                    new_list[i] = os.getenv(env_key)
            content.__setitem__(key, new_list)

        # 对象数组
        elif type(content[key]) == list and type(content[key][0]) == dict:
            print("yes list")


def convert_settings():
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = yaml.safe_load(f)

    load_env_to_content(content)

    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(content, f, Dumper=IndentDumper, allow_unicode=True, sort_keys=False, indent=4)


if __name__ == '__main__':
    convert_settings()
