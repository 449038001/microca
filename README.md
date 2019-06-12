microCA 项目

项目为双向认证证书自助颁发。后加入其他证书token到期提醒功能

项目启动：
/opt/gunicorn目录下：
gunicorn app:app -b 0.0.0.0:8898 -w 4

生成的双向认证储存在 /users 目录下
提交的证书储存在certs目录，到期前30天提醒，定时任务执行utils/check_update

数据库为mongodb
```
use admin
db.createRole({role:'sysadmin',roles:[],privileges:[{resource:{anyResource:true},actions:['anyAction']}]})
db.createUser({ user: "root", pwd: "pwd", roles: [{ role: "sysadmin", db: "admin" }] })
```

sudo mongod --dbpath /opt/microCA-master/database --port 27777
sudo mongod --dbpath /opt/microCA-master/database --port 27777 --auth --logpath /opt/microCA-master/logs/mongo.log --fork