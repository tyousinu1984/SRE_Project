#----------------------------------------------------
# S3 バケット
#----------------------------------------------------
resource "aws_s3_bucket" "buckets" {
  for_each = { for bucket_name in var.s3_bucket_name : bucket_name => bucket_name }

  tags = {
    Project = var.project_tag
  }
}

resource "aws_s3_bucket_acl" "buckets" {
  for_each = aws_s3_bucket.buckets
  bucket = each.value.id
  acl    = var.s3_bucket_acl
}