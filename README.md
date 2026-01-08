# USTC研究生综合服务平台学术报告自动选课

#### 郑重声明：本项目旨在通过自动化方式监控研究生学术报告课程的实时变化，并在出现可选择报告时发送通知，提高信息获取效率；本工具严格限制请求频率，仅用于学习自动化脚本与系统工程的实践；不会进行高频访问或突破系统限制，也不会影响服务器正常运行；若擅自修改执行间隔，导致被服务器封禁，后果自负！

### 1. 制作该脚本的缘由

由于USTC某`225学院`从`2025级`开始要求必须选够至少`8`个学术报告，才能进行毕业论文的开题，但是仅允许选择某些学院开设的报告，而且由于该学院人数众多，符合要求的报告如果有了新的不会自动提醒选课，导致知道消息之后该报告早就被抢光了，故做此脚本。

### 2. 该脚本实现的功能

本项目已重构为模块化的 Python 包 `ustc_grab`，提供更优雅的代码结构和更好的维护性。

#### 2.1 主程序与选课逻辑
```
main.py
```
负责调用 `ustc_grab` 包执行选课循环：
- 自动退掉在 `data/exclude.json` 中配置的课程。
- 搜索并筛选符合条件的报告。
- 自动抢课并发送邮件通知。

#### 2.2 自动保活
```
main_update_weu.py
```
负责定时更新 `_WEU` cookie 字段，防止会话过期。经过测试，`cookie`中的其他字段仅需手动登录平台抓包获取1次，但`_WEU`字段若不更新，会在若干小时后过期，故需要定时更新（下方会设置`30分钟`更新一次）。~~至于其他字段什么时候过期我也还不清楚，反正现在跑了2-3个月了还没过期，如果过期了就重新登录平台抓一下吧orz。~~

#### 2.3 功能模块 (在 `ustc_grab/` 包中)
- **核心逻辑** (`ustc_grab/manager.py`): 统筹搜索、选课、退课、查成绩等流程。
- **网络请求** (`ustc_grab/client.py`): 封装 `HTTP` 请求，自动处理复杂的查询参数和 `Headers`。
- **配置管理** (`ustc_grab/config.py`): 统一管理配置，支持 `.env` 和 `config.yml`。
- **邮件通知** (`ustc_grab/notification.py`): 发送选课成功、失败及 Cookie 过期通知。

#### 2.4 成绩监控 (可选功能)

本系统还实现了成绩查询功能，~~（你以为脚本名字叫查报告我就只查报告吗？）~~，会自动轮询 `/wdcjapp` 接口查询成绩，如有新出的成绩（通过唯一 `ID` 和本地缓存对比），自动发送详细的邮件通知（包含课程名、分数、绩点）。
**默认关闭**，需在配置文件中开启。
~~有心脏病或者高血压的记得千万别开，不然到时候一个邮件发过来发现挂科了有点猝不及防。~~

### 3. 使用方式

#### 运行逻辑：
- 每1分钟执行`main.py`
  - **(若开启)** 查询是否有新成绩发布并与`data/grades.json`比对，如果有，发送`成绩通知`提醒邮件
  - 读取`data/exclude.json`，查看是否有已经排除但仍然已选的报告，如果存在，尝试退课，若退课成功，发送`退课成功`提醒邮件
  - 然后查询特定院系的报告，看是否有上新，如果有上新，则尝试选课，选课成功，发送`选课成功`提醒邮件
  - 若符合条件的报告是`data/exclude.json`中已经排除的报告，不会选择该课程
  - 若`cookie`过期，则发送`cookie过期`提醒邮件
  - 如果没有报告上新，程序结束
- 每30分钟执行`main_update_weu.py`
  - 更新`cookie`中的`_WEU`字段用于保活

> **`Python`版本推荐`>=3.9`**

#### 3.1 下载到本地与安装依赖

```bash
git clone https://github.com/1540975647/ustc_grab_report_course.git
cd ustc_grab_report_course/
```

安装所需依赖：
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip3 install -r requirements.txt
```

#### 3.2 配置 `config.yml`

在`config.yml`中配置`email` ，`cookies`，`particular_course`和查询信息。模板文件位于 `templates/` 目录。

```bash
cp templates/config.template.yml config.yml
vim config.yml
```

```yaml
# 是否开启成绩自动查询 (默认 false，可修改为 true)
enable_grade_check: false
```

```yaml
email:
  # 邮件发送人 
  sender: xx@xx.com                                           # 必须修改
  # 邮件接收人          
  receiver: xx@xx.com                                         # 必须修改
  # 需自行开启SMTP          
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
  # 不建议修改，如若需要选特定学院的报告，请进入config.template.yml中查看          
  querySetting:                                               # 非必须
```

```yaml                                              
# 需要自行登录平台抓包获取（Chrome可按F12，打开网络，选择一个文件查看其请求头）
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

#### 3.3 排除不想选的课

对于某些符合搜索条件的课程，如果不想选择该课程，可以通过手动配置`data/exclude.json`，填入需要排除的课程号`BGBM`。

> **注意：** 最后一个课程号后不要加`,`

```bash
vim data/exclude.json
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

#### 3.4 配置定时任务

建议使用定时任务以确保及时获取报告信息。

**注：下方定时任务`3.4.1`和`3.4.2`配置2选1即可**

> **安全提示**: 建议不要使用 `root` 用户运行此服务。

#### 3.4.1 使用`cron`配置定时任务

```bash
crontab -e                                                  # 编辑定时任务
```

```
*/1  * * * * /path/to/ustc_grab_report_course/venv/bin/python3 /path/to/ustc_grab_report_course/main.py            # 每1分钟执行报告搜索脚本
*/30 * * * * /path/to/ustc_grab_report_course/venv/bin/python3 /path/to/ustc_grab_report_course/main_update_weu.py # 每30分钟更新一次cookie中的_WEU字段
```

```bash
crontab -l                                                  # 查看定时任务
```
#### 3.4.2 使用`ustc_grab_runner.sh`配置定时任务

`scripts/ustc_grab_runner.sh`是一个可自动执行`3.4.1`中两个`Python`文件的脚本。

> **注意**: 该脚本现在会自动查找项目根目录下的 `venv` 环境。无需手动修改 python 路径，但请确保 `venv` 存在。


```bash
# 新建日志文件保存路径
sudo mkdir -p /var/log/ustc_grab/{error,update,main}
```

```bash
# 添加执行权限
sudo chmod +x scripts/ustc_grab_runner.sh
```

```bash
# 添加服务
# 1. 创建专用系统用户 (建议)
sudo useradd -r -s /bin/false ustc-grab

# 2. 移动项目代码到推荐目录 /etc (可选，也可以修改 service 文件中的路径)
sudo mv ustc_grab_report_course /etc/
cd /etc/ustc_grab_report_course

# 3. 设置权限 (让 ustc-grab 用户拥有读写权限)
sudo chown -R ustc-grab:ustc-grab .
sudo chown -R ustc-grab:ustc-grab /var/log/ustc_grab

# 4. 复制服务文件
sudo cp scripts/ustc-grab.service /etc/systemd/system/

# 5. 重新加载 systemd 配置
sudo systemctl daemon-reload

# 6. 启动服务
sudo systemctl start ustc-grab.service

# 7. 查看服务状态
sudo systemctl status ustc-grab.service
```

```bash
# 可选项
# 启用开机启动 
sudo systemctl enable ustc-grab.service
# 重启服务 
sudo systemctl restart ustc-grab.service
# 关闭服务 
sudo systemctl stop ustc-grab.service
```

```bash
# 查看实时日志 (方式1: Systemd Journal)
# 脚本已实现双重输出，您可以通过 journalctl 查看所有日志
sudo journalctl -u ustc-grab.service -f

# 查看实时日志 (方式2: 文件日志)
# 日志同时也会保存在 /var/log/ustc_grab/ 下 (自动轮转清理，限制 100MB)
tail -f /var/log/ustc_grab/main/$(date +%Y-%m-%d)*.txt
```
