
hostname: lab4-worker
fqdn: lab4-worker.lab4.local
manage_etc_hosts: true

users:
  - name: ansible
    gecos: "Ansible Automation User"
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: sudo
    lock_passwd: true
    ssh_authorized_keys:
      - ${ansible_ssh_key}

  - name: student
    gecos: "Student User"
    shell: /bin/bash
    sudo: ALL=(ALL:ALL) ALL
    groups: sudo
    lock_passwd: false

packages:
  - python3
  - python3-pip
  - python3-venv
  - curl
  - git
  - ufw

package_update: true
package_upgrade: true

ssh_pwauth: true
disable_root: true

runcmd:
  - echo "student:12345678" | chpasswd
  - mkdir -p /home/student/.ssh
  - echo "${student_ssh_key}" >> /home/student/.ssh/authorized_keys
  - chown -R student:student /home/student/.ssh
  - chmod 700 /home/student/.ssh
  - chmod 600 /home/student/.ssh/authorized_keys
  - ufw allow 22/tcp
  - ufw allow 80/tcp
  - ufw --force enable
