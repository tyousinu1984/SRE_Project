# terrafrom.tfvarsから読み込む

#---------------------------------------
# assume role する IAM ロールの ARN
#---------------------------------------
variable "IamRoleArn" {
  description = "assume role する IAM ロールの ARN"
}


variable "HostZoneID" {
  type = string
  description = "ホストゾーン ID"
}

variable "DomainName" {
  description = "ドメイン名"
}

#-------------------------
# AMI 取得
#-------------------------
variable "WebserverInstanceID" {
  default =""
  description = "AMI を取得する インスタンスの ID"
}

variable "AMIName_Prefix" {
  default =""
  description = "AMI につける名前"
}


#---------------------------------------
# VPCID
#---------------------------------------
variable "VpcId"{
  default = "vpc-d434fcb1"
}

#ALBSubnet
variable "SubnetIds"{
 default = ["subnet-b128eaf9", "subnet-a232e789"]
}

#---------------------------------------
# Route53
#---------------------------------------
variable "HostZoneID" {
  default = ""
  description = "Route 53 ホストゾーン ID"
}


#---------------------------------------
# 共通変数
#---------------------------------------
variable "ResourceNamePrefix"{
 description = "リソースにつける接頭辞"
}

variable "Stage"{
 default = "dev"
 description = "ステージ。基本は dev/prod/staging のいずれか"
}

variable "ProjectTag" {
  description = "Project タグの値"
}

variable "CheckAlarmSetting" {
  description = "CheckAlarmSetting タグの値"
}

variable "CheckProjectSetting" {
  description = "CheckProjectSetting タグの値"
}

variable "CheckZabbixSetting" {
  description = "CheckZabbixSetting タグの値"
}

#-------------------------------------------------
# EC2
#-------------------------------------------------
variable "KeyPair"{
 description = "キーペア名"
}

variable "EC2_UserServerSettings" {
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
  description = "求人ユーザー・求人店舗管理 サーバーの情報"
}

variable "EC2_AdminServerSettings" {
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
  description = "大管理サーバーの情報"
}

variable "EC2_MemberServerSettings" {
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

variable "EC2_BatchServerSettings" {
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

variable "EC2_MailServerSettings" {
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
  description = "サーバーの情報"
}

#-------------------------------------------
# ALB
#-------------------------------------------
#ALBSecurity Group
variable "ALBSecurityGroupId"{
 default = "sg-0a4a275530e7e0dcf"
}

variable "ALBCertificateArn" {
  description = "ALB につける ACM SSL 証明書の ARN"
}

#InternetALB postfix
variable "ALBName"{
 default = "alb"
}

#TargetGroupName postfix
variable "TargetGroupName"{
 default = "tg"
}

variable "LoadBalancerDeregistrationDelay"{
 default = "10"
}

variable "TargetGroupSettings" {
  description = "ALB でのルーティングの条件に利用するパス一覧"
  type = map(object({
    tg_name= string
    priority    = number
    instances = list(string)
    path_pattern  = list( string)
    }))
    
}

#---------------------------------------
# RDS
#---------------------------------------
variable "DbClusterName" {
  default =""
  description ="DBクラスター名"
}

variable "DbInstanceName" {
  default =""
  description ="DBインスタンス名"
}

variable "EngineVersion" {
  default =""
  description ="MySQL Auroraバージョン"
}

variable "Engine" {
  default =""
  description ="MySQLエンジン"
}

variable "DbInstanceType" {
  default =""
  description ="DBインスタンスタイプ"
}

variable "DbName" {
  default =""
  description ="DB名"
}

variable "DbMasterUserName" {
  default =""
  description ="DBのマスターユーザー名"
}

variable "DbMasterUserPassword" {
  default = ""
  description ="DBのマスターユーザーパスワード"
}

variable "DbSgs" {
  default =""
  description ="DBのセキュリティグループ"
}


variable "DbClusterParameterGroupName" {
  default =""
  description ="DBクラスターのパラメータグループ"
}

variable "DbParameterGroupName" {
  default =""
  description ="DBのパラメータグループ"
}

variable "ParameterGroupFamily" {
  default = ""
  description = "パラメータグループのファミリー"
  
}


#---------------------------------------
# ElastiCache
#---------------------------------------
variable "ElastiCacheReplicationGroupId" {
  default =""
  description ="クラスター名"
}

variable "ElastiCacheNodeType" {
  default =""
  description ="ノードのタイプ"
}

variable "ElastiCacheNumCacheClusters" {
  default =""
  description ="ノードの数"
}

variable "ElastiCacheParameterGroupName" {
  default =""
  description ="パラメーターグループ"
}

variable "ElastiCacheEngineVersion" {
  default =""
  description ="エンジンバージョン"
}

variable "ElastiCacheSubnetGroupName" {
  default =""
  description ="ElastiCacheのサブネットグループ名"
}

variable "ElastiCacheSubnetIds" {
  default =""
  description ="ElastiCacheのサブネットIDのリスト"
}

variable "ElastiCacheSecurityGroupId" {
  default =""
  description ="ElastiCacheのセキュリティグループID"
}

variable "ElastiCacheParameterGroupFamily" {
  default = ""
  description ="ElastiCacheのパラメータグループのファミリー"
  
}

#-------------------------
# S3
#-------------------------
variable "S3BucketName" {
  default = []
  description = "S3バケット名"
}

variable "S3BucketAcl" {
  default = ""
  description = "S3 バケットのアクセス制限設定"
}



#-------------------------
# CloudFront
#-------------------------
variable "AliasDomainNames" {
  description = "CloudFront ディストリビューションのエイリアスのドメイン名の配列"
  default = []
}

variable "S3OriginId" {
  description = "オリジン名"
  default = []
}

variable "CloudFrontLogS3BucketDomainName" {
  description = "CloudFront ディストリビューションのログを保存する S3 バケットのドメイン名"
  default = []
}

variable "AcmCertificateArn" {
  description = "SSL証明書のArn"
  default = []
}

variable "SecurityPolicy" {
  description = "SSL 証明書のポリシー"
  default = []
}

variable "NumberedLambdaFunctionArn" {
  description = "Lambda@Edge の ARN（バージョン番号も指定する"
}
