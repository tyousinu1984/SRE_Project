resource "aws_elasticache_parameter_group" "redis_parameter_group" {
  name   = var.subnet_group_name
  family = var.parameter_group_family

  parameter {
    name  = "activerehashing"
    value = "yes"
  }

  parameter {
    name  = "min-slaves-to-write"
    value = "2"
  }
}

resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = var.subnet_group_name
  subnet_ids = var.subnet_ids
}


resource "aws_elasticache_replication_group" "redis" {
  automatic_failover_enabled  = true
  replication_group_id        = var.replication_group_id
  description                 = var.replication_group_id
  node_type                   = var.node_type
  num_cache_clusters          = var.num_cache_clusters
  parameter_group_name        = aws_elasticache_parameter_group.redis_parameter_group.name
  multi_az_enabled            = true
  engine                      = "redis"
  engine_version              = var.engine_version
  subnet_group_name           = aws_elasticache_subnet_group.redis_subnet_group.name
  security_group_ids          = [ var.security_group_id ]
  port                        = 6379

  tags = {
    Project = var.project_tag
    CheckAlarmSetting    = var.check_alarm_setting
    CheckProjectSetting  = var.check_project_setting
    CheckZabbixSetting   = var.check_zabbix_setting
    Name = var.replication_group_id


  }
}


