
# egando as zonas de disponibilidade disponíveis na região atual
data "aws_availability_zones" "available" {}
# Criando a VPC
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "globo-vpc"
  }
}

# Criando Internet Gateway (Apenas para a Subnet Pública)
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "globo-igw"
  }
}

# Criando Subnet Pública (Para Load Balancer ou Bastion Host)
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "globo-public-subnet"
  }


# Criando Subnet Pública (Para Load Balancer ou Bastion Host)
resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "globo-public-subnet-2"
  }
}

# Criando Tabela de Rotas Pública
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "globo-public-rt"
  }
}

# Criando Rota para Internet na Tabela de Rotas Pública
resource "aws_route" "public_route" {
  route_table_id         = aws_route_table.public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

# Associando a Subnet Pública à Tabela de Rotas Pública
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# Associando a Subnet Pública à Tabela de Rotas Pública
resource "aws_route_table_association" "public_assoc_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# Criando Subnet Privada (Usada pelo ECS Fargate)
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = false # Sem IP público

  tags = {
    Name = "globo-private-subnet"
  }
}

# Criando Tabela de Rotas Privada (Sem acesso à internet)
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "globo-private-rt"
  }
}

# Associando a Subnet Privada à Tabela de Rotas Privada (Sem NAT)
resource "aws_route_table_association" "private_assoc" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_rt.id
}

# Criando VPC Endpoint para S3 (Permite acesso ao S3 sem Internet)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [aws_route_table.private_rt.id]

  tags = {
    Name = "globo-s3-endpoint"
  }
}
