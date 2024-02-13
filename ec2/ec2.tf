###########################
# 求人ユーザー・求人店舗管理
##########################
# Web サーバー
resource "aws_instance" "user_server" {
    count                  = var.user_server_settings.count
    ami                    = var.user_server_settings.ami_id
    instance_type          = var.user_server_settings.instance_type
    vpc_security_group_ids = var.user_server_settings.security_group_ids
    subnet_id              = var.user_server_settings.subnet_id

    key_name               = var.keypair_name

    tags = {
        Name                 = format(var.user_server_settings.name, count.index+1)
        Project              = var.project_tag
        CheckAlarmSetting    = var.check_alarm_setting
        CheckProjectSetting  = var.check_project_setting
        CheckZabbixSetting   = var.check_zabbix_setting
    }
}

# EIP
resource "aws_eip" "eip_user_server" {
    count                  = var.user_server_settings.count
    instance              = aws_instance.user_server[count.index].id
    domain                = "vpc"
    public_ipv4_pool      = "amazon"
}


###########################
# 大管理
##########################
# Web サーバー
resource "aws_instance" "admin_server" {
    count                  = var.admin_server_settings.count
    ami                    = var.admin_server_settings.ami_id
    instance_type          = var.admin_server_settings.instance_type
    vpc_security_group_ids = var.admin_server_settings.security_group_ids
    subnet_id              = var.admin_server_settings.subnet_id

    key_name = var.keypair_name

    tags = {
        Name                 = format(var.admin_server_settings.name, count.index+1)
        Project              = var.project_tag
        CheckAlarmSetting    = var.check_alarm_setting
        CheckProjectSetting  = var.check_project_setting
        CheckZabbixSetting   = var.check_zabbix_setting
    }
}

# EIP
resource "aws_eip" "eip_web_admin" {
    count                  = var.admin_server_settings.count
    instance               = aws_instance.admin_server[count.index].id
    domain                 = "vpc"
    public_ipv4_pool       = "amazon"
}


###########################
# 求人会員・求人会員管理
##########################
# Web サーバー
resource "aws_instance" "member_server" {
    count                  = var.member_server_settings.count
    ami                    = var.member_server_settings.ami_id
    instance_type          = var.member_server_settings.instance_type
    vpc_security_group_ids = var.member_server_settings.security_group_ids
    subnet_id              = var.member_server_settings.subnet_id

    key_name = var.keypair_name

    tags = {
        Name                 = format(var.user_server_settings.name, count.index+1)
        Project              = var.project_tag
        CheckAlarmSetting    = var.check_alarm_setting
        CheckProjectSetting  = var.check_project_setting
        CheckZabbixSetting   = var.check_zabbix_setting
    }
}

# EIP
resource "aws_eip" "eip_member_server" {
    count                  = var.member_server_settings.count
    instance               = aws_instance.member_server[count.index].id
    domain                 = "vpc"
    public_ipv4_pool       = "amazon"
}

##########################
# バッチサーバー
##########################
# サーバー
resource "aws_instance" "batch_server" {
  ami                    = var.batch_server_settings.ami_id
  instance_type          = var.batch_server_settings.instance_type
  vpc_security_group_ids = var.batch_server_settings.security_group_ids
  subnet_id              = var.batch_server_settings.subnet_id

  key_name = var.keypair_name

  tags = {
    Name                 = var.batch_server_settings.name
    Project              = var.project_tag
    CheckAlarmSetting    = var.check_alarm_setting
    CheckProjectSetting  = var.check_project_setting
    CheckZabbixSetting   = var.check_zabbix_setting
  }

}

# EIP
resource "aws_eip" "eip_batch_server" {
    instance               = aws_instance.batch_server.id
    domain                 = "vpc"
    public_ipv4_pool       = "amazon"
}

##########################
# メールサーバー
##########################
# サーバー
resource "aws_instance" "mail_server" {
    ami                    = var.mail_server_settings.ami_id
    instance_type          = var.mail_server_settings.instance_type
    vpc_security_group_ids = var.mail_server_settings.security_group_ids
    subnet_id              = var.mail_server_settings.subnet_id

    key_name = var.keypair_name

    tags = {
        Name                 = var.mail_server_settings.name
        Project              = var.project_tag
        CheckAlarmSetting    = var.check_alarm_setting
        CheckProjectSetting  = var.check_project_setting
        CheckZabbixSetting   = var.check_zabbix_setting
    }

}

# EIP
resource "aws_eip" "eip_mail_server" {
    instance               = aws_instance.mail_server.id
    domain                 = "vpc"
    public_ipv4_pool       = "amazon"
}