# by Zhang Xinyu
terraform {
  required_version = ">=0.14.6"
}

# staging環境用 アカウント
provider "aws" {
  region = "ap-northeast-1"
  alias  = "staging"
  # IAM ロールを引き受ける
  assume_role {
    role_arn = var.IamRoleArn
  }
}

#---------------------------------------
# EC2 インスタンス 
#---------------------------------------
module "ec2" {
  source = "./ec2"
  # タグ
  project_tag     = var.ProjectTag
  check_alarm_setting = var.CheckAlarmSetting
  check_project_setting = var.CheckProjectSetting
  check_zabbix_setting = var.CheckZabbixSetting
  # キーペア名
  keypair_name = var.KeyPair

  user_server_settings = var.EC2_UserServerSettings
  admin_server_settings = var.EC2_AdminServerSettings
  member_server_settings = var.EC2_MemberServerSettings
  batch_server_settings = var.EC2_BatchServerSettings
  mail_server_settings = var.EC2_MailServerSettings

}

#---------------------------------------
# ALB
#---------------------------------------
module "alb" {
  source = "./alb"

  project_tag           = var.ProjectTag
  check_alarm_setting   = var.CheckAlarmSetting
  stage                 = var.Stage
  alb_name              = "${var.ResourceNamePrefix}-${var.ALBName}"

  target_group_settings        = {
    user_server = {
      tg_name =var.TargetGroupSettings.user_server.tg_name
      priority = var.TargetGroupSettings.user_server.priority
      path_pattern = var.TargetGroupSettings.user_server.path_pattern
      instances = module.ec2.user_server_instance_ids
    }
    admin_server = {
      tg_name = var.TargetGroupSettings.admin_server.tg_name
      priority = var.TargetGroupSettings.admin_server.priority
      path_pattern = var.TargetGroupSettings.admin_server.path_pattern
      instances = module.ec2.admin_server_instance_ids
    }
    member_server = {
      tg_name= var.TargetGroupSettings.member_server.tg_name
      priority = var.TargetGroupSettings.member_server.priority
      path_pattern = var.TargetGroupSettings.member_server.path_pattern
      instances = module.ec2.member_server_instance_ids
    }
  }

  alb_subnets           = var.SubnetIds
  vpc_id                = var.VpcId
  alb_sg                = var.ALBSecurityGroupId
  s3_bucket_for_log     = ""
  certificate_arn       = var.ALBCertificateArn
}

#------------------------------------------------
# RDS
#------------------------------------------------
module "rds" {
  source = "./rds"

  # タグ
  project_tag     = var.ProjectTag
  check_alarm_setting = var.CheckAlarmSetting
  check_project_setting = var.CheckProjectSetting
  check_zabbix_setting = var.CheckZabbixSetting

  db_cluster_name  = var.DbClusterName
  db_instance_name = var.DbInstanceName
  engine_version   = var.EngineVersion
  engine           = var.Engine
  db_instance_type = var.DbInstanceType

  db_name             = var.DbName
  db_master_user_name = var.DbMasterUserName
  
  db_master_user_password = var.DbMasterUserPassword

  db_sgs = var.DbSgs 
  availability_zones = var.SubnetIds
  db_cluster_parameter_group_name = var.DbClusterParameterGroupName
  db_parameter_group_name         = var.DbParameterGroupName
  parameter_group_family= var.ParameterGroupFamily
}

#---------------------------------------
# ElastiCache
#---------------------------------------
module "elasticache" {
  source = "./elasticache"

  project_tag     = var.ProjectTag
  check_alarm_setting = var.CheckAlarmSetting
  check_project_setting = var.CheckProjectSetting
  check_zabbix_setting = var.CheckZabbixSetting

  replication_group_id                  = var.ElastiCacheReplicationGroupId
  node_type                             = var.ElastiCacheNodeType
  num_cache_clusters                    = var.ElastiCacheNumCacheClusters
  parameter_group_name                  = var.ElastiCacheParameterGroupName
  parameter_group_family                = var.ElastiCacheParameterGroupFamily
  engine_version                        = var.ElastiCacheEngineVersion
  subnet_group_name                     = var.ElastiCacheSubnetGroupName
  security_group_id                     = var.ElastiCacheSecurityGroupId
  subnet_ids                            = var.SubnetIds
}


#---------------------------------------
# S3
#---------------------------------------
module "s3" {
  source = "./s3"

  project_tag    = var.ProjectTag
  s3_bucket_name = var.S3BucketName
  s3_bucket_acl  = var.S3BucketAcl
}


