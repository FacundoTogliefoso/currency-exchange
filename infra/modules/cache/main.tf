resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "${var.name}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = var.tags
}

resource "aws_security_group" "redis_sg" {
  name        = "${var.name}-sg"
  description = "Redis security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${var.name}-rg"
  description                = "Redis replication group for currency exchange"

  node_type                  = "cache.r6g.large"
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true

  engine                    = "redis"
  engine_version           = "7.2"
  port                     = 6379
  parameter_group_name     = "default.redis7"

  subnet_group_name        = aws_elasticache_subnet_group.redis_subnet_group.name
  security_group_ids       = [aws_security_group.redis_sg.id]

  tags = var.tags
}
