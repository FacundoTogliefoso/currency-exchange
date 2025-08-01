resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "${var.name}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = var.tags
}

resource "aws_security_group" "aurora_sg" {
  name        = "${var.name}-sg"
  description = "Aurora security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 3306
    to_port     = 3306
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

resource "aws_rds_cluster" "aurora" {
  cluster_identifier     = "${var.name}-cluster"
  engine                 = "aurora-mysql"
  engine_mode           = "provisioned"
  engine_version        = "8.0.mysql_aurora.3.05.2"
  database_name         = var.database_name
  master_username       = var.master_username
  master_password       = var.master_password

  db_subnet_group_name   = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids = [aws_security_group.aurora_sg.id]

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  serverlessv2_scaling_configuration {
    max_capacity = 16
    min_capacity = 0.5
  }

  tags = var.tags
}

resource "aws_rds_cluster_instance" "aurora_instances" {
  count              = 2
  identifier         = "${var.name}-instance-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version

  tags = var.tags
}
