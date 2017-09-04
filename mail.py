#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
