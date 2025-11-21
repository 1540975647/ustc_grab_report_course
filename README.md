# USTC研究生综合服务平台学术报告自动选课

### 1. 制作该脚本的缘由

由于USTC某`225学院`从`2025级`开始要求必须选够至少`8`个学术报告，才能进行毕业论文的开题，但是仅允许选择某些学院开设的报告，而且由于该学院人数众多，符合要求的报告如果有了新的不会自动提醒选课，导致知道消息之后该报告早就被抢光了，故做此脚本。



### 2. 该脚本实现的功能

#### 2.1 根据特定的学院和新的报告降序日期查询符合条件的报告

```
utils/search_report.py
```

#### 2.2 根据报告编号`BGBM`选课

```
utils/grab_particular_course.py
```

#### 2.3 根据报告编号`BGBM`退课

```
utils/withdraw_particular_course.py
```

#### 2.4 发送邮件提醒

```
utils/send_email.py
```


#### 2.5 先查报告，如果有上新符合条件的报告，则选课，选课成功，发送`选课成功`提醒邮件

```
main.py
```

#### 2.6 更新`cookie`中的`_WEU`字段保活

```
main_update_weu.py
```

#### 2.7 `cookie`过期时发送`cookie过期`提醒邮件

```
handle_post_result.py
```

#### 2.8 排除符合条件但不想选择的课程
在`exclude.json`中添加需要排除的课程号

### 3. 使用方式

`Python`版本推荐`>=3.9`

#### 3.1 下载到本地

```bash
sudo pip install PyYAML python-dotenv requests             # 安装依赖
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
  # 邮件接收人          
  receiver: xx@xx.com                                         # 必须修改
  # 需开启SMTP          
  smtp:          
    # SMTP邮件服务器，根据使用的SMTP服务器修改          
    server: smtp.qq.com             
    # SMTP邮件服务器端口号，根据使用的SMTP服务器修改          
    port: 465          
    # SMTP邮件服务器密钥          
    auth_code: xxxxxxxxxxxxxxxxxxxxx                          # 必须修改
```
```yaml
data-raw:          
  # 分页查询条件信息          
  querySetting:                                               # 非必须
```
```yaml
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
  BGBM: xxxxxxxxxxxxxxxxxxxxx                                 # 建议设为一个真实的可选人数多且过期距今较久的课程
```

```bash
:wq
```

#### 3.3 排除不想选的课

对于某些符合搜索条件的课程，如果不想选择该课程，可以通过手动配置`exclude.json`，需填入需要排除的课程号`BGBM`，如果没有可设置为`[]`

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

*此处配置的内容仅针对于自动搜索课程并选课的逻辑，如手动或使用`grab_particular_course.py`对**排除的课程**选课，仍可以选课成功*

#### 3.4 配置定时任务

由于需要一直发送搜索信息确保有报告上新，故建议使用定时任务

**注：下方定时任务`3.4.1`和`3.4.2`配置2选1即可**

#### 3.4.1 使用`cron`配置定时任务



```bash
crontab -e                                                  # 编辑定时任务
```

```
*/1  * * * * python /root/ustc_grab_report_course/main.py            # 每1分钟执行报告搜索脚本
*/30 * * * * python /root/ustc_grab_report_course/main_update_weu.py # 每30分钟更新一次cookie中的_WEU字段
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

