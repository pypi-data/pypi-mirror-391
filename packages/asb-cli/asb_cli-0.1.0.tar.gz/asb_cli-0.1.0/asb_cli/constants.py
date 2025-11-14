# Constants for template contents

ROLE_DEFAULTS_TEMPLATE = """# defaults/main.yml
# Default variables for the role
"""

ROLE_TASKS_TEMPLATE = """# tasks/main.yml
# Tasks for the role
"""

ROLE_HANDLERS_TEMPLATE = """# handlers/main.yml
# Handlers for the role
"""

ROLE_META_TEMPLATE = """# meta/main.yml
# Metadata for the role
"""

ROLE_VARS_TEMPLATE = """# vars/main.yml
# Variables for the role
"""

INVENTORY_TEMPLATE = """# inventory/hosts
[all]
localhost ansible_connection=local
"""

PLAYBOOK_TEMPLATE = """---
- name: Example Playbook
  hosts: all
  tasks:
    - name: Example task
      debug:
        msg: "Hello, Ansible!"
"""
