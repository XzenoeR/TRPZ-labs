terraform {
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7"
    }
  }
}

provider "libvirt" {
  uri = var.libvirt_uri
}

resource "libvirt_volume" "ubuntu_base" {
  name   = "ubuntu-base.qcow2"
  pool   = var.storage_pool
  source = var.ubuntu_image_url
  format = "qcow2"
}

resource "libvirt_volume" "worker_disk" {
  name           = "worker.qcow2"
  pool           = var.storage_pool
  base_volume_id = libvirt_volume.ubuntu_base.id
  size           = 21474836480 # 20 GB
}

resource "libvirt_volume" "db_disk" {
  name           = "db.qcow2"
  pool           = var.storage_pool
  base_volume_id = libvirt_volume.ubuntu_base.id
  size           = 21474836480 # 20 GB
}

resource "libvirt_network" "lab4_net" {
  name      = "lab4-net"
  mode      = "nat"
  domain    = "lab4.local"
  addresses = ["192.168.100.0/24"]
  autostart = true

  dhcp {
    enabled = true
  }

  dns {
    enabled = true
  }
}

resource "libvirt_cloudinit_disk" "worker_init" {
  name      = "worker-init.iso"
  pool      = var.storage_pool
  user_data = templatefile("${path.module}/cloud-init/worker.yaml.tpl", {
    ansible_ssh_key = var.ansible_ssh_public_key
    student_ssh_key = var.student_ssh_public_key
  })
  network_config = templatefile("${path.module}/cloud-init/network.yaml.tpl", {
    static_ip = "192.168.100.10"
    gateway   = "192.168.100.1"
  })
}

resource "libvirt_cloudinit_disk" "db_init" {
  name      = "db-init.iso"
  pool      = var.storage_pool
  user_data = templatefile("${path.module}/cloud-init/db.yaml.tpl", {
    ansible_ssh_key = var.ansible_ssh_public_key
    student_ssh_key = var.student_ssh_public_key
  })
  network_config = templatefile("${path.module}/cloud-init/network.yaml.tpl", {
    static_ip = "192.168.100.20"
    gateway   = "192.168.100.1"
  })
}

resource "libvirt_domain" "worker" {
  name      = "lab4-worker"
  memory    = 2048
  vcpu      = 2
  autostart = true

  cloudinit = libvirt_cloudinit_disk.worker_init.id

  network_interface {
    network_id     = libvirt_network.lab4_net.id
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.worker_disk.id
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
    autoport    = true
  }
}

resource "libvirt_domain" "db" {
  name      = "lab4-db"
  memory    = 2048
  vcpu      = 2
  autostart = true

  cloudinit = libvirt_cloudinit_disk.db_init.id

  network_interface {
    network_id     = libvirt_network.lab4_net.id
    wait_for_lease = true
  }

  disk {
    volume_id = libvirt_volume.db_disk.id
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
    autoport    = true
  }
}
