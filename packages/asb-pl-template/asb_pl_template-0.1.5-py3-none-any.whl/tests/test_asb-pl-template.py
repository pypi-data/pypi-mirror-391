import unittest
from unittest.mock import patch, MagicMock
import argparse
from asb_pl_template.cli import ASBPLTemplateCLI
from asb_pl_template.core import AnsibleProjectManager


class TestASBPLTemplateCLI(unittest.TestCase):

    def setUp(self):
        self.cli = ASBPLTemplateCLI()

    def test_setup_parser(self):
        parser = self.cli.setup_parser()
        self.assertEqual(isinstance(parser, argparse.ArgumentParser), True)

    @patch('asb_pl_template.core.AnsibleProjectManager')
    def test_run_init_project(self, mock_manager):
        args = MagicMock()
        args.command = 'init'
        args.init_type = 'project'
        args.project_name = 'test_project'
        args.roles_path = 'test_roles_path'
        args.role_names = ['role1', 'role2']
        args.playbook_name = 'test_playbook.yml'
        args.verbose = False
        args.example = False

        self.cli.run()

        mock_manager.assert_called_once_with(
            project_name='test_project',
            roles_path='test_roles_path',
            role_names=['role1', 'role2'],
            playbook_path=None,
            playbook_name='test_playbook.yml',
            example=False,
            verbose=False
        )

        manager_instance = mock_manager.return_value
        manager_instance.create_project.assert_called_once_with(
            project_name='test_project',
            roles_path='test_roles_path',
            role_names=['role1', 'role2'],
            playbook_name='test_playbook.yml'
        )


class TestAnsibleProjectManager(unittest.TestCase):

    def setUp(self):
        self.manager = AnsibleProjectManager(project_name='test_project')

    @patch('asb_pl_template.core.mkdirs')
    @patch('asb_pl_template.core.check_directory_exists')
    def test_create_role(self, mock_check, mock_mkdirs):
        mock_check.return_value = False
        role_path = 'test_role_path'
        role_names = ['role1', 'role2']
        self.manager.create_role(role_path, role_names)

        mock_mkdirs.assert_any_call(role_path, exist_ok=True)
        for role_name in role_names:
            role_full_path = os.path.join(role_path, role_name)
            mock_mkdirs.assert_any_call(role_full_path, exist_ok=True)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('asb_pl_template.core.mkdirs')
    def test_create_playbook(self, mock_mkdirs, mock_open):
        playbook_path = 'test_playbook_path'
        playbook_name = 'test_playbook.yml'
        self.manager.create_playbook(playbook_path, playbook_name, example=False)

        mock_mkdirs.assert_called_once_with(os.path.abspath(playbook_path), exist_ok=True)
        mock_open.assert_called_once_with(os.path.abspath(os.path.join(playbook_path, playbook_name)), 'w')


if __name__ == '__main__':
    unittest.main()
