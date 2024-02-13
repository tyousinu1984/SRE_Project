# RDS Aurora クラスター　パラメータグループ
resource "aws_rds_cluster_parameter_group" "cluster_parameter_group" {
  name        = var.db_cluster_parameter_group_name
  family      = var.parameter_group_family

  parameter {
    name  = "character_set_server"
    value = "utf8"
  }

}

# DB インスタンス パラメータグループ
resource "aws_db_parameter_group" "parameter_group" {
  name   = var.db_parameter_group_name
  family = var.parameter_group_family

  parameter {
    name  = "character_set_server"
    value = "utf8"
  }

}

# DB クラスター　インスタンス
resource "aws_rds_cluster_instance" "cluster_instances" {
  count              = 2
  identifier         = "${var.db_instance_name}-${count.index + 1}"
  cluster_identifier = aws_rds_cluster.cluster.id
  instance_class     = var.db_instance_type
  engine             = var.engine
  engine_version     = var.engine_version

  db_parameter_group_name = var.db_parameter_group_name

  auto_minor_version_upgrade = false
  # パブリックアクセシビリティ
  publicly_accessible = true
}





# RDS Aurora クラスター
resource "aws_rds_cluster" "cluster" {
  cluster_identifier = var.db_cluster_name
  engine             = var.engine
  engine_version     = var.engine_version

  availability_zones = var.availability_zones

  database_name   = var.db_name
  master_username = var.db_master_user_name
  master_password = var.db_master_user_password


  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.cluster_parameter_group.name

  # バックアップ保持期間
  backup_retention_period = 5
  # バックアップを実行する時間帯（タイムゾーンは UTC）
  preferred_backup_window = "16:00-17:00"

  #削除保護
  deletion_protection = true
  # CloudWatch logs に吐き出すもの
  enabled_cloudwatch_logs_exports = ["error", "slowquery"]

  # セキュリティグループ
  vpc_security_group_ids = var.db_sgs

  tags = {
    Project = var.project_tag
    CheckAlarmSetting    = var.check_alarm_setting
  }

  lifecycle {
    ignore_changes = [master_password, availability_zones]
  }

}




