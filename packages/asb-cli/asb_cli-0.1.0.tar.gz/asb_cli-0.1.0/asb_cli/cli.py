import os
import argparse
import shutil
import sys

from .constants import (
    ROLE_DEFAULTS_TEMPLATE,
    ROLE_TASKS_TEMPLATE,
    ROLE_HANDLERS_TEMPLATE,
    ROLE_META_TEMPLATE,
    ROLE_VARS_TEMPLATE,
    INVENTORY_TEMPLATE,
    PLAYBOOK_TEMPLATE,
)


def create_init_structure(args):
    path = args.path
    project_structure = [
        "group_vars",
        "host_vars",
        "roles",
        "playbooks",
        "inventory",
        "library",
        "filter_plugins",
    ]
    for folder in project_structure:
        full_path = os.path.join(path, folder)
        os.makedirs(full_path, exist_ok=True)
    print("Created project structure: {}".format(path))


def create_role_structure(args):
    path = args.path
    # 获取 path的路径和文件名
    path_abs = os.path.abspath(path)
    path_abs_dirname = os.path.dirname(path_abs)
    path_name = os.path.basename(os.path.normpath(path_abs))
    roles_path = os.path.abspath(os.path.join("roles"))
    roles_path_project = os.path.join(path_abs_dirname, "roles", path_name)
    # 如果 path 是 .或为 空的话，则使用当前目录
    if path == "." or not path:
        print("create role dir {}".format(roles_path))
        os.makedirs(roles_path, exist_ok=True)
        return
    # 如果角色目录已存在，先删除
    if os.path.exists(roles_path_project):
        shutil.rmtree(roles_path_project)
    # 如果当前目录没有 roles 创建 roles
    if not os.path.exists(roles_path_project):
        os.makedirs(roles_path_project)

    role_structure = [
        os.path.join(roles_path_project, "defaults"),
        os.path.join(roles_path_project, "files"),
        os.path.join(roles_path_project, "handlers"),
        os.path.join(roles_path_project, "meta"),
        os.path.join(roles_path_project, "tasks"),
        os.path.join(roles_path_project, "templates"),
        os.path.join(roles_path_project, "vars"),
    ]
    for folder in role_structure:
        os.makedirs(folder, exist_ok=True)
        print("Created directory: {}".format(folder))

    # role 中写入模版
    with open(os.path.join(roles_path_project, "defaults", "main.yml"), "w") as f:
        f.write(ROLE_DEFAULTS_TEMPLATE)
    with open(os.path.join(roles_path_project, "tasks", "main.yml"), "w") as f:
        f.write(ROLE_TASKS_TEMPLATE)
    with open(os.path.join(roles_path_project, "handlers", "main.yml"), "w") as f:
        f.write(ROLE_HANDLERS_TEMPLATE)
    with open(os.path.join(roles_path_project, "meta", "main.yml"), "w") as f:
        f.write(ROLE_META_TEMPLATE)
    with open(os.path.join(roles_path_project, "vars", "main.yml"), "w") as f:
        f.write(ROLE_VARS_TEMPLATE)


def create_playbook(args):
    playbook_name = args.name
    path = args.path
    path_abs = os.path.abspath(path)

    # 判断路径是否为目录
    if os.path.isdir(path_abs):
        playbook_path = os.path.join(path_abs, playbook_name)
    else:
        # 如果路径不是目录，而是文件路径，直接使用
        playbook_path = path_abs
        # 提取文件名
        file_name = os.path.basename(playbook_path)
        # 如果用户输入的路径包含文件名，优先使用该文件名
        if file_name:
            playbook_name = file_name

    # 确保目录存在
    playbook_dir = os.path.dirname(playbook_path)
    if not os.path.exists(playbook_dir):
        os.makedirs(playbook_dir, exist_ok=True)

    with open(playbook_path, "w") as f:
        f.write(PLAYBOOK_TEMPLATE)
    print("Created playbook: {}".format(playbook_path))


def create_inventory():
    inventory_path = "inventory/hosts"
    os.makedirs("inventory", exist_ok=True)
    with open(inventory_path, "w") as f:
        f.write(INVENTORY_TEMPLATE)
    print("Created inventory file: {}".format(inventory_path))


def clean_project():
    folders_to_remove = [
        "group_vars",
        "host_vars",
        "roles",
        "playbooks",
        "inventory",
        "library",
        "filter_plugins",
    ]
    for folder in folders_to_remove:
        if os.path.exists(folder):
            # 使用 shutil.rmtree 处理非空目录
            import shutil
            shutil.rmtree(folder)
            print("Removed directory: {}".format(folder))


def main():
    parser = argparse.ArgumentParser(description="asb_cli: A CLI tool for managing Ansible projects.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command: init
    parser_init = subparsers.add_parser("init", help="Create a standard Ansible project directory.")
    parser_init.add_argument("path", nargs="?", default=".",
                             help="Path to initialize the project (default: current directory).")
    parser_init.set_defaults(func=create_init_structure)

    # Sub-command: role
    parser_role = subparsers.add_parser(
        "role", help="Create a roles directory structure."
    )
    parser_role.add_argument("path", nargs="?", default=".",
                             help="Path to create the role structure (default: current directory ).")
    parser_role.set_defaults(func=create_role_structure)

    # Sub-command: playbook
    parser_playbook = subparsers.add_parser(
        "playbook", help="Create a single Ansible playbook."
    )
    parser_playbook.add_argument(
        "--name", default="site.yml", help="Name of the playbook file."
    )
    parser_playbook.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to create the playbook (default: current directory ).",
    )
    parser_playbook.set_defaults(func=create_playbook)

    # Sub-command: inventory
    parser_inventory = subparsers.add_parser(
        "inventory", help="Create a standard inventory file."
    )
    parser_inventory.set_defaults(func=create_inventory)

    # Sub-command: clean
    parser_clean = subparsers.add_parser(
        "clean", help="Clean up generated directories and files."
    )
    parser_clean.set_defaults(func=clean_project)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    # 直接调用 args.func 并传入 args
    args.func(args)


if __name__ == "__main__":
    main()
