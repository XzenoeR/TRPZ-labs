variable "libvirt_uri" {
  description = "URI підключення до libvirt (KVM)"
  type        = string
  default     = "qemu:///system"
}

variable "storage_pool" {
  description = "Назва storage pool для libvirt"
  type        = string
  default     = "default"
}

variable "ubuntu_image_url" {
  description = "URL або локальний шлях до Ubuntu 22.04 cloud image"
  type        = string
  default     = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
}

variable "ansible_ssh_public_key" {
  description = "SSH публічний ключ для користувача ansible"
  type        = string
}

variable "student_ssh_public_key" {
  description = "SSH публічний ключ студента"
  type        = string
}
