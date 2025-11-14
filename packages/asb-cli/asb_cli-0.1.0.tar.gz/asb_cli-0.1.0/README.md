# asb_cli

`asb_cli` 是一个用于管理 Ansible 项目的命令行工具。

## 功能
- `asb_cli init`: 创建一个标准的 Ansible 项目目录。
- `asb_cli role`: 创建一个类似 `ansible-galaxy` 的 roles 目录结构。
- `asb_cli playbook`: 创建一个单独的 Ansible playbook 文件。

## 安装
```bash
python setup.py develop
# 或者使用 pip 安装
pip install -e .
```

## 使用
```bash
# project
asb_cli init .
asb_cli init ./myprojkect
asb_cli init ../myprojkect
asb_cli init demo1
asb_cli init /tmp/test/demo1

# role
asb_cli role .
asb_cli role demo2
asb_cli role ../demo10
asb_cli role /tmp/test/demo1

# playbook
asb_cli playbook --name site.yml .
asb_cli playbook --name custom.yml ./playbooks
# 在指定绝对路径创建名为 prod.yml 的 playbook
asb_cli playbook --name prod.yml /tmp/test/playbooks
# 直接指定文件路径创建 playbook
asb_cli playbook --name custom.yml ./playbooks/custom.yml
```
