#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 定义banner
banner = r"""
           _                 _       _                       _       _
  __ _ ___| |__        _ __ | |     | |_ ___ _ __ ___  _ __ | | __ _| |_ ___
 / _` / __| '_ \ _____| '_ \| |_____| __/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \
| (_| \__ \ |_) |_____| |_) | |_____| ||  __/ | | | | | |_) | | (_| | ||  __/
 \__,_|___/_.__/      | .__/|_|      \__\___|_| |_| |_| .__/|_|\__,_|\__\___|
                      |_|                             |_|
"""

ANSIBLE_CFG = """
[defaults]
host_key_checking=False
pipelining=True
forks=100
any_errors_fatal=True
keep_remote_files=False

[ssh_connection]
retries = 15
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=600s
timeout = 10
"""

README_TEMPLATE = """
# project_name
description: project_name

## usage
"""

INVENTORY_TEMPLATE = """
# You can customize the base group here.
# These hostname must be resolvable from your deployment host
# You can add the following parameters for each node
# ansible_user=root api_interface=eth0
[nodes]
node01 api_interface=eth0
node02 api_interface=eth0
node03 api_interface=eth0

[server]
# This node is used to run the apiserver
node01 api_interface=eth0

[deploy]
# The deploy node represents the node where you run ansible and cannot be modified.
localhost ansible_connection=local api_interface=eth0

# The following is the group where each project is located
[openssl:children]
# Certificate generation node, in the deploy node, cannot be changed
deploy

[etcd:children]
nodes

[kubectl:children]
# It need to execute the kubectl command through the deployment node,
# so kubectl must include the deploy
deploy
nodes

[kubeserver:children]
server

[flannel:children]
nodes

[kubelet:children]
nodes
"""

# 定义项目结构模板
PROJECT_TEMPLATE = {
    '.asb-pl-template': {},
    'README.md': README_TEMPLATE,
    'ansible.cfg': ANSIBLE_CFG,
    'hosts': INVENTORY_TEMPLATE,
    'group_vars': {
        'main.yml': '# Common variables for all environments',
        'local.yml': '# Variables for local development',
        'prod.yml': '# Variables for production environment',
        'stage.yml': '# Variables for staging environment'
    },
    'host_vars': {
        'prod.yml': '# Variables for production hosts',
        'stage.yml': '# Variables for staging hosts'
    },
    'library': {},
    'requirements.yml': '# List your role dependencies here',
    'playbooks': {
        'site.yml': '# Main playbook\n - hosts: all\n   roles:\n     - role: common\n     - role: web\n     - role: database',
        'site-local.yml': '# Playbook for local development\n - hosts: local\n   roles:\n     - role: common\n     - role: web\n     - role: database',
        'site-prod.yml': '# Playbook for production environment\n - hosts: prod\n   roles:\n     - role: common\n     - role: web\n     - role: database',
        'site-stage.yml': '# Playbook for staging environment\n - hosts: stage\n   roles:\n     - role: common\n     - role: web\n     - role: database'
    },
    'inventories': {
        'prod': {
            'group_vars': {},
            'host_vars': {},
            'inventory': '# Production inventory file'
        },
        'stage': {
            'group_vars': {},
            'host_vars': {},
            'inventory': '# Staging inventory file'
        }
    },
    'roles': {},
    'tests': {
        'test.yml': {},
    }
}

TASK_TEMPLATE = """
# 示例任务
---
- name: 示例任务
  debug:
    msg: "This is an example task"    
"""

# 定义角色结构模板
ROLE_TEMPLATE = {
    'tasks': {
        'main.yml': TASK_TEMPLATE
    },
    'handlers': {
        'main.yml': {}
    },
    'templates': {
        'ntp.conf.j2': '# NTP configuration template'
    },
    'files': {
        'bar.txt': 'This is a sample text file',
        'foo.sh': '#!/bin/bash\n# This is a sample script'
    },
    'vars': {
        'main.yml': '# Variables for this role'
    },
    'defaults': {
        'main.yml': '# Default variables for this role'
    },
    'meta': {
        'main.yml': '# Role dependencies'
    }
}

# 新增简单的 playbook 模板
SIMPLE_PLAYBOOK_TEMPLATE = """
# 简单的 Ansible Playbook 示例
---
# 目标主机组
- hosts: all
  gather_facts: yes
  become: yes
  become_method: sudo

  # 任务列表
  tasks:
    - name: 显示主机名
      debug:
        msg: "当前主机名是 {{ ansible_hostname }}"

    - name: install packages
      apt: name=apt-transport-https,ca-certificates,curl,software-properties-common state=present

    - name: import key
      shell: curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add -

    - name: import installation source on ubuntu1804
      shell: add-apt-repository "deb [arch=amd64] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu {{ubuntu1804}} stable"
      when: ansible_facts['distribution_major_version'] == "18"

    - name: import installation source on ubuntu2004
      shell: add-apt-repository "deb [arch=amd64] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu {{ubuntu2004}} stable"
      when: ansible_facts['distribution_major_version'] == "20"

    - name: install docker for ubuntu1804
      apt: name=docker-ce={{docker_version}}{{ubuntu1804}},docker-ce-cli={{docker_version}}{{ubuntu1804}}
      when: ansible_facts['distribution_major_version'] == "18"

    - name: install docker for ubuntu2004
      apt: name=docker-ce={{docker_version}}{{ubuntu2004}},docker-ce-cli={{docker_version}}{{ubuntu2004}}
      when: ansible_facts['distribution_major_version'] == "20"

    - name: mkdir /etc/docker
      file: path=/etc/docker state=directory

    - name: aliyun Mirror acceleration
      copy: src=/data/ansible/files/daemon.json dest=/etc/docker/

    - name: load daemon
      shell: systemctl daemon-reload

    - name: start docker
      service: name=docker state=started enabled=yes
# ...
# 使用示例
# 假设该 playbook 文件名为 simple_playbook.yml
# 运行 playbook 到所有主机：
# ansible-playbook simple_playbook.yml -i hosts
# 运行 playbook 到特定主机组：
# ansible-playbook simple_playbook.yml -i hosts --limit group_name
"""

import os


def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return '.'.join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))


init = os.path.join(os.path.dirname(__file__), "__init__.py")
version_line = list(filter(lambda l: l.startswith("VERSION"), open(init)))[0]
VERSION = get_version(eval(version_line.split('=')[-1]))
