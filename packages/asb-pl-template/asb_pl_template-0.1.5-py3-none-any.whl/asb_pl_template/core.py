#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from .constants import PROJECT_TEMPLATE, ROLE_TEMPLATE, SIMPLE_PLAYBOOK_TEMPLATE
import logging
from .logger import setup_logger
from .lib import check_directory_exists, mkdirs


class AnsibleProjectManager:
    def __init__(self, project_name=None, roles_path=None, role_names=None, playbook_path=None, playbook_name=None,
                 example=False,
                 verbose=False):
        self.project_name = project_name
        self.roles_path = roles_path
        self.role_names = role_names if role_names else []
        self.playbook_path = playbook_path if playbook_path else os.path.join(os.getcwd(), 'playbooks')
        self.playbook_name = playbook_name if playbook_name != "." else os.path.join(os.getcwd(), 'playbooks',
                                                                                     'default.yml')
        self.example = example
        self.logger = setup_logger('asb-pl-template', logging.DEBUG if verbose else logging.INFO)
        if project_name:
            self.project_path = os.path.abspath(project_name) if os.path.isabs(project_name) else os.path.join(
                os.getcwd(), project_name)

    def create_directory_structure(self, path, template, project_name=None):
        """
        创建目录结构
        :param path: 目录路径
        :param template: 目录结构模板
        :param project_name: 项目名称
        :return: None
        """
        for key, value in template.items():
            try:
                if isinstance(value, dict):
                    new_path = os.path.join(path, key)
                    if not check_directory_exists(new_path):
                        mkdirs(new_path, exist_ok=True)
                        self.logger.debug(f"Created directory: {new_path}")
                    self.create_directory_structure(new_path, value, project_name)
                else:
                    file_path = os.path.join(path, key)
                    if project_name:
                        content = value.format(project_name=project_name)
                    else:
                        content = value
                    with open(file_path, 'w') as f:
                        f.write(content)
                    self.logger.debug(f"Created file: {file_path}")
            except Exception as e:
                self.logger.error(f"Error creating {key}: {e}")

    def create_role(self, role_path, role_names):
        """
        创建角色
        :param role_path: 角色路径
        :param role_names: 角色名称列表
        :return: None
        """
        mkdirs(role_path, exist_ok=True)
        self.logger.debug(f"Creating role directory: {role_path}")
        for role_name in role_names:
            role_full_path = os.path.join(role_path, role_name)
            mkdirs(role_full_path, exist_ok=True)
            self.create_directory_structure(role_full_path, ROLE_TEMPLATE)
            self.logger.debug(f"Created role: {role_full_path}")

    def create_playbook(self, playbook_path, playbook_name, example=False):
        """
        创建playbook
        :param playbook_path: playbook所在路径
        :param playbook_name: playbook名称
        :param example: 是否创建示例playbook
        """
        playbook_abs_path = os.path.abspath(playbook_path)
        mkdirs(playbook_abs_path, exist_ok=True)
        playbook_full_name = os.path.abspath(os.path.join(playbook_abs_path, os.path.basename(playbook_name)))
        if example:
            with open(playbook_full_name, 'w') as f:
                f.write(SIMPLE_PLAYBOOK_TEMPLATE)
        else:
            with open(playbook_full_name, 'w') as f:
                f.write(f'# {os.path.basename(playbook_name)} playbook')
        self.logger.debug(f"Created playbook: {playbook_full_name}")

    def create_project(self, **kwargs):
        """
        创建项目
        :param kwargs: 关键字参数
        :return: None
        """
        try:
            project_name = kwargs.get('project_name', self.project_name)
            roles_path = kwargs.get('roles_path', self.roles_path)
            role_names = kwargs.get('role_names', self.role_names)
            playbook_name = kwargs.get('playbook_name', self.playbook_name)

            if project_name:
                self.project_path = os.path.abspath(project_name) if os.path.isabs(project_name) else os.path.join(
                    os.getcwd(), project_name)
                self.logger.debug(f"Creating project: {project_name}")
                mkdirs(self.project_path, exist_ok=True)
                self.create_directory_structure(self.project_path, PROJECT_TEMPLATE, project_name)
            else:
                self.project_path = os.getcwd()

            if role_names:
                if not roles_path:
                    roles_full_path = os.path.join(self.project_path, 'roles')
                else:
                    roles_full_path = os.path.abspath(roles_path)
                self.create_role(roles_full_path, role_names)
            if playbook_name:
                playbook_path = os.path.join(self.project_path, 'playbooks')
                self.create_playbook(playbook_path, playbook_name)
        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
