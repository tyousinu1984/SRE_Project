locals {
  target_groups = {
    for listener_name, settings in var.target_group_settings : listener_name => {
      name      = settings.tg_name
      priority  = settings.priority
      path_pattern = settings.path_pattern
    }
  }
}

resource "aws_lb_target_group" "target_group" {

  for_each = local.target_groups
  name     = each.value.name
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  target_type = "instance"

  tags = {
    Project = var.project_tag
    CheckAlarmSetting = var.check_alarm_setting
    Stage = var.stage
  }
}

#----------------------------------------------------
# EC2 インスタンスをターゲットグループに登録
#----------------------------------------------------
# 求人ユーザー・求人店舗管理
resource "aws_lb_target_group_attachment" "user_server" {
  count = length(var.target_group_settings.user_server.instances)

  target_group_arn = aws_lb_target_group.target_group["user_server"].arn
  target_id        = var.target_group_settings.user_server.instances[count.index]
  port             = 80
}

# 大管理
resource "aws_lb_target_group_attachment" "admin_server" {
  count = length(var.target_group_settings.admin_server.instances)

  target_group_arn = aws_lb_target_group.target_group["admin_server"].arn
  target_id        = var.target_group_settings.admin_server.instances[count.index]
  port             = 80
}

# 求人会員・求人会員管理
resource "aws_lb_target_group_attachment" "member_server" {
  count = length(var.target_group_settings.member_server.instances)

  target_group_arn = aws_lb_target_group.target_group["member_server"].arn
  target_id        = var.target_group_settings.member_server.instances[count.index]
  port             = 80
}

#----------------------------------------------------
# ALB
#----------------------------------------------------
resource "aws_lb" "alb" {
  depends_on = [ aws_lb_target_group.target_group ]
  name               = var.alb_name
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg]
  subnets            = var.alb_subnets

  enable_deletion_protection = false

  access_logs {
    bucket  = var.s3_bucket_for_log
    prefix  = ""
    enabled = false
  }

  tags = {
    Project = var.project_tag
    CheckAlarmSetting = "NO"
    Stage = var.stage
  }
}


#----------------------------------------------------
# ALB リスナー
#----------------------------------------------------
# 80 リスナー（443 に転送するだけ）
resource "aws_lb_listener" "http" {
  depends_on = [ aws_lb_target_group.target_group, aws_lb.alb ]
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    # HTTPS にリダイレクト
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# 443 リスナー
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn

  # デフォルトアクションを設定
  default_action {
    type = "forward"
    # target_group に転送
    target_group_arn = aws_lb_target_group.target_group["user_server"].arn
  }
}

# 求人ユーザー・求人店舗管理 ALB リスナールール
resource "aws_lb_listener_rule" "user_listener" {

  count =length(var.target_group_settings.user_server.instances)
  listener_arn = aws_lb_listener.https.arn
  priority     = 30

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group["user_server"].arn
  }
  condition {
    path_pattern {
      values = var.target_group_settings.user_server.path_pattern
    }
  }
}

# 大管理  ALB リスナールール
resource "aws_lb_listener_rule" "admin_listener" {

  count =length(var.target_group_settings.admin_server.instances)

  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group["admin_server"].arn
  }

  condition {
    path_pattern {
      values = var.target_group_settings.admin_server.path_pattern
    }
  }

}

# 求人会員・求人会員管理  ALB リスナールール
resource "aws_lb_listener_rule" "member_listener" {
  listener_arn = aws_lb_listener.https.arn
  priority     = var.target_group_settings.member_server.priority

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group["member_server"].arn
  }

  condition {
    path_pattern {
      values = var.target_group_settings.member_server.path_pattern
    }
  }
}

