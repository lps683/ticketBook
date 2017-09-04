#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
"""
File: book.py
Author: liupeisen
Date: 2017/07/31 20:22:57
"""
from splinter.browser import Browser
from time import sleep
import datetime
import mail
import sys


url = "http://www.wentiyun.cn/venue-722.html"

executable_path = {'executable_path':'/usr/local/Cellar/chromedriver/2.31/bin/chromedriver'}


def test(b):
    #模拟一个成功框
    js = "jAlert(\"预订成功!\", \"提示\", function(){});"
    b.execute_script(js)

def timeCondition(h=7.0,m=1.0,s=0.0):
    now = datetime.datetime.now()
    dateStr = now.strftime('%H-%M-%S')
    hour, minute, second = dateStr.split('-')
    t1 = h*60.0 + m + s/60.0
    t2 = float(hour)*60.0 + float(minute) + float(second)/60.0
    if t1 >= t2:
        return True
    return False

def visitWeb(url):
    #访问网站
    #b = Browser(driver_name="chrome")
    b = Browser('chrome', **executable_path)
    b.visit(url)
    return b

def login(b, username, passwd):
    try:
        lf = b.find_link_by_text(u"登录")
        sleep(0.1)
        b.execute_script("window.scrollBy(300,0)")
        lf.click()
        b.fill("username",username) # username部分输入自己的账号
        b.fill("password",passwd) # passwd部分输入账号密码
        button = b.find_by_name("subButton")
        button.click()
    except Exception, e:
        print "登录失败，请检查登陆相关:", e
        sys.exit(1)

def getBookTime():
    #今天订明天
    date = datetime.datetime.now() + datetime.timedelta(days=1)
    dateStr = date.strftime('%Y-%m-%d')
    year, month, day = dateStr.split('-')
    date = '/'.join([month, day])
    return date

def book(b):
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

def tryBook(username, passwd):
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

def main():
    #读取用户名，密码
    if len(sys.argv) == 3:
        username = sys.argv[1]
        passwd = sys.argv[2]
    else:
        print "error input parameter: %s" % (len(sys.argv)-1)
        sys.exit(1)
    print ">>>>>>>>>>>>用户名: %s<<<<<<<<<<<" % username
    print "================LOG================="
    start = datetime.datetime.now()
    startStr = start.strftime('%Y-%m-%d %H:%M:%S')
    print "开始时间: %s" % startStr 
    ret = tryBook(username, passwd)
    end = datetime.datetime.now()
    endStr = end.strftime('%Y-%m-%d %H:%M:%S')
    print "结束时间: %s" % endStr
    print "共耗时:%s秒" % (end-start).seconds
    #邮件通知结果
    msg = ''
    if ret:
        msg = "%s,wonderful!book finished!" % username
    else:
        msg = "%s,sorry, book failed!please check your code!" % username
    mail.send(msg)
    print "=================END=================="

if __name__ == "__main__":
    main()
