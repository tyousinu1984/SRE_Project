# assume role する IAM ロールの ARN
IamRoleArn = "arn:aws:iam::840277471863:role/cor_administrators"

# ホストゾーン ID
HostZoneID="Z0771004319FN6L1PBQEH"

# 共通変数
Stage = "staging"
ProjectTag="ranking-deli.jp"
ResourceNamePrefix = "staging-hostjob-jp"
CheckAlarmSetting    = "NO"
CheckProjectSetting  = "NO"
CheckZabbixSetting   = "NO"

#VPCID
VpcId="vpc-d434fcb1"


#-------------------------------------------------
# EC2
#-------------------------------------------------
KeyPair="staging-hostjob.jp"
# 求人ユーザー・求人店舗管理
EC2_UserServerSettings= {
    # インスタンスの数
    count = 2
    # Name タグの値
    name = "staging-web-user%s.hostjob.jp"
    # サブネット ID
    subnet_id = "subnet-f919c58e"
    # インスタンスタイプ
    instance_type = "t3.small"
    #  AMI ID
    ami_id = "ami-07c09f34831338806"
    # 利用するセキュリティグループ一覧
    security_group_ids = [ "sg-00c804bf7618868e9" ]
}

# 大管理
EC2_AdminServerSettings= {
    # インスタンスの数
    count = 2
    # Name タグの値
    name = "staging-web-admin%s.hostjob.jp"
    # サブネット ID
    subnet_id = "subnet-f919c58e"
    # インスタンスタイプ
    instance_type = "t3.micro"
    #  AMI ID
    ami_id = "ami-05f58381acd06964c"
    # 利用するセキュリティグループ一覧
    security_group_ids = [ "sg-00c804bf7618868e9" ]
}

# 求人会員・求人会員管理
EC2_MemberServerSettings= {
    # インスタンスの数
    count = 2
    # Name タグの値
    name = "staging-web-member%s.hostjob.jp"
    # サブネット ID
    subnet_id = "subnet-f919c58e"
    # インスタンスタイプ
    instance_type = "t3.micro"
    #  AMI ID
    ami_id = "ami-05f58381acd06964c"
    # 利用するセキュリティグループ一覧
    security_group_ids = [ "sg-00c804bf7618868e9" ]
}

# バッチ用サーバー
EC2_BatchServerSettings= {
    name = "staging-batch.hostjob.jp"
    # サブネット ID
    subnet_id = "subnet-f919c58e"
    # インスタンスタイプ
    instance_type = "t3.micro"
    #  AMI ID
    ami_id = "ami-00ab3fd4947fe510c"
    # 利用するセキュリティグループ一覧
    security_group_ids = [ "sg-00c804bf7618868e9" ]
}

# メールサーバー
EC2_MailServerSettings= {
    name = "mail.staging.hostjob.jp"
    # サブネット ID
    subnet_id = "subnet-f919c58e"
    # インスタンスタイプ
    instance_type = "t3.micro"
    #  AMI ID
    ami_id = "ami-0101fd33e00919539"
    # 利用するセキュリティグループ一覧
    security_group_ids = [ "sg-0eb9fc319d9848ff3" ]
}


#-------------------------------------------------
# ALB
#-------------------------------------------------
ALBCertificateArn=""

#ALB postfix
ALBName="alb"
#TargetGroupName postfix
TargetGroupName="tg"
LoadBalancerDeregistrationDelay=10

# ALB でのルーティングの条件に使うパスの一覧
TargetGroupSettings = {
    user_server={
        tg_name="staging-hostjob-jp-user-tg"
        priority      = 30
        path_pattern = ["/*"]
        instances=[]
  }

    admin_server= {
        tg_name="staging-hostjob-jp-admin-tg"
        priority      = 20
        path_pattern = ["/operation/*"]
        instances=[]
  }
    member_server= {
        tg_name="staging-hostjob-jp-member-tg"
        priority      = 10
        path_pattern = ["/member/*"]
        instances=[]
  }
}

#---------------------------------------
# RDS
#---------------------------------------
DbClusterName="staging-dev-hostclub-cluster"
DbInstanceName="staging-hostjob-jp-instance"

DbInstanceType="db.t3.small"

DbName="hostclub"
DbMasterUserName="root"
DbMasterUserPassword=""

EngineVersion="8.0.mysql_aurora.3.03.0"
Engine="aurora-mysql"

DbSgs=["sg-087386d2e4b667df8"]

DbClusterParameterGroupName="staging-hostjob-jp-cluster-parameter-group"
DbParameterGroupName="staging-hostjob-jp-parameter-group"
ParameterGroupFamily="aurora-mysql8.0"

#---------------------------------------
# ElastiCache
#---------------------------------------
ElastiCacheReplicationGroupId="staging-hostclub"
ElastiCacheNodeType="cache.t3.micro"
ElastiCacheNumCacheClusters="2"
ElastiCacheParameterGroupName="staging-hostclub-parameter-group"
ElastiCacheEngineVersion="7.0"
ElastiCacheSubnetGroupName="staging-hostclub-subnet"
ElastiCacheParameterGroupFamily = "redis7"

#--------------------------------------
# S3
#--------------------------------------
S3BucketName=["stagingassets-hostjob.jp","staginguploads-hostjob.jp"]
S3BucketAcl = "private"