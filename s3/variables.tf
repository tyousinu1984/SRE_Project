# Project タグの値（共通）
variable "project_tag" {}

# S3 バケット名
variable "s3_bucket_name" {
    type = list(string)
}
# S3 バケットに適用する ACL
variable "s3_bucket_acl" {
    type = string
}