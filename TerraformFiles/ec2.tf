resource "aws_instance" "Example1" {
  ami           = var.ubuntu_ami
  instance_type = var.instance_type
  subnet_id     = aws_subnet.subnet1.id
  key_name      = var.key_name

  vpc_security_group_ids      = [aws_security_group.DemoSg.id]
  associate_public_ip_address = true
  user_data                   = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu
  EOF

  tags = {
    Name = "PEP-EC2-1"
    team = "sjce-devops1"
  }
}

resource "aws_instance" "Example2" {
  ami           = var.ubuntu_ami
  instance_type = var.instance_type
  subnet_id     = aws_subnet.subnet2.id
  key_name      = var.key_name

  vpc_security_group_ids = [
    aws_security_group.DemoSg.id
  ]

  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu
  EOF

  tags = {
    Name = "PEP-EC2-2"
    team = "sjce-devops1"
  }
}