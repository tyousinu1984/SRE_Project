# Project タグの値（共通）
variable "project_tag" {
  description = "Project タグの値"  
}

variable "check_alarm_setting" {}

variable "stage" {
  default = "dev"
  description = "ステージ。 dev/prod/staging のいずれか"
}

variable "alb_name" {
  description = "ALB の名前"
}

# variable "tg_names" {
#   description = "ターゲットグループの名前"
# }


# ALB が使用できるサブネット一覧
variable "alb_subnets" {}

variable "vpc_id" {}


# セキュリティグループ
variable "alb_sg" {}

# 使用する ACM SSL 証明書の ARN
variable "certificate_arn" {}

# アクセスログを保存する S3 バケット名
variable "s3_bucket_for_log" {}

# ---------------------------------
#  ターゲットグループに登録するインスタンスの情報
# ---------------------------------
variable "target_group_settings" {
  description = "ALB でのルーティングの条件に利用するパス一覧"
  type = map(object({
    tg_name =string
    priority    = number
    instances = list(string)
    path_pattern  = list(string)
    }))
}