#----------------------------------------------------
# 出力
#----------------------------------------------------
output "alb_arn" {
  value = aws_lb.alb.arn
}


output "alb_dns_name" {
  value = aws_lb.alb.dns_name
}

output "alb_hosted_zone_id" {
  value = aws_lb.alb.zone_id
}
