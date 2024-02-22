

## 必要ライブラリのインストール

```bash
sudo apt-get install bc
```


## 修正結果の確認

１子プロセスあたりのメモリ使用量 の確認    
```bash

# PHPの場合、出力はpm.start_servers　程度ならOK                
ps aux | pgrep php | wc -l                

# Apacheの場合、出力はStartServers程度ならOK                
ps aux | pgrep httpd | wc -l        

```