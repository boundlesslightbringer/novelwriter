resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "novelwriter-vpc"
  }
}

# Public subnet 1
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.0.0/24"
  availability_zone       = "${var.aws-region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "novelwriter-public-subnet-1"
  }
}

# Public subnet 2 (required for ALB)
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws-region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "novelwriter-public-subnet-2"
  }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "novelwriter-private-subnet"
  }
}

# Internet Gateway for public subnet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "novelwriter-igw"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  vpc = true

  tags = {
    Name = "novelwriter-nat-eip"
  }

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateway for private subnet internet access
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "novelwriter-nat-gateway"
  }

  depends_on = [aws_internet_gateway.main]
}

# Public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "novelwriter-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Private route table with NAT Gateway route
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "novelwriter-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "s3_endpoint" {
  name        = "novelwriter-s3-endpoint-sg"
  description = "Controls access to the S3 VPC Endpoint"
  vpc_id      = aws_vpc.main.id

  # Allow traffic from frontend and backend security groups
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name = "novelwriter-s3-endpoint-sg"
  }
}

resource "aws_security_group" "bedrock_endpoint" {
  name        = "novelwriter-bedrock-endpoint-sg"
  description = "Controls access to the Bedrock VPC Endpoint"
  vpc_id      = aws_vpc.main.id

  # Allow traffic from the backend security group
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name = "novelwriter-bedrock-endpoint-sg"
  }
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws-region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = {
    Name = "novelwriter-s3-endpoint"
  }
}

resource "aws_vpc_endpoint" "bedrock" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws-region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids = [
    aws_subnet.private.id
  ]

  security_group_ids = [
    aws_security_group.bedrock_endpoint.id,
  ]

  tags = {
    Name = "novelwriter-bedrock-endpoint"
  }
}

# This security group controls traffic to/from the ALB
# Ingress: Allows HTTP/HTTPS from the public internet 
# Egress: Allows traffic to frontend and backend services for request forwarding

resource "aws_security_group" "alb" {
  name        = "novelwriter-alb-sg"
  description = "Security group for Application Load Balancer - controls public internet access"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "novelwriter-alb-sg"
  }
}

# Allow HTTP traffic from the internet to ALB
resource "aws_security_group_rule" "alb_http_ingress" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTP traffic from the internet"
}

# Allow HTTPS traffic from the internet to ALB
resource "aws_security_group_rule" "alb_https_ingress" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTPS traffic from the internet"
}

# Allow ALB to forward traffic to frontend (React) on port 80
resource "aws_security_group_rule" "alb_to_frontend_egress" {
  type                     = "egress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.frontend.id
  security_group_id        = aws_security_group.alb.id
  description              = "Allow ALB to forward traffic to React frontend"
}

# Allow ALB to forward traffic to backend (FastAPI) on port 7000
resource "aws_security_group_rule" "alb_to_backend_egress" {
  type                     = "egress"
  from_port                = 7000
  to_port                  = 7000
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.backend.id
  security_group_id        = aws_security_group.alb.id
  description              = "Allow ALB to forward traffic to FastAPI backend"
}

# This security group controls traffic to the React application
# Ingress: Only accepts traffic from the ALB 
# Egress: Allows necessary outbound traffic 

resource "aws_security_group" "frontend" {
  name        = "novelwriter-frontend-sg"
  description = "Security group for React frontend - only accepts traffic from ALB"
  vpc_id      = aws_vpc.main.id

  # Allow all outbound traffic for frontend needs (S3, CDN, external APIs, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic from frontend"
  }

  tags = {
    Name = "novelwriter-frontend-sg"
  }
}

# Only allow traffic from ALB to frontend on port 80
resource "aws_security_group_rule" "frontend_from_alb" {
  type                     = "ingress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
  security_group_id        = aws_security_group.frontend.id
  description              = "Allow traffic from ALB only - prevents direct access bypass"
}

# Allow SSH traffic from my public IP to frontend
resource "aws_security_group_rule" "frontend_ssh_ingress" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [format("%s/32", var.LOCAL_PUBLIC_IP)]
  security_group_id = aws_security_group.frontend.id
  description       = "Allow SSH traffic from my local IP to frontend"
}

# ============================================================================
# Backend (FastAPI) Security Group
# ============================================================================
# This security group controls traffic to the FastAPI application
# Ingress: Only accepts traffic from the ALB (prevents direct access bypass)
# Egress: Allows necessary outbound traffic (RDS, external APIs, Bedrock, etc.)

resource "aws_security_group" "backend" {
  name        = "novelwriter-backend-sg"
  description = "Security group for FastAPI backend - only accepts traffic from ALB"
  vpc_id      = aws_vpc.main.id

  # Allow all outbound traffic for backend needs (RDS, Bedrock, Pinecone, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic from backend"
  }

  tags = {
    Name = "novelwriter-backend-sg"
  }
}

# Only allow traffic from ALB to backend on port 7000
resource "aws_security_group_rule" "backend_from_alb" {
  type                     = "ingress"
  from_port                = 7000
  to_port                  = 7000
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
  security_group_id        = aws_security_group.backend.id
  description              = "Allow traffic from ALB only - prevents direct access bypass"
}

resource "aws_lb" "webapp" {
  name               = "webapp"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public.id, aws_subnet.public_2.id]

  tags = {
    Name = "webapp"
  }
}

resource "aws_lb_target_group" "frontend" {
  name                          = "frontend-target-group"
  port                          = 80
  protocol                      = "HTTP"
  target_type                   = "instance"
  vpc_id                        = aws_vpc.main.id
  load_balancing_algorithm_type = "round_robin"

  tags = {
    Name = "frontend-target-group"
  }

  health_check {
    path                = "/"            # home page
    port                = "traffic-port" # Use same port as traffic (80)
    protocol            = "HTTP"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }
}

resource "aws_lb_target_group" "backend" {
  name                          = "backend-target-group"
  port                          = 7000
  protocol                      = "HTTP"
  target_type                   = "instance"
  vpc_id                        = aws_vpc.main.id
  load_balancing_algorithm_type = "round_robin"

  tags = {
    Name = "backend-target-group"
  }

  health_check {
    path                = "/docs"        # FastAPI docs endpoint
    port                = "traffic-port" # Use same port as traffic (7000)
    protocol            = "HTTP"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }
}

# Attach React frontend instance to the frontend target group
resource "aws_lb_target_group_attachment" "react_frontend" {
  target_group_arn = aws_lb_target_group.frontend.arn
  target_id        = aws_instance.react-server.id
  port             = 80
}

# Attach FastAPI backend instance to the backend target group
resource "aws_lb_target_group_attachment" "fastapi_backend" {
  target_group_arn = aws_lb_target_group.backend.arn
  target_id        = aws_instance.fastapi-server.id
  port             = 7000
}

# Single listener on port 80 for path-based routing
resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.webapp.arn
  port              = "80"
  protocol          = "HTTP"

  # Default action: forward all unmatched requests to frontend
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# Listener rule: route API endpoints to backend
resource "aws_lb_listener_rule" "backend" {
  listener_arn = aws_lb_listener.main.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = [
        "/api/*",
        "/docs",
        "/docs/*",
        "/openapi.json",
        "/redoc"
      ]
    }
  }
}


# Security group for chroma server instances
resource "aws_security_group" "chroma_server" {
  name        = "novelwriter-chroma-server-sg"
  description = "Controls access for the chroma server"
  vpc_id      = aws_vpc.main.id

  # Allows all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "novelwriter-chroma-server-sg"
  }
}

# Separate ingress rule to avoid circular dependency
resource "aws_security_group_rule" "backend_to_chroma" {
  type                     = "ingress"
  from_port                = 8000
  to_port                  = 8000
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.backend.id
  security_group_id        = aws_security_group.chroma_server.id
  description              = "Allow Chroma access from backend security group"
}