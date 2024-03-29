[csv2xlsx_0.3.0_Linux_x86_64.tar.gz](:/2ec7578fdaff4706a051cb44af3845b3)


```sh
#!/bin/bash

# преобразование отчета в xls и отправка его по почте
# https://github.com/mentax/csv2xlsx/releases/tag/v0.3.0

sesFromAddress="report@example.com"
sesToAddress="numbers@example.com"
sesSubject="Атоматическая рассылка отчета"
sesSMTP=""
sesPort="587"
sesMessage="Добрый день! Отчет во вложении к письму."
DataFolder="/data/"

if ! mountpoint -q $DataFolder
then
    echo "Folder was not mounted. Mounting folder..."
    /bin/bash /opt/scripts/mount_report.sh
    sleep 30
fi

if mountpoint -q $DataFolder
then
    echo "Folder was mounted. Sending mail..."
    cdrFile="$DataFolder/sipuni_01$(date -d "-1 month" +"%m%Y")_mm.cdr"
    csvFile="/tmp/s_01$(date -d "-1 month" +"%m%Y")_mm.csv"
    sesFile="/tmp/s_01$(date -d "-1 month" +"%m%Y")_mm.xlsx"
    iconv -f WINDOWS-1251 -t UTF-8 $cdrFile -o $csvFile
    /usr/bin/csv2xlsx --output $sesFile $csvFile
    echo $sesFile
    sesMIMEType=`file --mime-type "$sesFile" | sed 's/.*: //'`
    curl -k -v --url smtp://$sesSMTP:$sesPort --ssl-reqd --mail-from $sesFromAddress --mail-rcpt $sesToAddress -F '=(;type=multipart/mixed' -F "=$sesMessage;type=text/plain" -F "file=@$sesFile;type=$sesMIMEType;encoder=base64" -F '=)' -H "Subject: $sesSubject" -H "From: $sesFromAddress;" -H "To: $sesToAddress"
else
    echo "Folder mount error"
    exit 1
fi
```
```sh
#!/usr/bin/expect -d

set env(LC_ALL) "C"
set env(PS1) "shell:"
set timeout 30

set user "user"
set password "password"
set host "sftp.example.com"
set port "22"
set local_dir "/data"
set remove_dir "/report"

spawn /bin/sh

expect "shell:"

send -- "sshfs $user@$host:$remove_dir $local_dir -p $port -o reconnect\r"

expect "password:"

send -- "$password\r"

sleep 1
```
