output "waf_arn" {
  value = aws_wafv2_web_acl.main.arn
}

output "ec2_security_group_id" {
  value = aws_security_group.ec2_sg.id
}

output "alb_security_group_id" {
  value = aws_security_group.alb_sg.id
}

output "redis_security_group_id" {
  value = aws_security_group.redis_sg.id
}

output "aurora_security_group_id" {
  value = aws_security_group.aurora_sg.id
}
