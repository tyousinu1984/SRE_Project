# Project タグの値（共通）
variable "project_tag" {}
variable "check_alarm_setting" {}
variable "check_project_setting" {}
variable "check_zabbix_setting" {}

variable "user_server_settings" {
  type = object({
    # インスタンスの数
    count = number
    # Name タグの値
    name = string
    # サブネット ID
    subnet_id = string
    # インスタンスタイプ
    instance_type = string
    #  AMI ID
    ami_id = string
    # 利用するセキュリティグループ一覧
    security_group_ids = list(string)
  })
  description = "求人ユーザー・求人店舗管理 WEB サーバーの情報"
}

variable "admin_server_settings" {
  type = object({
    # インスタンスの数
    count = number
    # Name タグの値
    name = string
    # サブネット ID
    subnet_id = string
    # インスタンスタイプ
    instance_type = string
    #  AMI ID
    ami_id = string
    # 利用するセキュリティグループ一覧
    security_group_ids = list(string)
  })
  description = "大管理 WEB サーバーの情報"
}

variable "member_server_settings" {
  type = object({
    # インスタンスの数
    count = number
    # Name タグの値
    name = string
    # サブネット ID
    subnet_id = string
    # インスタンスタイプ
    instance_type = string
    #  AMI ID
    ami_id = string
    # 利用するセキュリティグループ一覧
    security_group_ids = list(string)
  })
  description = "求人会員・求人会員管理 WEB サーバーの情報"
}


variable "batch_server_settings" {
  type = object({
    # Name タグの値
    name = string
    # サブネット ID
    subnet_id = string
    # インスタンスタイプ
    instance_type = string
    #  AMI ID
    ami_id = string
    # 利用するセキュリティグループ一覧
    security_group_ids = list(string)
  })
  description = "バッチサーバーの情報"
}

variable "mail_server_settings" {
  type = object({
    # Name タグの値
    name = string
    # サブネット ID
    subnet_id = string
    # インスタンスタイプ
    instance_type = string
    #  AMI ID
    ami_id = string
    # 利用するセキュリティグループ一覧
    security_group_ids = list(string)
  })
  description = "メールサーバーの情報"
}


# キーペア名
variable "keypair_name" {}
