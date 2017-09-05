博客原文地址：https://segmentfault.com/a/1190000011008702
## 前言
    暑假闲来无事，每天上午的宝贵时间想去游泳，减减肚子，练练耐力，正好我们那个地方游泳馆上午提供免费的票，但是，需要前一天早上七点开始预定第二天上午的免费游泳票。往年暑假，我是每天早上六点五十五准时起床，眼睛半睁不睁的等着七点一到，立马抢票！抢完一脸解脱地瘫倒在床上继续睡觉。简直就是煎熬啊，我在学校都没起这么早过。
    今年暑假，我实在是不想再早起了，考虑到订票网站的订票流程非常简易，是否能写一个脚本代替我每天早上完成订票任务呢。答案是肯定的。最后我大概虽然其实用到的方法很简单，但是既然是在生活中难得遇到的实际问题，我也做一个分享。之前我是没有任何刷票、爬虫经历的。（本人专注数据挖掘）
    技术改变生活，本篇博客的目的仅仅是分享并记录一下用互联网方法解决懒人在生活中的实际问题。

## 背景
订票网站：[韵动株洲游泳馆订票网站](http://www.wentiyun.cn/venue-722.html)
订票规则：用户当天7:00—22:00，预约第二日免费游泳公益券领取资格，每位用户每天只能预订一张（如有余票当天也可预订）。
游泳馆概况：（嘿嘿，我大**株洲**就是厉害）
![这里写图片描述](http://img.blog.csdn.net/20170904213143940?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
![这里写图片描述](http://img.blog.csdn.net/20170904213200356?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
**注意：本脚本只实现简单的订票功能，因为该网站无需验证码（很多外行的朋友，虽然我也是外行，都问我能不能帮忙去12306抢票。。。）**

## 功能目标
1. 自动登录功能（**无验证码！**）
2. 自动选择预定场地、时间等信息，并提交表单
3. 支持多账号同时进行刷票任务
4. 定时任务
5. 邮件提醒抢票结果

## 工具模块
1. python
2. [splinter](https://splinter.readthedocs.io/en/latest/)
3. shell
4. [crontab](http://blog.csdn.net/xiyuan1999/article/details/8160998)或[plist](http://www.cnblogs.com/hanlingzhi/p/6505967.html)

## 流程分析
直接进入游泳馆预订界面（还有很多其他的运动项目可以预约哦，羽毛球、室内足球...真想给株洲政府点个赞）
![这里写图片描述](http://img.blog.csdn.net/20170904213222175?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
点击右上角登录按钮进入登录页面
![这里写图片描述](http://img.blog.csdn.net/20170904213410788?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
输入手机账号和密码，点击登录按钮进入登录状态，此时页面会跳转到预订界面
![这里写图片描述](http://img.blog.csdn.net/20170904213431567?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
选择好预定日期、预定时间，点击确认预订按钮确认预订
![这里写图片描述](http://img.blog.csdn.net/20170904213447889?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
确认对话框点击确认，完成所有预订过程（非预订时间或者预定完了所以这里显示"undefined"）
以上就是整个预定流程，很简单吧！正是这么简单，让我萌生了花点时间写个脚本来代替我订票的邪恶想法！

## 功能实现
### Splinter环境配置
- [下载并安装splinter](http://blog.csdn.net/revitalizing/article/details/50520927)
- [下载并安装chrome Web驱动](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- [python splinter参考教程](https://zhuanlan.zhihu.com/p/20545751)

### 访问[游泳馆预定界面](http://www.wentiyun.cn/venue-722.html)
```python
from splinter.browser import Browser
from time import sleep
import datetime
import mail
import sys
url = "http://www.wentiyun.cn/venue-722.html"
#配置自己的chrome驱动路径
executable_path = {'executable_path':'/usr/local/Cellar/chromedriver/2.31/bin/chromedriver'}

def visitWeb(url):
    #访问网站
    b = Browser('chrome', **executable_path)
    b.visit(url)
    return b
```

### 进入[登录页面](http://www.wentiyun.cn/login.html)并账号密码登录
```python
def login(b, username, passwd):
    try:
        lf = b.find_link_by_text(u"登录")#登录按钮是链接的形式
        sleep(0.1)
        b.execute_script("window.scrollBy(300,0)")#下滑滚轮，将输入框和确认按钮移动至视野范围内
        lf.click()
        b.fill("username",username) # username部分输入自己的账号
        b.fill("password",passwd) # passwd部分输入账号密码
        button = b.find_by_name("subButton")
        button.click()
    except Exception, e:
        print "登录失败，请检查登陆相关:", e
        sys.exit(1)
```

### 持续刷票策略
一旦以用户的身份进入到预订界面，就需要按时间、场地信息要求进行选择，并确认。考虑到很可能提前预约或其他情况导致某次订票失败，所以，仅仅一次订票行为是不行的，需要反复订票行为，直到订票成功，于是，订票策略如下：
1. 反复订票行为，退出条件：订票一分钟，即到七点过一分后退出，或预订成功后退出
2. 一次完整的订票退出后（满足1退出条件），为了保险，重启chrome，继续预订操作，十次操作后，退出预订程序
3. 时间选择：获取明天日期，选择预订明天的游泳票
```python
def getBookTime():
    #今天订明天，时间逻辑
    date = datetime.datetime.now() + datetime.timedelta(days=1)
    dateStr = date.strftime('%Y-%m-%d')
    year, month, day = dateStr.split('-')
    date = '/'.join([month, day])
    return date
```
```python
def timeCondition(h=7.0,m=1.0,s=0.0):
	#退出时间判断
    now = datetime.datetime.now()
    dateStr = now.strftime('%H-%M-%S')
    hour, minute, second = dateStr.split('-')
    t1 = h*60.0 + m + s/60.0
    t2 = float(hour)*60.0 + float(minute) + float(second)/60.0
    if t1 >= t2:
        return True
    return False
```
```python
def book(b):
	#反复订票行为,直到时间条件达到或预订成功退出
    while(True):
        start = datetime.datetime.now()
        startStr = start.strftime('%Y-%m-%d %H:%M:%S')
        print "********** %s ********" % startStr
        try:
            #选择日期
            date = getBookTime()
            b.find_link_by_text(date).click()
            #按钮移到视野范围内
            b.execute_script("window.scrollBy(0,100)")
            #css显示确认按钮
            js = "var i=document.getElementsByClassName(\"btn_box\");i[0].style=\"display:true;\""
            b.execute_script(js)
            #点击确认
            b.find_by_name('btn_submit').click()
            sleep(0.1)
            b.find_by_id('popup_ok').click()
            sleep(0.1)
            #测试弹出框
            #test(b)
            #sleep(0.1)
            result = b.evaluate_script("document.getElementById(\"popup_message\").innerText")
            b.find_by_id('popup_ok').click()
            sleep(0.1)
            print result
            end = datetime.datetime.now()
            print "预订页面刷票耗时:%s秒" % (end-start).seconds
            if result == "预订成功!".decode("utf-8"):
                return True
            elif not timeCondition():
                return False
            b.reload()
        except Exception, e:
            print '预订页面刷票失败,原因:', e
            end = datetime.datetime.now()
            print "共耗时:%s秒" % (end-start).seconds
            #判读当前时间如果是7点过5分了，放弃订票
            if not timeCondition():
                return False
            b.reload()
```
```python
def tryBook(username, passwd):
	#持续刷票10次后，退出程序
    r = False
    for i in xrange(10):
        try:
            start = datetime.datetime.now()
            startStr = start.strftime('%Y-%m-%d %H:%M:%S')
            print "========== 第%s次尝试,开始时间%s ========" % (i, startStr)
            b = visitWeb(url)
            login(b, username, passwd)
            r = book(b)
            if r:
                print "book finish!"
                b.quit()
                break
            else:
                print "try %s again, 已经七点1分，抢票进入尾声" % i
                b.quit()
            end = datetime.datetime.now()
            print "========== 第%s次尝试结束,共耗时%s秒 ========" % (i, (end-start).seconds)
        except Exception, e:
            print '第%s次尝试失败，原因:%s' % (i, e)
            end = datetime.datetime.now()
            print "========== 第%s次尝试结束,共耗时%s秒 ========" % (i, (end-start).seconds)
            return False
    return r
```

### [邮件服务](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432005226355aadb8d4b2f3f42f6b1d6f2c5bd8d5263000)
- 参考廖雪峰老师的实现哦，程序其实不麻烦，主要是邮箱的SMTP服务！
- 需要邮箱开通SMTP代理服务，如果你qq号是很久之前注册的了，那我不推荐使用qq邮箱，一系列的密保会让你崩溃。推荐使用新浪邮箱。
- 发送程序如下mail.py

```python
import smtplib  
import traceback  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from email.header import Header
from email.utils import parseaddr, formataddr
'''
to_addr = "844582201@qq.com"  
password = "*****"  
from_addr = "m13072163887@163.com"  
msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
server = smtplib.SMTP("smtp.163.com") # SMTP协议默认端口是25
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()
'''
'''
    @subject:邮件主题 
    @msg:邮件内容 
    @toaddrs:收信人的邮箱地址 
    @fromaddr:发信人的邮箱地址 
    @smtpaddr:smtp服务地址，可以在邮箱看，比如163邮箱为smtp.163.com 
    @password:发信人的邮箱密码 
''' 
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
    
def sendmail(subject,msg,toaddrs,fromaddr,smtpaddr,password):  
    mail_msg = MIMEMultipart()  
    if not isinstance(subject,unicode):  
        subject = unicode(subject, 'utf-8')  
    mail_msg['Subject'] = subject  
    mail_msg['From'] = _format_addr('Python-auto <%s>' % fromaddr)
    mail_msg['To'] = ','.join(toaddrs)  
    mail_msg.attach(MIMEText(msg, 'plain', 'utf-8'))  
    try:  
        s = smtplib.SMTP()  
        s.set_debuglevel(1)
        s.connect(smtpaddr,25)  #连接smtp服务器  
        s.login(fromaddr,password)  #登录邮箱  
        s.sendmail(fromaddr, toaddrs, mail_msg.as_string()) #发送邮件  
        s.quit()  
    except Exception,e:  
       print "Error: unable to send email", e  
       print traceback.format_exc()  

def send(msg):
    fromaddr = "mynameislps@sina.com"  
    smtpaddr = "smtp.sina.com"
    password = "*****"  
    subject = "这是邮件的主题"
    toaddrs = ["844582201@qq.com"]
    sendmail(subject,msg,toaddrs,fromaddr,smtpaddr,password)
```
### 定时任务策略
每天七点，抢票开始。为了保险并且考虑到上文所构建的抢票策略，我们可以六点五十九分开始操作（考虑到还要访问预订页面、登录页面以及登录操作等，万一有一定的延时）。于是我们将任务布置在每天早上的六点五十九分。
定时任务的工具有两种，一种是使用Linux自带的定时工具crontab，一种是使用比较优雅的Mac自带的定时工具plist。这两种工具非常简单实用，这里也不做太多介绍。

### 多账号同时订票操作策略
这就需要借助强大的shell脚本，我们把需要订票的帐号密码信息配置在shell内，同时shell根据这些帐号信息启动不同的进程来同时完成订票任务。
```shell
#!/bin/bash
my_array=("130****3887" "****"\
        "187****4631" "****")
#待操作用户个数
len=${#my_array[@]}
len=`expr $len / 2`
i=0
while (($i < $len))
do 
    echo "第($i)个用户为: ${my_array[2*i]}"
    logname="/Users/lps/work/program/ticketReservation/log/${my_array[2*i]}.log"
    nohup /Users/lps/anaconda/bin/python /Users/lps/work/program/ticketReservation/book.py ${my_array[2*i]} ${my_array[2*i+1]} > ${logname} 2>&1 &
    i=`expr $i + 1`
done
```

### 日志服务
良好、健壮的程序需要一套比较完备的日志系统，本程序的日志服务都在上文中的程序中反映了，当然不见得是最好的。仅供参考。这方便我们定位错误或失败的发生位置！


[完整的工程](https://github.com/lps683/ticketBook)在Github上：https://github.com/lps683/ticketBook

## 某些蛋疼的问题
- 需要将按钮／链接显示在视野范围内才能进行点击操作。上文程序中诸如`b.execute_script("window.scrollBy(300,0)")`等操作都是上下调整页面位置，将按钮显示在视野范围内；如果某些按钮是invisible的，那么我们可以通过修改JS中控件的属性来显示按钮。如上文程序中的
```python
#css显示确认按钮
js = "var i=document.getElementsByClassName(\"btn_box\");i[0].style=\"display:true;\""
b.execute_script(js)
```
- 弹出框定位问题：最后预定成功会弹出一个确认框：
![这里写图片描述](http://img.blog.csdn.net/20170904213511921?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHBzNjgz/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
那要获得这个对话框并不容易。我尝试过诸如`alert = browser.get_alert() alert.text alert.accept() alert.dismiss()`之类的办法都没有成功。最后右键这个对话框，找到它的源码，根据ID信息找到这个对话框才解决的！

## 总结
1. 技术上来说，本文并没有什么亮点，如果要应付12306等一系列的网站，那还有很多很麻烦的东西要研究。但是，能用技术来解决生活中的实际问题，何乐而不为呢！
2. 其实这个定时订票程序是一个很流程化的东西，实际上就是程序在模拟人的各种行为，所以在coding前一定要好好测试网站订票流程，把握订票的规律。
3. 有和同学交流，如果能catch到预定的消息格式，那岂不是更加简便了！嗯，我觉得很有道理，不过没有作尝试，我对真正的那些刷票软件也非常感兴趣，但是现在还没有时间去研究，也欢迎大牛指点！

