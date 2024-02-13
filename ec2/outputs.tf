## Web サーバーのインスタンス ID
output "user_server_instance_ids" {
  value = aws_instance.user_server[*].id 
  description = "求人ユーザー・求人店舗管理 インスタンス ID 一覧"
}

output "admin_server_instance_ids" {
  value =  aws_instance.admin_server[*].id 
 description = "大管理 インスタンス ID 一覧"
}

output "member_server_instance_ids" {
  value =  aws_instance.member_server[*].id 
 description = "求人会員・求人会員管理 インスタンス ID 一覧"
}


output "batch_server_public_ip" {
  value = aws_eip.eip_batch_server.public_ip
 description = "バッチ用サーバーのパブリック IP アドレス"
}

output "mail_server_public_ip" {
  value = aws_eip.eip_mail_server.public_ip
 description = "メールサーバーのパブリック IP アドレス"
}