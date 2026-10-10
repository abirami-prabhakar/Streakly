# Security Group
resource "aws_security_group" "DemoSg" {
  name   = "Ec2-firewall"
  vpc_id = aws_vpc.vpc.id
}

# SSH
resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.DemoSg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

# HTTP
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.DemoSg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

# HTTPS
resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.DemoSg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

# Outbound
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.DemoSg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
