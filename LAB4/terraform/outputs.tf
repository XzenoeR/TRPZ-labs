output "worker_ip" {
  description = "IP-адреса VM1 (worker)"
  value       = libvirt_domain.worker.network_interface[0].addresses[0]
}

output "db_ip" {
  description = "IP-адреса VM2 (db)"
  value       = libvirt_domain.db.network_interface[0].addresses[0]
}

output "ansible_inventory" {
  description = "Готовий Ansible inventory для копіювання в ansible/inventory.ini"
  value       = <<-EOT
    [workers]
    worker ansible_host=${libvirt_domain.worker.network_interface[0].addresses[0]} ansible_user=ansible ansible_ssh_private_key_file=~/.ssh/ansible_id_rsa

    [db]
    db ansible_host=${libvirt_domain.db.network_interface[0].addresses[0]} ansible_user=ansible ansible_ssh_private_key_file=~/.ssh/ansible_id_rsa

    [all:vars]
    ansible_python_interpreter=/usr/bin/python3
  EOT
}
