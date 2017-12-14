from selenium import webdriver
import urllib
proxy =urllib.request.ProxyHandler({'http': '10.192.2.211:80'})  # 设置proxy
opener =urllib.request.build_opener(proxy)  # 挂载opener
urllib.request.install_opener(opener)  # 安装opener
#page = opener.open('http://www.galaxyasset.com/upload2010/2017/10/26/094210053_128_50394743-8964-360e-a860-dea786754437.pdf').read()
page = opener.open('http://www.galaxyasset.com/upload2010/2017/08/29/102356570_128_5a584ed1-7f0b-3dbc-aab8-11c24d28ce6a.pdf').read()
f = open('filename2.pdf','wb')
f.write(page)
f.close()

#floder
#(01fundname shuomingshu (2017nian xxci))
#(2016)