# !/bin/bash

if [[ $# -lt 10 ]];then
    exit
fi

HostName=$1
DBName=$2
DBUser=$3
WordPressAdminUser=$4
BasicAuthUser=$5

KusanagiPassword=$6
DBUserPassword=$7
DBRootPassword=$8
WordPressAdminPassword=$9
BasicAuthPassword=${10}

FTPPASS=$KusanagiPassword


# 以下を参考に設定しました。
# CORE TECH WIKI /SREチーム/保守・運用/IP分散/マーケ1課サテライト/本番環境/KUSANAGI による WordPress サーバー構築/サーバー構築  
# https://wiki.core-tech.jp/624e80924bd307003e08c1da


##########################################################
# - 初期設定
##########################################################
echo "開始: 初期設定"
#--------------------------------------------
# ホスト名変更
#--------------------------------------------

echo "ホスト名変更"
hostnamectl set-hostname ${HostName}

#--------------------------------------------
# /etc/hosts 変更
# SRE-2683 kusanagiサーバーの自動構築でhostsファイルを編集しないようにする
# https://cor.backlog.com/view/SRE-2683
#--------------------------------------------
# echo "/etc/hosts 変更"
# date=`date +%Y%m%d-%H%M-%S`
# cp -p /etc/hosts /etc/hosts-$date
# sed -i "s/localhost4.localdomain4/localhost4.localdomain4 ${HostName}/g" /etc/hosts

#--------------------------------------------
# プロンプト 表示フォーマットを変更
#--------------------------------------------
echo "プロンプト 表示フォーマットを変更"
date=`date +%Y%m%d-%H%M-%S`
cp -p /etc/bashrc /etc/bashrc-$date

sed -i 's/\\u@\\h /\\u@\\H /g' /etc/bashrc
#--------------------------------------------
# motd にホスト名を追加
#--------------------------------------------
echo "motd にホスト名を追加"
date=`date +%Y%m%d-%H%M-%S`
cp -p /etc/motd /etc/motd-$date

echo '-------------------'  >> /etc/motd
echo $HostName  >> /etc/motd

#--------------------------------------------
# - 不要な Apache 設定ファイルを移動
#--------------------------------------------
date=`date +%Y%m%d-%H%M-%S`
# cp -p /etc/hosts /etc/hosts-$date
cd /etc/httpd/conf.d/
mv _ssl.conf _ssl.conf-$date

#--------------------------------------------
# - Kusanagi で Apache を使うように設定
#--------------------------------------------
echo "Kusanagi で Apache を使うように設定"
kusanagi httpd

 #--------------------------------------------
 # - Kusanagi で php7-fpm を使うように設定（php8-fpm がデフォルトで起動する kusanagi8.6.2202 以降に対応）
 #--------------------------------------------
 echo "Kusanagi で php7-fpm を使うように設定"
kusanagi php7
 # 念のために php8-fpm を止める
systemctl stop php8-fpm
 

##########################################################
# - Kusanagi 初期設定
##########################################################
echo "開始: Kusanagi 初期設定"
#--------------------------------------------
# KUSANAGI 初期化
#--------------------------------------------
kusanagi init \
    --tz Tokyo \
    --lang ja \
    --keyboard ja \
    --kusanagi-pass ${KusanagiPassword} \
    --nophrase \
    --dbsystem mariadb \
    --dbrootpass ${DBRootPassword} \
    --httpd \
    --php7

# sleep 240

#--------------------------------------------
# 不要なファイルの移動
#--------------------------------------------
date=`date +%Y%m%d-%H%M-%S`
cd /etc/httpd/conf
mv httpd.conf httpd.conf-$date
cd ../conf.d/
mv _http.conf _http.conf-$date


#--------------------------------------------
# Apacheのダウングレード（2.4.52 のプロセス突然死バグ回避）
#--------------------------------------------
echo "開始: Apacheのダウングレード"
yum -y downgrade kusanagi-httpd-2.4.51-2.noarch


#--------------------------------------------
# KUSANAGI プロヴィジョニング
#--------------------------------------------
echo "開始: KUSANAGI プロヴィジョニング"
kusanagi provision --WordPress --wplang ja --no-email \
    --fqdn  ${HostName} \
    --dbname ${DBName} \
    --dbuser ${DBUser} \
    --dbpass ${DBUserPassword} \
    ${HostName}

#--------------------------------------------
# KUSANAGI プロビジョニングでできた不要ファイルの移動
#--------------------------------------------

cd /etc/httpd/conf.d
date=`date +%Y%m%d-%H%M-%S`
mv ${HostName}_http.conf _${HostName}_http.conf-$date
mv ${HostName}_ssl.conf _${HostName}_ssl.conf-$date
mv _http.conf _http.conf-$date



##########################################################
# - Apache 設定
##########################################################
echo "開始: Apache 設定"
#--------------------------------------------
# ALB ヘルスチェック用の VirtualHost 設定（ログ出力を access.log に設定する）
#--------------------------------------------

cat << EOF >>/etc/httpd/conf.d/00_localhost.conf
<VirtualHost *:80>
    ServerName localhost
    CustomLog /var/log/httpd/access.log combined
</VirtualHost>
EOF

#--------------------------------------------
# VirtualHost 設定
#--------------------------------------------
echo "開始:  VirtualHost 設定"
cat << EOF >> /etc/httpd/conf.d/${HostName}.conf
<VirtualHost *:80>
    ServerAdmin webmaster@example.com
    DocumentRoot /home/kusanagi/${HostName}/DocumentRoot
    ServerName ${HostName}
    ServerAlias www.${HostName}
    ErrorLog  /home/kusanagi/${HostName}/log/httpd/error.log
    CustomLog /home/kusanagi/${HostName}/log/httpd/access.log combined env=!no_log

    <IfModule mod_security2.c>
        #IncludeOptional modsecurity.d/kusanagi_activated_rules/wordpress/*.conf
        #SecAuditLog /home/kusanagi/${HostName}/log/httpd/waf.log
    </IfModule>

    <Directory "/home/kusanagi/${HostName}/DocumentRoot">
        Require all granted
        AllowOverride All
        Options FollowSymlinks
    </Directory>
</VirtualHost>
EOF


#--------------------------------------------
# X-Forwarded 用の Log 設定追加
#--------------------------------------------
echo "開始:  X-Forwarded 用の Log 設定追加"
date=`date +%Y%m%d-%H%M-%S`
cp -p /etc/httpd/httpd.conf /etc/httpd/httpd.conf-$date

sed -i 's/LogFormat "%h %l %u %t \\"%r\\" %>s %b \\"%{Referer}i\\" \\"%{User-Agent}i\\"" combined/LogFormat "%{X-Forwarded-For}i %h %l %u %t \\"%r\\" %>s %b \\"%{Referer}i\\" \\"%{User-Agent}i\\"" combined/g' /etc/httpd/httpd.conf

#--------------------------------------------
# X-Signature設定をコメントアウト
#--------------------------------------------
sed -i '/X-Signature/s/^/#/' /etc/httpd/httpd.conf

#--------------------------------------------
# サービス再起動
#--------------------------------------------
echo "開始:  Apache 再起動"
systemctl restart httpd.service



##########################################################
# - WordPress インストール
##########################################################
echo "開始: WordPress インストール"
#--------------------------------------------
# wp-config.php を作成
#--------------------------------------------
cd /home/kusanagi/${HostName}/DocumentRoot
cp -p wp-config-sample.php wp-config.php

configFile=/home/kusanagi/${HostName}/DocumentRoot/wp-config.php


SALTS=$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)

SALT_NAMES="AUTH_KEY SECURE_AUTH_KEY LOGGED_IN_KEY NONCE_KEY AUTH_SALT SECURE_AUTH_SALT LOGGED_IN_SALT NONCE_SALT"

for SALT_NAME in $SALT_NAMES
do
    sed -i -e "s/$SALT_NAME/${SALT_NAME}1/g" $configFile
done

line=$(sed -n '/AUTH_KEY1/{=;q}' $configFile)
echo -e "$SALTS" |sed -i -e "${line}r/dev/stdin" $configFile

for SALT_NAME in $SALT_NAMES
do
    sed -i -e "/${SALTNAME}1/d" $configFile
done


sed -i "s/database_name_here/${DBName}/g" $configFile
sed -i "s/username_here/${DBUser}/g" $configFile
sed -i "s/password_here/${DBUserPassword}/g" $configFile

cat << 'EOL' |sed -i '21r /dev/stdin' $configFile
// AWS ELB(ALB) リダイレクトループ対策
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
} elseif (isset( $_SERVER['HTTP_CLOUDFRONT_FORWARDED_PROTO']) && $_SERVER['HTTP_CLOUDFRONT_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] ='on';
}
EOL

sleep 5

sed -i "s/#define('FTP_PASS', '\*\*\*\*\*')/define('FTP_PASS', '${FTPPASS}')/g" $configFile
chown kusanagi:www $configFile


#--------------------------------------------
# コマンドラインで Wordpress をインストール
#--------------------------------------------
echo "開始: コマンドラインで Wordpress をインストール"
cd /home/kusanagi/${HostName}/DocumentRoot
sudo -u kusanagi -- /usr/bin/php7 /usr/local/bin/wp core install \
    --url=${HostName} \
    --title=${HostName} \
    --admin_user=${WordPressAdminUser} \
    --admin_password=${WordPressAdminPassword} \
    --admin_email=infra-support@core-tech.jp

#--------------------------------------------
# wp-config.php のパーミッション変更
#--------------------------------------------
chmod 640 wp-config.php
chown kusanagi:www wp-config.php

#--------------------------------------------
# プラグイン/テーマディレクトリ配下のディレクトリのパーミッションが、作成時に777になるように設定する
#--------------------------------------------
setfacl -R -d -m u::rwx,g::rwx,o::rwx /home/kusanagi/${HostName}/DocumentRoot/wp-content/plugins
setfacl -R -d -m u::rwx,g::rwx,o::rwx /home/kusanagi/${HostName}/DocumentRoot/wp-content/themes

#--------------------------------------------
# サイトURLのプロトコルをhttpsに変更
#--------------------------------------------
mysql -h localhost -u${DBUser} -p${DBUserPassword} ${DBName} -e "UPDATE wp_options SET option_value = 'https://${HostName}' where option_name IN ('home','siteurl');"


##########################################################
# - SFTP 設定
##########################################################
echo "開始: SFTP 設定"
#--------------------------------------------
# SFTP用ユーザー作成（kusanagi と同じ UID にする）
#--------------------------------------------
useradd -d /home/kusanagi -M ${DBUser} -o -u 1002 -g 1002 -s /sbin/nologin
# パスワード設定（kusanagi と同じパスワードにする）
echo   ${KusanagiPassword} | passwd --stdin ${DBUser}

#--------------------------------------------
# バインドモードでmountする
#--------------------------------------------
mkdir -p /chroot/${DBUser}/kusanagi
mount -B /home/kusanagi /chroot/${DBUser}/kusanagi


#--------------------------------------------
# 再起動してもmountされるようにする
#--------------------------------------------

# バックアップ
date=`date +%Y%m%d-%H%M-%S`
cp -p /etc/fstab /root/fstab-$date
# /etc/fstabの編集
cat << EOF >>  /etc/fstab
    /home/kusanagi /chroot/${DBUser}/kusanagi none bind 0 0
EOF

#--------------------------------------------
# /etc/ssh/sshd_configの編集
#--------------------------------------------
echo "開始:  /etc/ssh/sshd_configの編集"
cp -pr /etc/ssh/sshd_config /etc/ssh/_sshd_config.orig

echo "" >> /etc/ssh/sshd_config
sed -i 's/#Port 22/Port 22/g' /etc/ssh/sshd_config
# sed -i '/Port 22/a\Port 54322' /etc/ssh/sshd_config
cat << EOF >>  /etc/ssh/sshd_config
Match User ${DBUser}
    ChrootDirectory /chroot/${DBUser}
    X11Forwarding no
    AllowTcpForwarding no
    PasswordAuthentication yes
    ForceCommand internal-sftp
EOF
service sshd restart
sleep 5

#--------------------------------------------
# WP 更新用の鍵を作成する
#--------------------------------------------
echo "開始: WP 更新用の鍵を作成する"
rm -rf /home/kusanagi/.wp-ssh
su - kusanagi -c 'mkdir -m 700 /home/kusanagi/.wp-ssh; ssh-keygen -q -N "" -f /home/kusanagi/.wp-ssh/id_rsa'
cat /home/kusanagi/.wp-ssh/id_rsa.pub >> /home/kusanagi/.ssh/authorized_keys
chown -R kusanagi:kusanagi /home/kusanagi/.wp-ssh

#--------------------------------------------
# WP 更新をssh経由で更新するように修正
#--------------------------------------------
sed -i "/FTP_HOST/a\define('FTP_PRIKEY', '\/home\/kusanagi\/.wp-ssh\/id_rsa');" /home/kusanagi/${HostName}/DocumentRoot/wp-config.php
sed -i "/FTP_HOST/a\define('FTP_PUBKEY', '\/home\/kusanagi\/.wp-ssh\/id_rsa.pub');" /home/kusanagi/${HostName}/DocumentRoot/wp-config.php
sed -i "s/ftpsockets/ssh2/g" /home/kusanagi/${HostName}/DocumentRoot/wp-config.php
sed -i "s/#define('FTP_PASS', '\*\*\*\*\*')/define('FTP_PASS', ${KusanagiPassword})/g" /home/kusanagi/${HostName}/DocumentRoot/wp-config.php
chown kusanagi:www /home/kusanagi/${HostName}/DocumentRoot/wp-config.php

#--------------------------------------------
# WPの SFTP での更新用プラグインを入れる
#--------------------------------------------
cd /home/kusanagi/${HostName}/DocumentRoot
sudo -u kusanagi -- /usr/bin/php7 /usr/local/bin/wp plugin install ssh-sftp-updater-support --activate
# sleep 10


#--------------------------------------------
# Basic 認証
#--------------------------------------------
echo "開始: Basic 認証"
cd /home/kusanagi/${HostName}/DocumentRoot

# 現在の .htaccess を移動
date=`date +%Y%m%d-%H%M-%S`
mv .htaccess ../../.htaccess-$date

# ヒアドキュメントで .htacess を作成
cat << 'EOL' >> .htaccess
<Files ~ "^\.(htaccess|htpasswd)$">
    deny from all
</Files>
### IP許可 ###
SetEnvIf X-Forwarded-For 30.110.200.51 allow_ip
SetEnvIf X-Forwarded-For 30.110.200.52 allow_ip
SetEnvIf X-Forwarded-For 30.110.200.53 allow_ip
SetEnvIf X-Forwarded-For 30.110.200.54 allow_ip
<FilesMatch "^(wp\-login\.php|wp\-admin|wp\-config\.php|xmlrpc)">
    order deny,allow
    deny from all
    allow from env=allow_ip
</FilesMatch>
### BasicAuth
AuthType Basic
AuthName "ENTER YOUR NAME & PASSWORD TO LOGIN"
AuthUserFile /home/kusanagi/.htpasswd
Require valid-user
<IfModule mod_rewrite.c>
    RewriteEngine on
        RewriteCond %{HTTP:X-Forwarded-Proto} =http
        RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
        RewriteCond %{THE_REQUEST} ^.*/index.php
        RewriteRule ^(.*)index.php$ https://{HostName}/$1 [R=301,L]
        RewriteCond %{THE_REQUEST} ^.*/index.html
        RewriteRule ^(.*)index.html$ https://{HostName}/$1 [R=301,L]
        RewriteCond %{HTTP_HOST} ^www.{HostName}
        RewriteRule ^(.*)$ https://{HostName}/$1 [R=301,L]
</IfModule>

<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    #RewriteRule Shibboleth.sso - [L]
    RewriteRule ^index\.php$ - [L]
    RewriteCond %{REQUEST_URI} !\.(gif|css|js|swf|jpeg|jpg|jpe|png|ico|swd|pdf|svg|eot|ttf|woff)$
    RewriteCond %{REQUEST_FILENAME} !-f
    #RewriteCond %{REQUEST_URI} !(^/Shibboleth.sso/)
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.php [L]
</IfModule>
# END WordPress
EOL

sed -ie "s/{HostName}/${HostName}/g" .htaccess
# 所有者を変更
chown kusanagi:www .htaccess
chmod 664 .htaccess
# htpasswd 作成
echo ${BasicAuthPassword} |  htpasswd -i -c /home/kusanagi/.htpasswd ${BasicAuthUser}


#--------------------------------------------
# Apacheユーザーがファイルを作成する場合のumaskの指定
#--------------------------------------------
cat << EOF >> /home/kusanagi/${HostName}/DocumentRoot/wp-config.php
define('FS_CHMOD_DIR', (0775 & ~ umask()));
define('FS_CHMOD_FILE', (0664 & ~ umask()));
EOF

##########################################################
# - Zabbix agent 設定
##########################################################
echo "開始: Zabbix agent 設定"
#--------------------------------------------
# サーバー指定
#--------------------------------------------

cd /etc/zabbix
date=`date +%Y%m%d-%H%M-%S`
cp -p zabbix_agentd.conf zabbix_agentd.conf-$date

zabbixIP=50.60.140.80
sed -i "s/127.0.0.1/$zabbixIP/g" zabbix_agentd.conf

#--------------------------------------------
# エージェントの再起動
#--------------------------------------------
systemctl restart zabbix-agent


##########################################################
# - チューニング
##########################################################
echo "開始: チューニング"
#--------------------------------------------
# 事前準備
#--------------------------------------------

sleep 5

# jq を入れる
yum install -y jq
sleep 10

#--------------------------------------------
# 各変数の取得
#--------------------------------------------
echo "開始: 各変数の取得"
# インスタンスタイプを取得
# https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
# instanceType=$(curl http://169.254.169.254/latest/meta-data/instance-type)
# メモリサイズを取得
# memoryInMiB=$(aws ec2 describe-instance-types --instance-types $instanceType | jq ".InstanceTypes[]|(.MemoryInfo.SizeInMiB)")
memoryInMiB=$(cat /tmp/instance-spec | jq ".InstanceTypes[]|(.MemoryInfo.SizeInMiB)")

# 各値を取り出す（注意点あり。詳細は以下 URL を参照）
# http://blog.calcurio.com/jq-numeric-key.html
apacheParams=$(cat /tmp/apache-mpm-tuning-parameters.json | jq ".Parameters[\"$memoryInMiB\"]")
phpParams=$(cat /tmp/php-fpm-tuning-parameters.json | jq ".Parameters[\"$memoryInMiB\"]")
mysqlParams=$(cat /tmp/mysql-tuning-parameters.json | jq ".Parameters[\"$memoryInMiB\"]")

# Apacheのパラメーター取得
StartServers=$(echo $apacheParams | jq -r '.StartServers')
MinSpareThreads=$(echo $apacheParams | jq -r '.MinSpareThreads')
MaxSpareThreads=$(echo $apacheParams | jq -r '.MaxSpareThreads')
ThreadsPerChild=$(echo $apacheParams | jq -r '.ThreadsPerChild')
ServerLimit=$(echo $apacheParams | jq -r '.ServerLimit')
MaxRequestWorkers=$(echo $apacheParams | jq -r '.MaxRequestWorkers')
MaxConnectionsPerChild=$(echo $apacheParams | jq -r '.MaxConnectionsPerChild')

# PHPのパラメーター取得
start_servers=$(echo $phpParams | jq -r '.start_servers')
min_spare_servers=$(echo $phpParams | jq -r '.min_spare_servers')
max_spare_servers=$(echo $phpParams | jq -r '.max_spare_servers')
max_children=$(echo $phpParams | jq -r '.max_children')
max_requests=$(echo $phpParams | jq -r '.max_requests')

# MySQL（MariaDB）のパラメーター取得
max_connections=$(echo $mysqlParams | jq -r '.max_connections')
thread_cache_size=$(echo $mysqlParams | jq -r '.thread_cache_size')
table_cache=$(echo $mysqlParams | jq -r '.table_cache')
read_buffer_size=$(echo $mysqlParams | jq -r '.read_buffer_size')
max_allowed_packet=$(echo $mysqlParams | jq -r '.max_allowed_packet')
query_cache_size=$(echo $mysqlParams | jq -r '.query_cache_size')
join_buffer_size=$(echo $mysqlParams | jq -r '.join_buffer_size')
innodb_buffer_pool_size=$(echo $mysqlParams | jq -r '.innodb_buffer_pool_size')
max_heap_table_size=$(echo $mysqlParams | jq -r '.max_heap_table_size')
tmp_table_size=$(echo $mysqlParams | jq -r '.tmp_table_size')

#--------------------------------------------
# MariaDB 設定
#--------------------------------------------
echo "開始: MariaDB 設定"
cd /etc/my.cnf.d
date=`date +%Y%m%d-%H%M-%S`
mv server.cnf  server.cnf-$date

cat << EOL >> server.cnf
#
# These groups are read by MariaDB server.
# Use it for options that only the server (but not clients) should see
#
# See the examples of server my.cnf files in /usr/share/mysql/
#

# this is read by the standalone daemon and embedded servers
[server]

# this is only for the mysqld standalone daemon
[mysqld]
character_set_server = utf8mb4
max_connections = $max_connections
wait_timeout = 300
interactive_timeout = 300
thread_cache_size = $thread_cache_size
table_cache = $table_cache
max_allowed_packet = $max_allowed_packet
query_cache_size = $query_cache_size
thread_stack = 512K

key_buffer_size = 32M
sort_buffer_size = 2M
read_buffer_size = $read_buffer_size
read_rnd_buffer_size = 1M
join_buffer_size = $join_buffer_size

myisam_sort_buffer_size = 1M 
bulk_insert_buffer_size = 1M

innodb_buffer_pool_size = $innodb_buffer_pool_size
innodb_log_file_size = 32M
max_heap_table_size = $max_heap_table_size
innodb_thread_concurrency = 8
tmp_table_size = $tmp_table_size

log-error = /var/log/mysql/mysqld.log
log-warnings = 1

slow_query_log = 1
slow_query_log_file = "/var/log/mysql/slow.log"
long_query_time = 1.2

#
# * Galera-related settings
#
[galera]
# Mandatory settings
# wsrep_on=ON
# wsrep_provider=
# wsrep_cluster_address=
# binlog_format=row
# default_storage_engine=InnoDB
# innodb_autoinc_lock_mode=2
#
# Allow server to accept connections on all interfaces.
#
# bind-address=0.0.0.0
#
# Optional setting
# wsrep_slave_threads=1
# innodb_flush_log_at_trx_commit=0

# this is only for embedded server
[embedded]

# This group is only read by MariaDB servers, not by MySQL.
# If you use the same .cnf file for MySQL and MariaDB,
# you can put MariaDB-only options here
[mariadb]

# This group is only read by MariaDB-10.1 servers.
# If you use the same .cnf file for MariaDB of different versions,
# use this group for options that older servers don't understand
[mariadb-10.1]
EOL

#--------------------------------------------
# PHP-FPM 設定
#--------------------------------------------
echo "開始: PHP-FPM 設定"
cd /etc/php7-fpm.d/
date=`date +%Y%m%d-%H%M-%S`
grep -v "^[!;]"  www.conf > www.conf-$date-woComment
# 現在の設定をバックアップ
mv www.conf www.conf-$date

# 設定ファイルを新規作成
cat << EOL >> www.conf
[www]
user = kusanagi
group = kusanagi

listen = 127.0.0.1:9000
listen.allowed_clients = 127.0.0.1

pm = dynamic
pm.start_servers =$start_servers
pm.min_spare_servers = $min_spare_servers
pm.max_spare_servers = $max_spare_servers
pm.max_children = $max_children
pm.max_requests = $max_requests


slowlog = /var/log/php7-fpm/www-slow.log

request_slowlog_timeout = 10
request_terminate_timeout = 180

php_admin_value[error_log] = /var/log/php7-fpm/www-error.log
php_admin_flag[log_errors] = on
php_value[session.save_handler] = files
php_value[session.save_path]    = /var/lib/php7/session
php_value[soap.wsdl_cache_dir]  = /var/lib/php7/wsdlcache
EOL


#--------------------------------------------
# Apche MPM 設定
#--------------------------------------------
echo "開始: Apche MEPM 設定"
cd /etc/httpd
date=`date +%Y%m%d-%H%M-%S`
cp -p httpd.conf  httpd.conf-$date
sed -i "/StartServers/c\\\tStartServers\\t${StartServers}" httpd.conf
sed -i "/MinSpareThreads/c\\\tMinSpareThreads\\t${MinSpareThreads}" httpd.conf
sed -i "/MaxSpareThreads/c\\\tMaxSpareThreads\\t${MaxSpareThreads}" httpd.conf
sed -i "/ServerLimit/c\\\tServerLimit\\t${ServerLimit}" httpd.conf
sed -i "/MaxRequestWorkers/c\\\tMaxRequestWorkers\\t${MaxRequestWorkers}" httpd.conf
sed -i "/MaxConnectionsPerChild/c\\\tMaxConnectionsPerChild\\t${MaxConnectionsPerChild}" httpd.conf
sed -i "/ThreadsPerChild/c\\\tThreadsPerChild\\t${ThreadsPerChild}" httpd.conf


#--------------------------------------------
# Kusanagi再起動
#--------------------------------------------
kusanagi restart

#--------------------------------------------
# MariaDB 再起動
#--------------------------------------------
systemctl restart mariadb


#--------------------------------------------
# 2022年08月26日追加
# monit の無効化
#--------------------------------------------
echo "開始: monit の無効化"
# サービスを停止
systemctl stop monit
# 自動起動を停止
systemctl disable monit
# テーマのインポートに失敗してたので、themes ディレクトリのパーミッションを 777 に変更
chmod 777 /home/kusanagi/${HostName}/DocumentRoot/wp-content/plugins
chmod 777 /home/kusanagi/${HostName}/DocumentRoot/wp-content/themes

# 終了
echo "終了"