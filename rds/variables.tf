# Project タグの値（共通）
variable "project_tag" {}
variable "check_alarm_setting" {}
variable "check_project_setting" {}
variable "check_zabbix_setting" {}

# Aurora エンジンのバージョン
variable "engine_version" {
  default = "5.7.mysql_aurora.2.09.2"
}

variable "parameter_group_family" {
  
}
# Aurora エンジン
# aurora: Aurora 1.x
# aurora-mysql: Aurora 2.x
# https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Updates.20180206.html#AuroraMySQL.Updates.20180206.CLI
variable "engine" {
  default = "aurora"
}

variable "db_instance_type" {}

# Aurora DB クラスター名
variable "db_cluster_name" {}

# Aurora DB インスタンス名
variable "db_instance_name" {}

# DBの名前
variable "db_name" {}

variable "db_master_user_name" {
  default = "root"
}
variable "db_master_user_password" {}

# DB のセキュリティグループのID一覧
variable "db_sgs" {
  default = []
}

# マルチAZ
variable "availability_zones" {
  
}

# DB クラスター用のパラメータグループ名
variable "db_cluster_parameter_group_name" {}
# DB インスタンス用のパラメータグループ名
variable "db_parameter_group_name" {}