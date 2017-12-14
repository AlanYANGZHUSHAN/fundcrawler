# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:59:41 2017

@author: GS949KS
"""

from selenium import webdriver
from datetime import datetime
import pickle
import math
import pandas as pd
import re
import urllib
import os
import sys
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='ctfund.log',
                    filemode='w')
if sys.path[0]:
    os.chdir(sys.path[0])
def get_fund_list(driver,path_str,k):
    fund_list = []
    while True:
        k +=1
        try:       
            temp = driver.find_element_by_xpath(path_str%(k))
            fund_list.append([temp.text,temp.get_attribute('href').replace('overview','jjgg')])
        except:            
            break
    print('get_fund_list is end')
    logging.info('get_fund_list is end')
    return fund_list

def get_title_list_page(driver,path_str,start_date,end_date,jud,item,n,page):
    title_date = []
    fail_title = []
    for k in range(1,n+1):
        try:
            temp_date = driver.find_element_by_xpath(path_str%k).text
            if start_date <= datetime.strptime(temp_date, "%Y-%m-%d") and end_date >= datetime.strptime(temp_date, "%Y-%m-%d"):
                temp_title = driver.find_element_by_xpath(path_str.replace('span','a')%k)
                title_date.append([temp_title.get_attribute('title'),temp_title.get_attribute('href'),temp_date,item[0],item[1]])
            if start_date > datetime.strptime(temp_date, "%Y-%m-%d"):
                jud = 0
                break
        except:
            fail_title.append([item[0],item[1],page,k])
            continue
    return title_date,jud,fail_title

def get_title_list(driver,path_str,start_date,end_date,item):
    n = 10
    total_title_num = int(driver.find_element_by_xpath(path_str[0]).text.replace(',',''))
    total_page = math.ceil(total_title_num/n)
    title_date = []
    fail_title_date = []
    jud = 1
    for i in range(total_page):
        if i < total_page-1:
            n = 10
        else:
            n = total_title_num - total_page*10
        temp_success,jud,temp_fail = get_title_list_page(driver,path_str[1],start_date,end_date,jud,item,n,i+1)
        title_date.extend(temp_success)
        fail_title_date.extend(temp_fail)
        if jud:
            driver.find_element_by_xpath(path_str[2]).click()
        else:
            break
    if jud:
        print('get_title_list %s end'%item[0])
        logging.info('get_title_list %s end'%item[0])
    else:
        print('get_title_list %s early end'%item[0])
        logging.info('get_title_list %s early end'%item[0])
    return title_date,fail_title_date

def del_same_title(title):
    df = pd.DataFrame(title,columns = ['title','title url','date','fund name','fund url'])
    group_df = df.groupby(['title url'])
    index = []
    for name,group in group_df:
        index.append(group.index[0])
    df = df.iloc[index,:]
    return df         

def save_to_csv(df):
    df['selection'] = 'Y'
    df['tag name'] = ''
    df['file name'] = ''
    df.to_excel('ctfund.xls',encoding = 'utf_8_sig')
    
def get_fund_name_list(driver):
    path_str = "/html/body/div[3]/div[2]/div[1]/ul/li[%s]/a"
    temp =driver.find_element_by_xpath(path_str%(1))
    fund_list = []
    temp_title = temp.text
    temp_href = temp.get_attribute('href').replace('overview','jjgg')
    fund_list.append([temp_title,temp_href])
    k = 9
    fund_list.extend(get_fund_list(driver,path_str,k))
    fund_list = wash_fund_name_list(fund_list)    
    output = open('ctfund.pkl', 'wb')
    pickle.dump(fund_list,output)
    output.close()


def wash_fund_name_list(fund_list):
    r = re.compile(r'^[a-zA-Z]')
    for index in range(len(fund_list)):
        temp_title = fund_list[index][0]
        if r.match(temp_title[-1]):
            fund_list[index][0] = temp_title[:-1]
    return fund_list
    
def get_fund_title_all(driver,start_date,end_date):
    driver.get("http://www.ctfund.com/funds/501046/overview/index.html")
    #get_fund_name_list(driver)    
    fund_list = pickle.load(open('ctfund.pkl', 'rb'))
    path_str = ['/html/body/div[3]/div[2]/div[2]/div/div/div/table/tbody/tr/td[1]/strong[3]',\
                '/html/body/div[3]/div[2]/div[2]/div/div/div/ul/li[%s]/span',\
                '/html/body/div[3]/div[2]/div[2]/div/div/div/table/tbody/tr/td[4]/a']
    title = []
    fail_title = []
    for item in fund_list:
        driver.get(item[1])
        temp_success,temp_fail=get_title_list(driver,path_str,start_date,end_date,item)
        title.extend(temp_success)
        fail_title.extend(temp_fail)
    df = del_same_title(title)
    href = 'http://www.ctfund.com/information/disclosure/index.html'
    driver.get(href)
    path_str = ['/html/body/div[3]/div[2]/div[2]/div/table/tbody/tr/td[1]/strong[3]',\
                '/html/body/div[3]/div[2]/div[2]/div/ul/li[%s]/span',\
                '/html/body/div[3]/div[2]/div[2]/div/table/tbody/tr/td[4]/a']
    item = ['基金公告',href]
    temp_success,temp_fail = get_title_list(driver,path_str,start_date,end_date,item)
    title = temp_success
    fail_title.extend(temp_fail)
    print('-------共失败'+str(len(fail_title))+'条记录----------------')
    logging.info('-------共失败'+str(len(fail_title))+'条记录----------------')
    title_new = []
    for item in title:
        if len(df[df['title url'] == item[0]]) == 0:
            title_new.append(item)
    df = df.append(del_same_title(title_new),ignore_index = True)
    save_to_csv(df)
    df = pd.DataFrame(fail_title,columns = ['fund name','fund url','page','number'])
    df.to_excel('ctfund_fail.xls',encoding = 'utf_8_sig')

def get_file_by_title(driver,filename):
    df = pd.read_excel(filename,index_col = 0)
    selected_df = list(df[df['selection']=='Y'].index)
    fail_title = []
    for selection in selected_df:
        temp_file_name= ''
        try:
            item = {'pdf':[],'doc':[]}
            temp_path_str = '/html/body/div[3]/div/div[2]/ul/li[1]/a'
            item = load_file(driver,df['title url'][selection],temp_path_str,item)
            temp_path_str = '/html/body/div[3]/div/div[2]/ul/li[2]/a'
            item = load_file(driver,df['title url'][selection],temp_path_str,item)
            if item['pdf']:
                urllib.request.urlretrieve(item['pdf'][0],item['pdf'][1])
                temp_file_name = item['pdf'][1]
            elif item['doc']:
                urllib.request.urlretrieve(item['doc'][0],item['doc'][1])
                temp_file_name = item['doc'][1]
            else:
                urllib.request.urlretrieve(df['title url'][selection],df['title'][selection]+'.html')
                temp_file_name = df['title'][selection]+'.html'
            df.loc[selection,'file name'] = temp_file_name
        except:
            fail_title.append(selection)
    print('----------------共有'+str(len(fail_title))+'条记录下载失败-------------------')
    df.to_excel('ctfund.xls',encoding ='utf_8_sig')
    logging.info('----------------共有'+str(len(fail_title))+'条记录下载失败-------------------')
    df = df.loc[fail_title]
    df.to_excel('ctfunddownload_fail.xls',encoding ='utf_8_sig')

def load_file(driver,href,path_str,item):
    driver.get(href)
    file_name = ''
    try:
        temp = driver.find_element_by_xpath(path_str)
        file_name = temp.text
        if '.pdf' in file_name:
            item['pdf'] = [temp.get_attribute('href'),temp.text]
        if '.doc' in file_name:
            item['doc'] = [temp.get_attribute('href'),temp.text]
        return item
    except:
        return item

        
if __name__ =='__main__':
    #Action = input('Pease select your action -----get title list (Y) or download file (N): ')
    Action = 'Y'
    driver = webdriver.PhantomJS()
    if Action =='Y' or Action =='y':
        #start_date = input('input start date: ')
        #end_date = input('input end date: ')
        start_date ='2016-1-1'
        end_date = '2018-1-1'
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        print("start to get fund list,please wait.......")
        logging.info("start to get fund list,please wait.......")
        get_fund_title_all(driver,start_date,end_date)
    else:
        df = get_file_by_title(driver,'ctfund.xls')
    driver.quit()
    input('press any key to quit')