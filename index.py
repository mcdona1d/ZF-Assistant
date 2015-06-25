#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import web
import time
import json
import MySQLdb
import hashlib
import urllib
import urllib2
import cookielib
from lxml import etree
from weixin import WeiXinClient
from bs4 import BeautifulSoup
 
 
urls = (
'/weixin','WeixinInterface'
)

reload(sys)
sys.setdefaultencoding("utf-8")

my_appid = '' #填写你的appid
my_secret = '' #填写你的app secret

jw_url='http://' #你的教务系统地址
jw='' #你的教务系统地址

website = '' #挂载网页用到的域名

def _check_hash(data):
    #sha1加密算法
    signature=data.signature
    timestamp=data.timestamp
    nonce=data.nonce
    #自己的token
    token="wjhahaha" #这里改写你在微信公众平台里输入的token
    #字典序排序
    list=[token,timestamp,nonce]
    list.sort()
    sha1=hashlib.sha1()
    map(sha1.update,list)
    hashcode=sha1.hexdigest()
    #如果是来自微信的请求，则回复True
    if hashcode == signature:
        return True
    return False

def _do_event_subscribe(server, fromUser, toUser, xml):
    return server._reply_text(fromUser, toUser, u'欢迎关注海滨学院官方微信，使用查询功能请先绑定学号，绑定方法 “#学号#密码”，例如“#12111000#password”，绑定后即可使用全部功能，感谢关注')
    
def _do_event_unsubscribe(server, fromUser, toUser, xml):
    try:
        username = _get_username(fromUser, server.client)
        
        
        if (re.match(username,fromUser)):
            pass
        else:
            try:
                conn=MySQLdb.connect(host='localhost',user='root',passwd='wj949925',db='wechat_servers',port=3306)
                cur=conn.cursor()
                sql='delete from user where openid = "%s"' %(fromUser)
                cur.execute(sql)
                conn.commit()
                conn.close()
                pass
            except MySQLdb.Error,e:
                print "数据库异常，解绑失败，请稍候重试"
    except Exception, e:
        
        print "解绑出错，请稍候再试(ubd time check bd info)"

    return server._reply_text(fromUser, toUser, u'bye!')

def _do_event_SCAN(server, fromUser, toUser, xml):
    pass

def _do_event_LOCATION(server, fromUser, toUser, xml):
    pass

def _do_event_VIEW(server, fromUser, toUser, xml):
    pass

def _do_event_CLICK(server, fromUser, toUser, xml):
    key = xml.find('EventKey').text
    try:
        return _weixin_click_table[key](server, fromUser, toUser, xml)
    except KeyError, e:
        print '_do_event_CLICK: %s' %e
        return server._reply_text(fromUser, toUser, u'Unknow click: '+key)


_weixin_event_table = {
    'subscribe'     :   _do_event_subscribe,
    'unsubscribe'   :   _do_event_unsubscribe,
    'SCAN'          :   _do_event_SCAN,
    'LOCATION'      :   _do_event_LOCATION,
    'CLICK'         :   _do_event_CLICK,
    'VIEW'          :   _do_event_VIEW,

}

def _get_username(openid, client):
    selectid=openid
    conn=MySQLdb.connect(host='localhost',user='root',passwd='wj949925',db='wechat_servers',port=3306)
    cur=conn.cursor()
    sql='select * from user where openid = "%s"' %(selectid)

    try:   
        cur.execute(sql)
        conn.commit()
        conn.close()
        results = cur.fetchall()

        for row in results:
            selectid = row[1]
        
        return selectid

    except MySQLdb.Error,e:
        conn.rollback()
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return none

def _get_password(openid, client):
    selectpw=openid
    conn=MySQLdb.connect(host='localhost',user='root',passwd='wj949925',db='wechat_servers',port=3306)
    cur=conn.cursor()
    sql='select * from user where openid = "%s"' %(selectpw)

    try:   
        cur.execute(sql)
        conn.commit()
        conn.close()
        results = cur.fetchall()

        for row in results:
            selectpw = row[2]
        
        return selectpw

    except MySQLdb.Error,e:
        conn.rollback()
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return none

def _link_schoolid(server, fromUser, toUser,content, openid):
    #1.先检查绑定情况 
    #2.输入格式 
    #3.验证帐号对错 
    #4.写入数据库绑定成功
    #进入提取信息账号绑定环节
    

    try:
        username = _get_username(openid, server.client)
        
        
        if (re.match(username,openid)):
            
            try:
                bd_str="#([0-9]*)#(\w*)"
                bd_info = re.search(bd_str,content)
                std_id=bd_info.group(1)
                std_pass=bd_info.group(2)
                
                #return self._reply_text(fromUser, toUser, u'xh:' + std_id +u'pass:' + std_pass +u'openid:' + openid)
                
            except KeyError, e:
                return server._reply_text(fromUser, toUser, u'您输入的学号密码格式错误，请检查后重试')
            
            loginURL = jw_url+'/default6.aspx'      #this is the login page for xupt
            
            #ID = std_id
            #Password =  std_pass
            #print 'Loading........'
            page = urllib2.urlopen(loginURL).read()
            view = r'name="__VIEWSTATE" value="(.+)" '
            view = re.compile(view)
            finaview = view.findall(page)[0]

            postdata = urllib.urlencode({
                    '__VIEWSTATE':finaview,        
                    'txtYhm':std_id,                #std ID
                    'txtMm':std_pass,           #password
                        'rblJs':'学生',
                        'btnDl':' 登录'})         
            headers = {
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            
            cookie = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            myRequest = urllib2.Request(loginURL, postdata,headers)
            loginPage = opener.open(myRequest).read()
            page =  unicode(loginPage, 'gb2312').encode("utf-8")
            
            
            Sname = r'<span id="xhxm">(.+)同学</span>'
            Sname = re.compile(Sname)
            try:
                std_name = Sname.findall(page)[0]
            except IndexError, e:
                return server._reply_text(fromUser, toUser, u"您输入的学号或密码有误，请检查后重试")
                #print "User-name or password error, try again!"
                
            
            try:
                conn=MySQLdb.connect(host='localhost',user='root',passwd='wj949925',db='wechat_servers',port=3306)
                cur=conn.cursor()
                sql='insert into user (openid,schoolid,password) values ("%s","%s","%s")' %(openid,std_id,std_pass)
                cur.execute(sql)
                conn.commit()
                conn.close()
                return server._reply_text(fromUser, toUser, u'恭喜您！'+std_name+'同学，账号绑定成功！您现在可以使用本平台的全部功能！如需解绑请回复 “解绑”')
            except MySQLdb.Error,e:
                return server._reply_text(fromUser, toUser, u'数据库写入失败，请稍候再试')   
        else:
            return server._reply_text(fromUser, toUser, u"此微信账号已经绑定学号，不能重复绑定！请先解绑后操作")
    except Exception, e:
        
        return server._reply_text(fromUser, toUser, u"绑定出错，请稍候再试(bd time check bd info)")



def _unlink_schoolid(server, fromUser, toUser, openid):
    #进入解除绑定环节
    try:
        username = _get_username(openid, server.client)
        
        
        if (re.match(username,openid)):
            return server._reply_text(fromUser, toUser, u"账号未绑定")
        else:
            try:
                conn=MySQLdb.connect(host='localhost',user='root',passwd='wj949925',db='wechat_servers',port=3306)
                cur=conn.cursor()
                sql='delete from user where openid = "%s"' %(openid)
                cur.execute(sql)
                conn.commit()
                conn.close()
                return server._reply_text(fromUser, toUser, u'账号解绑成功！')
            except MySQLdb.Error,e:
                return server._reply_text(fromUser, toUser, u'数据库异常，解绑失败，请稍候重试')
    except Exception, e:
        
        return server._reply_text(fromUser, toUser, u"解绑出错，请稍候再试(ubd time check bd info)")
    
#def _do_change_ALARM_OFF(server, fromUser, toUser, xml):
#    return server._reply_text(fromUser, toUser, u"检测报警开")  


def _do_click_CHECKCLASSTABLE(server, fromUser, toUser, xml):
    #find username and password from database
    openid = xml.find('FromUserName').text
    try:
        username = _get_username(openid, server.client)
        password = _get_password(openid, server.client)
        if (re.match(username,openid)):
            return server._reply_text(fromUser, toUser, u"您还未绑定账号，请先绑定，绑定方法 “#学号#密码”，例如“#12111000#password”，绑定后即可使用全部功能")
        else:
             #开始查询
            loginURL = jw_url+'/default6.aspx'      #this is the login page for xupt
    
            page = urllib2.urlopen(loginURL).read()
            view = r'name="__VIEWSTATE" value="(.+)" '
            view = re.compile(view)
            finaview = view.findall(page)[0]

            postdata = urllib.urlencode({
                    '__VIEWSTATE':finaview,         
                    'txtYhm':username,              #std ID
                    'txtMm':password,           #password
                        'rblJs':'学生',
                        'btnDl':' 登录'})         
            headers = {
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            cookie = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            myRequest = urllib2.Request(loginURL, postdata,headers)
            loginPage = opener.open(myRequest).read()
            page =  unicode(loginPage, 'gb2312').encode("utf-8")        #get the cookie 
            # print page
            Sname = r'<span id="xhxm">(.+)同学</span>'
            Sname = re.compile(Sname)
            try:
                name = Sname.findall(page)[0]
            except IndexError, e:
                return server._reply_text(fromUser, toUser, u"您绑定的账号信息可能已经失效，请解绑后重新绑定")

                exit()
            else:
                pass
            
            
            # print cookie
            for i in cookie:
                Cookie = i.name+"="+i.value
            # print Cookie
            
            head = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':jw,
            'Cookie':Cookie,
            'Origin':jw_url,
            'Pragma':'no-cache',
            'Referer':jw_url+'/xs_main.aspx?xh='+username,
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            
            getdata = urllib.urlencode({
                'xh':username,
                'xm':name,
                'gnmkdm': 'N121603'

                })
           
            MyRequest= urllib2.Request(jw_url+'/xskbcx.aspx?'+getdata,None, head)     #According to this page ,we can get the viewstats
            
            #loginPage=unicode(opener.open(MyRequest).read(), 'gb2312').encode("utf-8")
            #data = urllib.urlencode({
            #   "__VIEWSTATE":getVIEW(loginPage),
            #   "__EVENTTARGET":"xqd",
            #   "xnd":"2014-2015",
            #   "xqd":"2"
            #   })
            #MyRequest= urllib2.Request('http://10.10.9.33/xskscx.aspx?'+getdata,data, head)        #Score's page
            html = opener.open(MyRequest)
            result =  unicode(html.read(), 'gb2312').encode("utf-8")
                
            #print result
            #Print (result)
            
            
            
            soup = BeautifulSoup(result)
            
            table = soup.find("table", {"id": "Table1"})
            table2 = soup.find("table", {"id": "DBGrid"})
            
            table = str(table)
            table2 = str(table2)
            
            table='<table border="1"'+table[17:]
            table2='<table border="1"'+table2[17:]

            #print table
            fo = open('/var/www/html/tableinfo/%s.html'%(username),'wb+')
            fo.write('<meta charset="utf-8"><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
            #fo.write('<table border="1"')
            fo.write(table)
            fo.write(table2)
            fo.close()
            address= '/tableinfo/%s.html"'%(username)
            reply_msg = "<a href="+website+address+">点击此处查看详细课表</a>"
            
            #print  reply_msg
            return server._reply_text(fromUser, toUser,reply_msg )
    except Exception, e:
        #err_msg += str(e)
        return server._reply_text(fromUser, toUser, u"课表查询出错!")
        

def _do_click_CHECKSCORE(server, fromUser, toUser, xml):
    #pass
    openid = xml.find('FromUserName').text
    try:
        username = _get_username(openid, server.client)
        password = _get_password(openid, server.client)
        if (re.match(username,openid)):
            return server._reply_text(fromUser, toUser, u"您还未绑定账号，请先绑定，绑定方法 “#学号#密码”，例如“#12111000#password”，绑定后即可使用全部功能")
        else:
             #开始查询
            loginURL = jw_url+'/default6.aspx'      #this is the login page for xupt
    
            page = urllib2.urlopen(loginURL).read()
            view = r'name="__VIEWSTATE" value="(.+)" '
            view = re.compile(view)
            finaview = view.findall(page)[0]

            postdata = urllib.urlencode({
                    '__VIEWSTATE':finaview,         
                    'txtYhm':username,              #std ID
                    'txtMm':password,           #password
                        'rblJs':'学生',
                        'btnDl':' 登录'})         
            headers = {
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            cookie = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            myRequest = urllib2.Request(loginURL, postdata,headers)
            loginPage = opener.open(myRequest).read()
            page =  unicode(loginPage, 'gb2312').encode("utf-8")        #get the cookie 
            # print page
            Sname = r'<span id="xhxm">(.+)同学</span>'
            Sname = re.compile(Sname)
            try:
                name = Sname.findall(page)[0]
            except IndexError, e:
                return server._reply_text(fromUser, toUser, u"您绑定的账号信息可能已经失效，请解绑后重新绑定")

                exit()
            else:
                pass
            
            
            # print cookie
            for i in cookie:
                Cookie = i.name+"="+i.value
            # print Cookie
            
            head = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':jw,
            'Cookie':Cookie,
            'Origin':jw_url,
            'Pragma':'no-cache',
            'Referer':jw_url+'/xs_main.aspx?xh='+username,
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            
            getdata = urllib.urlencode({
                'xh':username,
                'xm':name,
                'gnmkdm': 'N121605'

                })
           
            MyRequest= urllib2.Request(jw_url+'/xscjcx.aspx?'+getdata,None, head)     #According to this page ,we can get the viewstats
            
            loginPage=unicode(opener.open(MyRequest).read(), 'gb2312').encode("utf-8")
            loginview = r'name="__VIEWSTATE" value="(.+)" '
            loginview = re.compile(loginview)
            loginfinaview = view.findall(loginPage)[0]
            data = urllib.urlencode({
                "__VIEWSTATE":loginfinaview,
                "ddlXN":'2014-2015',
                "ddlXQ":'2',
                "ddl_kcxz":'',
                "btn_xq":'学期成绩'
                })
            MyRequest= urllib2.Request(jw_url+'/xscjcx.aspx?'+getdata,data, head)   
            html = opener.open(MyRequest)
            result =  unicode(html.read(), 'gb2312').encode("utf-8")
                
            #print result
            #Print (result)
            
            
            
            soup = BeautifulSoup(result)
            
            table = soup.find("table", {"id": "Datagrid1"})
            
            
            table = str(table)
            
            
            table='<table border="1"'+table[17:]
            

            #print table
            fo = open('/var/www/html/scoreinfo/%s.html'%(username),'wb+')
            fo.write('<meta charset="utf-8"><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
            #fo.write('<table border="1"')
            fo.write(table)
            
            fo.close()
            address= '/scoreinfo/%s.html"'%(username)
            reply_msg = "<a href="+website+address+">点击此处查看本学期成绩</a>"
            
            #print  reply_msg
            return server._reply_text(fromUser, toUser,reply_msg )
    except Exception, e:
        #err_msg += str(e)
        return server._reply_text(fromUser, toUser, u"成绩查询出错!")

def _do_click_CHECKEXAM(server, fromUser, toUser, xml):
    #pass
    openid = xml.find('FromUserName').text
    try:
        username = _get_username(openid, server.client)
        password = _get_password(openid, server.client)
        
        if (re.match(username,openid)):
            return server._reply_text(fromUser, toUser, u"您还未绑定账号，请先绑定，绑定方法 “#学号#密码”，例如“#12111000#password”，绑定后即可使用全部功能")
        else:
            
            #开始查询
            loginURL = jw_url+'/default6.aspx'      #this is the login page for xupt
    
            page = urllib2.urlopen(loginURL).read()
            view = r'name="__VIEWSTATE" value="(.+)" '
            view = re.compile(view)
            finaview = view.findall(page)[0]

            postdata = urllib.urlencode({
                    '__VIEWSTATE':finaview,         
                    'txtYhm':username,              #std ID
                    'txtMm':password,           #password
                        'rblJs':'学生',
                        'btnDl':' 登录'})         
            headers = {
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            cookie = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            myRequest = urllib2.Request(loginURL, postdata,headers)
            loginPage = opener.open(myRequest).read()
            page =  unicode(loginPage, 'gb2312').encode("utf-8")        #get the cookie 
            # print page
            Sname = r'<span id="xhxm">(.+)同学</span>'
            Sname = re.compile(Sname)
            try:
                name = Sname.findall(page)[0]
            except IndexError, e:
                return server._reply_text(fromUser, toUser, u"您绑定的账号信息可能已经失效，请解绑后重新绑定")

                exit()
            else:
                pass
            
            
            # print cookie
            for i in cookie:
                Cookie = i.name+"="+i.value
            # print Cookie
            
            head = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':jw,
            'Cookie':Cookie,
            'Origin':jw_url,
            'Pragma':'no-cache',
            'Referer':jw_url+'/xs_main.aspx?xh='+username,
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            
            getdata = urllib.urlencode({
                'xh':username,
                'xm':name,
                'gnmkdm': 'N121604'

                })
           
            MyRequest= urllib2.Request(jw_url+'/xskscx.aspx?'+getdata,None, head)     #According to this page ,we can get the viewstats
            
            #loginPage=unicode(opener.open(MyRequest).read(), 'gb2312').encode("utf-8")
            #data = urllib.urlencode({
            #   "__VIEWSTATE":getVIEW(loginPage),
            #   "__EVENTTARGET":"xqd",
            #   "xnd":"2014-2015",
            #   "xqd":"2"
            #   })
            #MyRequest= urllib2.Request('http://10.10.9.33/xskscx.aspx?'+getdata,data, head)        #Score's page
            html = opener.open(MyRequest)
            result =  unicode(html.read(), 'gb2312').encode("utf-8")
                
            #print result
            #Print (result)
            
            
            
            soup = BeautifulSoup(result)
            
            table = soup.find("table")
            
            table = str(table)
            table='<table border="1"'+table[17:]
            #print table
            fo = open('/var/www/html/examinfo/%s.html'%(username),'wb+')
            fo.write('<meta charset="utf-8"><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
            fo.write(table)
            fo.close()
            address= '/examinfo/%s.html"'%(username)
            reply_msg = "<a href="+website+address+">点击此处查看考试信息</a>"
            
            #print  reply_msg
            return server._reply_text(fromUser, toUser,reply_msg )
    except Exception, e:
        #err_msg += str(e)
        return server._reply_text(fromUser, toUser, u"考试信息查询出错!")

def _do_click_CHECKUSERINFO(server, fromUser, toUser, xml):
    #查询绑定信息 学号 姓名 帐号状态正常/异常
    #pass
    
    openid = xml.find('FromUserName').text
    try:
        username = _get_username(openid, server.client)
        password = _get_password(openid, server.client)
        if (re.match(username,openid)):
            return server._reply_text(fromUser, toUser, u"您还未绑定账号，请先绑定，绑定方法 “#学号#密码”，例如“#12111000#password”，绑定后即可使用全部功能，如需解除绑定请回复 “解绑”")
        else:
            loginURL = jw_url+'/default6.aspx'      #this is the login page for xupt
            
            #ID = std_id
            #Password =  std_pass
            #print 'Loading........'
            page = urllib2.urlopen(loginURL).read()
            
            view = r'name="__VIEWSTATE" value="(.+)" '
            view = re.compile(view)
            finaview = view.findall(page)[0]

            postdata = urllib.urlencode({
                    '__VIEWSTATE':finaview,        
                    'txtYhm':username,                #std ID
                    'txtMm':password,           #password
                        'rblJs':'学生',
                        'btnDl':' 登录'})         
            headers = {
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
            }
            
            cookie = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            myRequest = urllib2.Request(loginURL, postdata,headers)
            loginPage = opener.open(myRequest).read()
            page =  unicode(loginPage, 'gb2312').encode("utf-8")
            
            
            Sname = r'<span id="xhxm">(.+)同学</span>'
            Sname = re.compile(Sname)
            try:
                std_name = Sname.findall(page)[0]
            except IndexError, e:
                return server._reply_text(fromUser, toUser, u"您绑定的账号信息可能已经失效，请解绑后重新绑定")
            return server._reply_text(fromUser, toUser, u""+std_name+"同学，您的帐号状态正常，您绑定的学号为"+username+"如需解绑请回复 “解绑”")
                #print "User-name or password error, try again!"
    except Exception, e:
        #err_msg += str(e)
        return server._reply_text(fromUser, toUser, u"绑定信息查询出错!")

def _do_click_WEATHERINFO(server, fromUser, toUser, xml):
    #pass
    weatherurl ='http://weather.123.duba.net/static/weather_info/101090701.html'
    getweather = urllib2.urlopen(weatherurl).read()
    getweather=getweather[17:-1]
    loadweather = json.loads(getweather)['weatherinfo']
    reply_msg = "城市： %s \n温度： %s℃\n天气： %s\n风向： %s\n风力： %s\nPM2.5指数： %s\nPM2.5级别： %s" \
                        %(loadweather ['city'], loadweather ['temp'], loadweather ['img_title_single'],loadweather ['wd'],loadweather ['ws'],loadweather ['pm'],loadweather ['pm-level'])
    return server._reply_text(fromUser, toUser, reply_msg)

def _do_click_CALENDER(server, fromUser, toUser, xml):
    pass
    #data = _image_upload(server.client)
    #return server._reply_image(fromUser, toUser, data.media_id)
#def _image_upload(client):
    #resp='cal.jpg'
    #return client.media.upload.file(type='image', pic=resp)
def _do_click_ACTIVITYINFO(server, fromUser, toUser, xml):
    pass

def _do_click_JWINFO(server, fromUser, toUser, xml):
    pass



_weixin_click_table = {
    
    'V1001_CHECKCLASSTABLE'        :   _do_click_CHECKCLASSTABLE,
    'V1001_CHECKSCORE'             :   _do_click_CHECKSCORE,
    'V1001_CHECKEXAM'              :   _do_click_CHECKEXAM,
    'V1001_CHECKUSERINFO'          :   _do_click_CHECKUSERINFO,
    'V1001_WEATHERINFO'            :   _do_click_WEATHERINFO,
    'V1001_CALENDER'               :   _do_click_CALENDER,
    'V1001_ACTIVITYINFO'           :   _do_click_ACTIVITYINFO,
    'V1001_JWINFO'                 :   _do_click_JWINFO

}

class WeixinInterface:
 
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)
        self.client = WeiXinClient(my_appid, my_secret, fc=True, path='/tmp')
        self.client.request_access_token()

    

 

    def _recv_text(self, fromUser, toUser, xml):
        content = xml.find('Content').text
        openid = xml.find('FromUserName').text
        bdcheck_text = re.compile(r'#')
        #ubdcheck_text = re.compile(r'unlink')
        bdmatch = bdcheck_text.match(content)
        #ubdmatch = ubdcheck_text.match(content)
        if bdmatch:
            return _link_schoolid(self, fromUser, toUser, content, openid)
        elif content == '解绑':
            return _unlink_schoolid(self, fromUser, toUser, openid)
            #return self._reply_text(fromUser, toUser, u'啊！' )
            #return _do_change_ALARM_OFF(self, fromUser, toUser, xml)

        else:
            reply_msg = content
            return self._reply_text(fromUser, toUser, u'我还不能理解你说的话:' + reply_msg)
    
    def _recv_event(self, fromUser, toUser, xml):
        event = xml.find('Event').text
        try:
            return _weixin_event_table[event](self, fromUser, toUser, xml)
        except KeyError, e:
            print '_recv_event: %s' %e
            return self._reply_text(fromUser, toUser, u'Unknow event: '+event)

    def _recv_image(self, fromUser, toUser, xml):
        #url = xml.find('PicUrl').text
        #req = urllib2.Request(url)
        #try:
        #    resp = urllib2.urlopen(req, timeout = 2)
        #    print self.yee.image.upload('12345', '27360', fd = resp) #12345替换为自己的yeelink设备的id
        #except urllib2.HTTPError, e:
        #    print e
        #    return self._reply_text(fromUser, toUser, u'上传图片失败！')
        #view = 'http://www.yeelink.net/devices/' #自己的YEELINK页面
        #return self._reply_text(fromUser, toUser, u'图片已收到已上传到此地址:'+view)
        return self.render.reply_text(fromUser,toUser,int(time.time()),u"接收图片处理的功能正在开发中")

    def _recv_voice(self, fromUser, toUser, xml):
        return self.render.reply_text(fromUser,toUser,int(time.time()),u"接收声音处理的功能正在开发中")

    def _recv_video(self, fromUser, toUser, xml):
        return self.render.reply_text(fromUser,toUser,int(time.time()),u"接收视频处理的功能正在开发中")

    def _recv_location(self, fromUser, toUser, xml):
        return self.render.reply_text(fromUser,toUser,int(time.time()),u"接收位置处理的功能正在开发中")

    def _recv_link(self, fromUser, toUser, xml):
        return self.render.reply_text(fromUser,toUser,int(time.time()),u"接收链接处理的功能正在开发中")

    def _reply_text(self, toUser, fromUser, msg):
        return self.render.reply_text(toUser, fromUser, int(time.time()),msg)

    def _reply_image(self, toUser, fromUser, media_id):
        return self.render.reply_image(toUser, fromUser, int(time.time()), media_id)

    def _reply_news(self, toUser, fromUser, title, descrip, picUrl, hqUrl):
        return self.render.reply_news(toUser, fromUser, int(time.time()), title, descrip, picUrl, hqUrl)



    def GET(self):
        #获取输入参数
	data = web.input()
        if _check_hash(data):
            return data.echostr

    def POST(self):        
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        msgType=xml.find("MsgType").text
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        
        if msgType == 'text':
            return self._recv_text(fromUser, toUser, xml)
        
        if msgType == 'event':
            return self._recv_event(fromUser, toUser, xml)
        
        if msgType == 'image':
            return self._recv_image(fromUser, toUser, xml)
       
        if msgType == 'voice':
            return self._recv_voice(fromUser, toUser, xml)
        
        if msgType == 'video':
            return self._recv_video(fromUser, toUser, xml)
        
        if msgType == 'location':
            return self._recv_location(fromUser, toUser, xml)
        
        if msgType == 'link':
            return self._recv_link(fromUser, toUser, xml)
        
        else:
            return self._reply_text(fromUser, toUser, u'Unknow msg:' + msgType)
        

application = web.application(urls, globals())

if __name__ == "__main__":
    application.run()
