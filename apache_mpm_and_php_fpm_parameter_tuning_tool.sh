# !/bin/bash

CEILING() {
    echo "scale=0;($1+0.9)/1" | bc
}

FLOOR() {
    local value=$1
    local result=$(echo "scale=0; $value / 10 * 10" | bc)
    echo $result
}

ROUND() {
    local value=$1
    local num_digits=$2

    # num_digitsが負の場合は0に設定する
    if ((num_digits < 0)); then
        num_digits=0
    fi

    echo "scale=$num_digits; $value" | bc
}
php_child_process_magnification="${1:-1}"
apache_child_process_magnification="${1:-1}"


total_memory=$(free -m | grep Mem | awk '{print $2}')

# PHP子プロセスの中メモリ使用率 (MB)
php_child_process_medium_memory=$(ps aux | grep php | awk '{print $6}' | sort -nr | awk '{sum+=$1}END{print sum/NR/1024}')

# PHP 許容するメモリ使用量率
php_allowable_memory_rate=0.6
# PHP 許容するメモリ使用量(MB)
php_allowable_memory=$(echo "$total_memory * $php_allowable_memory_rate * $php_child_process_magnification" | bc)
# PHPの１子プロセスのメモリ使用量(MB)
php_child_process_memory=$(CEILING $php_child_process_medium_memory)
echo "PHPの１子プロセスのメモリ使用量(MB): $php_child_process_memory"

# Apache子プロセスの中メモリ使用率 (MB)
apache_child_process_medium_memory=$(ps aux | grep httpd | awk '{print $6}' | sort -nr | awk '{sum+=$1}END{print sum/NR/1024}')
# Apache 許容するメモリ使用量率
apache_allowable_memory_rate=0.1
# Apache 許容するメモリ使用量(MB)
apache_allowable_memory=$(echo "$total_memory * $apache_allowable_memory_rate * $apache_child_process_magnification$" | bc)
# Apacheの１子プロセスのメモリ使用量(MB)
apache_child_process_memory=$(CEILING $apache_child_process_medium_memory)
echo "Apacheの１子プロセスのメモリ使用量(MB): $apache_child_process_memory"

# PHP-FPM のチューニング
pm_max_children=$(FLOOR $(echo "$php_allowable_memory/$php_child_process_memory" | bc))
pm_start_servers=$(ROUND $(echo "$pm_max_children*2/3" | bc) 0)
pm_min_spare_servers=$pm_start_servers
pm_max_spare_servers=$(ROUND "($pm_max_children + $pm_start_servers)/2" 0)
pm_max_requests=250

echo ""
echo "====PHP-FPM のチューニング===="
echo "pm.max_children = $pm_max_children"
echo "pm.start_servers = $pm_start_servers"
echo "pm.min_spare_servers = $pm_min_spare_servers"
echo "pm.max_spare_servers = $pm_max_spare_servers"
echo "pm.max_requests = $pm_max_requests"

# Apache のチューニング
MinSpareThreads=$pm_min_spare_servers
MaxSpareThreads=$pm_max_spare_servers
MaxRequestWorkers=$pm_max_children

ThreadsPerChild=$(ROUND $(echo "$MaxRequestWorkers / ($MaxSpareThreads - $MinSpareThreads + 1)" | bc) 0)
StartServers=$(ROUND $(echo "$MinSpareThreads/$ThreadsPerChild" | bc) 0)
ServerLimit=$(ROUND $(echo "$MaxSpareThreads/$ThreadsPerChild" | bc) 1)
MaxConnectionsPerChild=250

echo ""
echo "====Apache のチューニング===="
echo "StartServers = $StartServers"
echo "ThreadsPerChild = $ThreadsPerChild"
echo "MinSpareThreads = $MinSpareThreads"
echo "MaxSpareThreads = $MaxSpareThreads"
echo "MaxRequestWorkers = $MaxRequestWorkers"
echo "ServerLimit= $ServerLimit"
echo "MaxConnectionsPerChild = $MaxConnectionsPerChild"