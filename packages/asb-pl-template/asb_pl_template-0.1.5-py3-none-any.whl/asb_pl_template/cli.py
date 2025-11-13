#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .core import AnsibleProjectManager
from .constants import banner, VERSION


class ASBPLTemplateCLI:
    def __init__(self):
        self.parser = self.setup_parser()

    def setup_parser(self):
        parser = argparse.ArgumentParser(prog="asb-pl-template", description="Ansible Project Manager\n" + banner,
                                         epilog="please use -h/--help for more information",
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}",
                            help="Show the version and exit")
        parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
        subparsers = parser.add_subparsers(dest="command", required=True)

        # init 子命令
        init_parser = subparsers.add_parser("init", help="Initialize a project, role, or playbook")
        init_subparsers = init_parser.add_subparsers(dest="init_type", required=True)

        # init project 子命令
        project_parser = init_subparsers.add_parser("project", help="Create a new project")
        project_parser.add_argument("project_name", help="Name or path of the project")
        project_parser.add_argument("--roles-path", help="Path to the roles directory")
        project_parser.add_argument("--role-names", nargs='+', help="Names of the roles")
        project_parser.add_argument("--playbook-name", help="Name of the playbook")

        # init role 子命令
        role_parser = init_subparsers.add_parser("role", help="Create a new role")
        role_parser.add_argument("--role_path", dest="role_path", default=".", help="Path to the role directory")
        role_parser.add_argument("role_names", nargs='*', default=['role_template'], help="Names of the roles")

        # init playbook 子命令
        playbook_parser = init_subparsers.add_parser("playbook", help="Create a new playbook")
        playbook_parser.add_argument("--playbook_path", dest="playbook_path", default=".",
                                     help="Path to the playbook directory")
        playbook_parser.add_argument("playbook_name", nargs='?', default='site.yml',
                                     help="Name or path of the playbook")
        playbook_parser.add_argument("--example", action="store_true", help="Create a simple playbook with example")

        return parser

    def create_manager(self, args):
        return AnsibleProjectManager(
            project_name=getattr(args, 'project_name', None),
            roles_path=getattr(args, 'roles_path', None),
            role_names=getattr(args, 'role_names', []),
            playbook_path=getattr(args, 'playbook_path', None),
            playbook_name=getattr(args, 'playbook_name', None),
            example=getattr(args, 'example', False),
            verbose=args.verbose
        )

    def run(self):
        args = self.parser.parse_args()
        if args.command == "init":
            manager = self.create_manager(args)
            if args.init_type == "project":
                manager.create_project(
                    project_name=args.project_name,
                    roles_path=args.roles_path,
                    role_names=args.role_names,
                    playbook_name=args.playbook_name
                )
            elif args.init_type == "role":
                if args.role_names is None:
                    args.role_names = ['role_template']
                if len(args.role_names) == 1:
                    if "".join(args.role_names) == ".":
                        args.role_names = ["role_template"]
                # print(args.role_path, args.role_names)
                manager.create_role(
                    role_path=args.role_path,
                    role_names=args.role_names
                )
            elif args.init_type == "playbook":
                manager.create_playbook(
                    playbook_path=args.playbook_path,
                    playbook_name=args.playbook_name,
                    example=args.example
                )


def main():
    cli = ASBPLTemplateCLI()
    cli.run()


if __name__ == "__main__":
    main()
