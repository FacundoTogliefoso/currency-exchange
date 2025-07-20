output "aurora_cluster_endpoint" {
  value = aws_rds_cluster.aurora.endpoint
}

output "aurora_reader_endpoint" {
  value = aws_rds_cluster.aurora.reader_endpoint
}

output "aurora_port" {
  value = aws_rds_cluster.aurora.port
}

output "aurora_database_name" {
  value = aws_rds_cluster.aurora.database_name
}

output "aurora_security_group_id" {
  value = aws_security_group.aurora_sg.id
}
