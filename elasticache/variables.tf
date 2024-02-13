# Project タグの値（共通）
variable "project_tag" {}
variable "check_alarm_setting" {}
variable "check_project_setting" {}
variable "check_zabbix_setting" {}
# クラスター名
variable "replication_group_id" {}

# ノードのタイプ
variable "node_type" {}

# ノードの数
variable "num_cache_clusters" {}

# パラメーターグループ
variable "parameter_group_name" {}

# パラメーターグループのファミリー
variable "parameter_group_family" {}

# エンジンバージョン
variable "engine_version" {}

# サブネットグループ名
variable "subnet_group_name" {}

# サブネットグループIDのリスト
variable "subnet_ids" {}

# セキュリティグループID
variable "security_group_id" {}