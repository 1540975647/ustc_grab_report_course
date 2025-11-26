# USTC研究生综合服务平台学术报告自动选课

#### 郑重声明：本项目旨在通过自动化方式监控研究生学术报告课程的实时变化，并在出现可选择报告时发送通知，提高信息获取效率；本工具严格限制请求频率，仅用于学习自动化脚本与系统工程的实践；不会进行高频访问或突破系统限制，也不会影响服务器正常运行；若擅自修改执行间隔，导致被服务器封禁，后果自负！
### 1. 制作该脚本的缘由

由于USTC某`225学院`从`2025级`开始要求必须选够至少`8`个学术报告，才能进行毕业论文的开题，但是仅允许选择某些学院开设的报告，而且由于该学院人数众多，符合要求的报告如果有了新的不会自动提醒选课，导致知道消息之后该报告早就被抢光了，故做此脚本



### 2. 该脚本实现的功能

#### 2.1 以下除了`2.2`的所有功能
```
main.py
```

#### 2.2 更新`cookie`中的`_WEU`字段保活

```
main_update_weu.py
```
经过测试，`cookie`中的其他字段仅需手动登录平台抓包获取`1`次，但`_WEU`字段若不更新，会在若干小时后过期，故需要定时更新（下方会设置`30分钟`更新一次）。~~至于其他字段什么时候过期我也还不清楚，反正现在跑了1个多月了还没过期，如果过期了就重新登录平台抓一下吧orz~~

#### 2.3 根据特定的学院和新的报告降序日期查询符合条件的报告

```
utils/search_report.py
```

#### 2.4 根据报告编号`BGBM`选课

```
utils/grab_particular_course.py
```

#### 2.5 根据报告编号`BGBM`退课

```
utils/withdraw_particular_course.py
```

#### 2.6 发送邮件提醒（包含`选课成功`，`退课成功`，`cookie过期`）

```
utils/send_email.py
```

#### 2.7 检查`cookie`是否已经过期

```
utils/handle_post_result.py
```

#### 2.8 排除符合条件但不想选择的课程
```
utils/withdraw_exclude_courses.py
```
在`exclude.json`中添加需要排除的课程号后，系统会在下一次执行`main.py`时尝试退掉其中所有课程，之后也不会对其中的课程执行选课操作


### 3. 使用方式


#### 运行逻辑：
- 每1分钟执行`main.py`
  - 首先读取`exclude.json`，查看是否有已经排除但仍然已选的报告，如果存在，尝试退课，若退课成功，发送`退课成功`提醒邮件
  - 然后查询特定院系的报告，看是否有上新，如果有上新，则尝试选课，选课成功，发送`选课成功`的提醒邮件
  - 若上新的报告是`exclude.json`中已经排除的报告，不会选择该课程
  - 若`cookie`过期，则发送`cookie过期`提醒邮件
  - 如果没有报告上新，程序结束
- 每30分钟执行`main_update_weu.py`
  - 更新`cookie`中的`_WEU`字段用于保活

`Python`版本推荐`>= 3.9`</br></br>


#### 3.1 下载到本地

```bash
sudo pip3 install PyYAML python-dotenv requests             # 安装依赖
```
```bash
git clone https://github.com/1540975647/ustc_grab_report_course.git
```

```bash
cd ustc_grab_report_course/
```


#### 3.2 在`config.yml`中配置`email` ，`cookies`，`particular_course`和查询信息

```bash
cp config.template.yml config.yml
vim config.yml
```

```yaml
email:
  # 邮件发送人 
  sender: xx@xx.com                                           # 必须修改
  # 邮件接收人（可以和发送人相同，也就是自己发给自己）          
  receiver: xx@xx.com                                         # 必须修改
  # 需开启SMTP          
  smtp:          
    # SMTP邮件服务器，根据使用的SMTP服务器修改          
    server: smtp.qq.com             
    # SMTP邮件服务器端口号，根据使用的SMTP服务器修改          
    port: 465          
    # SMTP邮件服务器授权码，对应的是发送人的邮箱          
    auth_code: xxxxxxxxxxxxxxxxxxxxx                          # 必须修改
```
```yaml
data-raw:          
  # 分页查询条件信息          
  querySetting:                                               # 非必须
```
```yaml
# 需要自行登录平台抓包获取（Chrome可按F12打开开发者工具，打开网络，选择一个文件查看其请求头）
cookies:
  GS_DBLOGIN_TOKEN: xxxxxxxxxxxxxxxxxxxxx                     # 必须修改
  GS_SESSIONID: xxxxxxxxxxxxxxxxxxxxx                         # 必须修改
  EMAP_LANG: zh                                               # 非必须
  THEME: blue                                                 # 非必须
  _WEU: xxxxxxxxxxxxxxxxxxxxx                                 # 必须定时修改(可使用main_update_weu.py)
  route: xxxxxxxxxxxxxxxxxxxxx                                # 必须修改
```

```yaml
particular_course:
  # 用于保活cookie中_WEU字段的特殊课程编号
  # 这个课程，系统会每隔30分钟先退课，再在1分钟后选课
  BGBM: xxxxxxxxxxxxxxxxxxxxx                                 # 建议设为一个真实的可选人数多且过期距今较久的课程
```

```bash
:wq
```

#### 3.3 排除不想选的课

对于某些符合搜索条件的报告（比如在东区、西区，~~或者由微电子学院开设的~~），系统选课成功但手动退掉后，系统还会重新选课。如果不想选择这类报告，可以通过手动配置`exclude.json`，填入需要排除的课程号`BGBM`，如果没有可设置为`[]`。
填入后，系统会在之后运行`main.py`时，尝试退掉该门课，而且未来也不会再重新对该报告进行选课操作

**注意**：最后一个课程后不要添加`,`
```bash
cp exclude.template.json exclude.json
vim exclude.json
```

```json
{
  "EXCLUDE_BGBM": [
    "04cba049ba9a4fcba73e4800ba1607d3", 
    "de253fc99d1a40d6af0fb3b8826e0ec0", 
    "55914b1de2c844e787b257c9f04a4bbc"  
  ]
}
```

```bash
:wq
```



#### 3.4 配置定时任务

由于需要一直发送搜索信息确保有报告上新，故建议使用定时任务

**注：下方定时任务`3.4.1`和`3.4.2`配置2选1即可**

#### 3.4.1 使用`cron`配置定时任务



```bash
crontab -e                                                  # 编辑定时任务
```

```
*/1  * * * * python3 /root/ustc_grab_report_course/main.py            # 每1分钟执行报告搜索脚本
*/30 * * * * python3 /root/ustc_grab_report_course/main_update_weu.py # 每30分钟更新一次cookie中的_WEU字段
```

```bash
:wq                                                         # 退出编辑
```

```bash
crontab -l                                                  # 查看定时任务
```

#### 3.4.2 使用`ustc_grab_runner.sh`配置定时任务

`ustc_grab_runner.sh`是一个可自动执行`3.4.1`中两个`Python`文件的脚本，下方会将该脚本设定为一个`service`，可以直接设置开关和开机自启

```bash
# 新建日志文件保存路径，默认情况下当某个日志文件夹大小超过100MB时，会删除其中
# 距今最久的日志，可在ustc_grab_runner.sh中修改大小
sudo mkdir -p /var/log/ustc_grab/{error,update,main}
```

```bash
# 添加执行权限
# 如果其中路径有变化需要自行替换
sudo chmod +x ustc_grab_runner.sh
```

```bash
# 添加服务
# 如果ustc-grab.service文件中的路径有变化需要自行替换
sudo cp ustc-grab.service /etc/systemd/system/
```

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机启动  
sudo systemctl enable ustc-grab.service

# 立即启动服务
sudo systemctl start ustc-grab.service
```

```bash
# 查看服务状态
sudo systemctl status ustc-grab.service

# 实时查看服务日志
sudo journalctl -u ustc-grab.service -f

# 查看自定义日志文件
tail -f /var/log/ustc_grab/main/yyyy-MM-dd_HH-mm-ss.txt
tail -f /var/log/ustc_grab/update/yyyy-MM-dd_HH-mm-ss.txt
tail -f /var/log/ustc_grab/error/yyyy-MM-dd_HH-mm-ss.txt
```

```bash
# 停止或重启服务（可选）
sudo systemctl stop ustc-grab.service
sudo systemctl restart ustc-grab.service
```

