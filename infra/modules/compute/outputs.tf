output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "alb_zone_id" {
  value = aws_lb.main.zone_id
}

output "alb_arn" {
  value = aws_lb.main.arn
}

output "target_group_arn" {
  value = aws_lb_target_group.app.arn
}

output "asg_name" {
  value = aws_autoscaling_group.app.name
}

output "ec2_security_group_id" {
  value = aws_security_group.ec2_sg.id
}
