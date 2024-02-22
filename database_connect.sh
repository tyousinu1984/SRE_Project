#!/bin/bash

# データベース接続情報
db_connections=(
    host1 user1 password1
    host2 user2 password2
    host3 user3 password3
)

# 何秒毎にデータベースの状態を確認するか
sleepTime=5

# データベースの状態を確認する関数
check_database() {
    dbHost=$1
    dbUser=$2
    password=$3

    mysqladmin ping -h ${dbHost} -u ${dbUser} -p${password} 2>&1 | grep alive > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "${dbHost} status is alive"
        date
        echo "---------"
        dbStatus="alive"
        sleep ${sleepTime}
    else
        echo "${dbHost} status is dead"
        date
        echo "---------"
        dbStatus="dead"
        sleep ${sleepTime}
    fi

    ## mysql に ping を飛ばす処理(2回目以降)
    while true; do
        mysqladmin ping -h ${dbHost} -u ${dbUser} -p${password} 2>&1 | grep alive > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            if [ ${dbStatus} = "alive" ]; then
                sleep ${sleepTime}
            elif [ ${dbStatus} = "dead" ]; then
                echo "${dbHost} status has been alive"
                date
                echo "---------"
                dbStatus="alive"
                sleep ${sleepTime}
            fi
        else
            if [ ${dbStatus} = "alive" ]; then
                echo "${dbHost} status has been dead"
                date
                echo "---------"
                dbStatus="dead"
                sleep ${sleepTime}
            elif [ ${dbStatus} = "dead" ]; then
                sleep ${sleepTime}
            fi
        fi
    done
}

# バックグラウンドでデータベースの状態を確認
for ((i = 0; i < ${#db_connections[@]}; i += 3)); do
    (check_database "${db_connections[i]}" "${db_connections[i+1]}" "${db_connections[i+2]}") &
done

# Wait for all background tasks to complete
wait