output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "dashboard_url" {
  value = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.app_logs.name
}
