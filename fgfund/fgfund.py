# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:59:41 2017

@author: GS949KS
"""
from selenium import webdriver
import pickle
from datetime import datetime
import pandas as pd
import re
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='fgfund.log',
                    filemode='w')
filename = {
	'success': 'fgfund.xls',
	'fail': 'fgfund_fail.xls',
	'fail_download':'fgfunddownload_fail.xls'
}
filecolumns = {
	'success':['title','title url','date','fund name','fund url'],
	'fail':['fund name','fund url','page','Number']
}
PATH_STR = {
	'fund': ['//*[@id="pageNavigator"]',\
			'/html/body/div/div[1]/div[2]/div[2]/div[2]/div/a[%s]',\
			'/html/body/div/div[1]/div[2]/div[2]/div[2]/ul/li[%s]/span',\
			'/html/body/div/div[1]/div[2]/div[2]/div[2]/ul/li[%s]/a[2]',\
			'/html/body/div/div[1]/div[2]/div[2]/div[2]/ul/li[%s]/a'],
	'fund report': ['//*[@id="pageNavigator"]',\
				'/html/body/div[5]/div[2]/div/div[2]/div/div/div/div/a[%s]',\
				'/html/body/div[5]/div[2]/div/div[2]/div/div/div/ul/li[%s]/span',\
				'/html/body/div[5]/div[2]/div/div[2]/div/div/div/ul/li[%s]/a',\
				'/html/body/div[5]/div[2]/div/div[2]/div/div/div/ul/li[%s]/a[2]']
}
def sub_get_fund_url_list(driver,temp_path_str):
	fund_list = []
	k = 0
	while True:
		k += 1
		try:
			fund_list.append(driver.find_element_by_xpath(temp_path_str%k).get_attribute('href'))
		except:
			break
	return fund_list

def get_fund_url_list(driver):
	fund_list = []
	temp_path_str = '/html/body/div[4]/div[3]/table[2]/tbody[1]/tr[%s]/td[1]/h3/a'
	temp = sub_get_fund_url_list(driver,temp_path_str)
	fund_list.extend(temp)
	temp_path_str = '/html/body/div[4]/table[2]/tbody[1]/tr[%s]/td[1]/h3/a'
	temp = sub_get_fund_url_list(driver,temp_path_str)
	fund_list.extend(temp)
	print('------------首页共有'+str(len(fund_list))+'个基金-----------------')
	logging.info('------------首页共有'+str(len(fund_list))+'个基金-----------------')
	fund_list = list(set(fund_list))
	output = open('fgfund.pkl', 'wb')
	pickle.dump(fund_list,output)
	output.close()

def get_fund_name_list(driver,start_date,end_date,fund_list,PATH_STR):
	title = []
	fail_title = []
	path_str = PATH_STR['fund']
	for item_href in fund_list:
		driver.get(item_href)
		try:
			temp_fund_name = driver.find_element_by_xpath('/html/body/div[4]/div[1]/div[1]/div[1]/dl/dd/h4').text
		except:
			temp_fund_name = ''
		fund_name_href = [temp_fund_name,item_href]
		url = {}
		url['season_url'] = item_href.replace('index.html?statistics_type=$fundsMiddle$','report/season/index.html')
		url['fenhong_url'] = item_href.replace('index.html?statistics_type=$fundsMiddle$','report/fenhong/index.html')
		url['half_url'] = item_href.replace('index.html?statistics_type=$fundsMiddle$','report/half/index.html')
		url['zhaomu_url'] = item_href.replace('index.html?statistics_type=$fundsMiddle$','report/zhaomu/index.html')
		url['year_url'] = item_href.replace('index.html?statistics_type=$fundsMiddle$','report/year/index.html')
		url['other_url'] = item_href.replace('index.html?statistics_type=$fundsMiddle$','report/other/index.html')
		temp_success,temp_fail = get_title_list(driver,url['season_url'],'season',path_str,start_date,end_date,fund_name_href,3)
		title.extend(temp_success)
		fail_title.extend(temp_fail)
		temp_success,temp_fail = get_title_list(driver,url['fenhong_url'],'fenhong',path_str,start_date,end_date,fund_name_href,4)
		title.extend(temp_success)
		fail_title.extend(temp_fail)	
		temp_success,temp_fail = get_title_list(driver,url['half_url'],'half',path_str,start_date,end_date,fund_name_href,3)
		title.extend(temp_success)
		fail_title.extend(temp_fail)
		temp_success,temp_fail = get_title_list(driver,url['zhaomu_url'],'zhaomu',path_str,start_date,end_date,fund_name_href,4)
		title.extend(temp_success)
		fail_title.extend(temp_fail)
		temp_success,temp_fail = get_title_list(driver,url['year_url'],'year',path_str,start_date,end_date,fund_name_href,3)
		title.extend(temp_success)
		fail_title.extend(temp_fail)
		temp_success,temp_fail = get_title_list(driver,url['other_url'],'other',path_str,start_date,end_date,fund_name_href,4)
		title.extend(temp_success)
		fail_title.extend(temp_fail)
	return title,fail_title

def get_title_list(driver,url,kind,path_str,start_date,end_date,fund_name_href,path_str_n,k=0):
	driver.get(url)
	total_page = get_total_page(driver,path_str)
	print('------共'+str(total_page)+'页---------')
	logging.info('------共'+str(total_page)+'页---------')
	jud = 1
	title_date = []
	fail_title_date = []
	for page in range(total_page):
		if page<total_page-1:
			end_k = 1
		else:
			end_k = 0 
		if k == 1 and page == 0:
			jud,temp_success,temp_fail = get_title_list_page(driver,path_str,start_date,end_date,jud,fund_name_href,path_str_n,1,end_k,page+1)
		else:
			jud,temp_success,temp_fail = get_title_list_page(driver,path_str,start_date,end_date,jud,fund_name_href,path_str_n,0,end_k,page+1)
		title_date.extend(temp_success)
		fail_title_date.extend(temp_fail)
		print('*********第'+str(page+1)+'页完成*************')
		logging.info('*********第'+str(page+1)+'页完成*************')
		if jud:
			driver,driver_jud = better_turn_page(driver,path_str,page,total_page)
			if not driver_jud:
				for number in range(1,11):
					fail_title_date.extend([fund_name_href[0],fund_name_href[1],page+1,number])
		else:
			break
	if jud:
		print('get_title_list %s----%s end'%(fund_name_href[0],kind))
		logging.info('get_title_list %s----%s end'%(fund_name_href[0],kind))
	else:
		print('get_title_list %s----%s early end'%(fund_name_href[0],kind))
		logging.info('get_title_list %s----%s early end'%(fund_name_href[0],kind))
	return title_date,fail_title_date
def get_total_page(driver,path_str):
	try:
		total_page = driver.find_element_by_xpath(path_str[0]).text
		temp = re.findall(r'/(.+?)页）| /(.+?)页\)',total_page)[0]
		if temp[0]:
			total_page = int(temp[0].replace(',',''))
		elif temp[1]:
			total_page = int(temp[1].replace(',',''))
		else:
			total_page = 1
	except:
		total_page = 1
	return total_page
def better_turn_page(driver,path_str,page,total_page):
	if page == total_page -1:
		return driver,1
	try:
		if total_page == 2 and page == 0:
			page_temp = driver.find_element_by_xpath(path_str[1]%3).text
			if page_temp == '下一页':
				driver.find_element_by_xpath(path_str[1]%3).click()
				return driver,1
			else:
				return turn_page(driver,path_str)
		elif total_page == 3 and page == 0:
			page_temp = driver.find_element_by_xpath(path_str[1]%4).text
			if page_temp == '下一页':
				driver.find_element_by_xpath(path_str[1]%4).click()
				return driver,1
			else:
				return turn_page(driver,path_str)

		elif (total_page == 3 and page == 1) or (total_page >= 4 and page == 0):
			page_temp = driver.find_element_by_xpath(path_str[1]%5).text
			if page_temp == '下一页':
				driver.find_element_by_xpath(path_str[1]%5).click()
				return driver,1
			else:
				return turn_page(driver,path_str)

		elif (total_page == 4 and page == 1) or (total_page == 4 and page == 2) :
			page_temp = driver.find_element_by_xpath(path_str[1]%6).text
			if page_temp == '下一页':
				driver.find_element_by_xpath(path_str[1]%6).click()
				return driver,1
			else:
				return turn_page(driver,path_str)

		elif (total_page >= 5 and page == 1) or (total_page == 5 and page == 2) or (total_page >= 5 and page == total_page - 2):
			page_temp = driver.find_element_by_xpath(path_str[1]%7).text
			if page_temp == '下一页':
				driver.find_element_by_xpath(path_str[1]%7).click()
				return driver,1
			else:
				return turn_page(driver,path_str)

		elif (total_page >= 6 and page == 2) or (total_page >= 6 and page == total_page -3):
			page_temp = driver.find_element_by_xpath(path_str[1]%8).text
			if page_temp == '下一页':
				driver.find_element_by_xpath(path_str[1]%8).click()
				return driver,1
			else:
				return turn_page(driver,path_str)

		elif (total_page >= 7 and page > 2) or (total_page >= 7 and page < total_page -3):
			return turn_page(driver,path_str)
	except:
		return  turn_page(driver,path_str)
	
def turn_page(driver,path_str,page_index = 9):
	if page_index <= 0:
		return driver,0
	try:
		page_temp = driver.find_element_by_xpath(path_str[1]%page_index).text
		if page_temp == '下一页':
			driver.find_element_by_xpath(path_str[1]%page_index).click()
			return driver,1
		else:
			return turn_page(driver,path_str,page_index-1)
	except:
		return turn_page(driver,path_str,page_index-1)


def get_title_list_page(driver,path_str,start_date,end_date,jud,fund_name_href,path_str_n,start_k,end_k,page):
	jud = 1
	title_date = []
	fail_title_date = []
	for k in range(start_k+1,11):
		try:
			temp_date = driver.find_element_by_xpath(path_str[2]%k).text
			if start_date <= datetime.strptime(temp_date, "%Y-%m-%d") and end_date >= datetime.strptime(temp_date, "%Y-%m-%d"):
				try:
					temp_title = driver.find_element_by_xpath(path_str[path_str_n]%k)
				except:
					if path_str_n ==3:
						temp_title = driver.find_element_by_xpath(path_str[path_str_n+1]%k)
					else:
						temp_title = driver.find_element_by_xpath(path_str[path_str_n-1]%k)
				print('TITLE:'+temp_title.get_attribute('title')+'*****DATE:'+temp_date)
				logging.info('TITLE:'+temp_title.get_attribute('title')+'*****DATE:'+temp_date)
				title_date.append([temp_title.get_attribute('title'),temp_title.get_attribute('href'),temp_date,fund_name_href[0],fund_name_href[1]])
			if start_date > datetime.strptime(temp_date, "%Y-%m-%d"):
				jud = 0
				break
		except:
			if end_k:
				fail_title_date.append([fund_name_href[0],fund_name_href[1],page,k])
			continue
	return jud,title_date,fail_title_date

def del_same_title(title,filecolumns):
	df = pd.DataFrame(title,columns = filecolumns['success'])
	group_df = df.groupby(['title url'])
	index = []
	for name,group in group_df:
		index.append(group.index[0])
	df = df.iloc[index,:]
	return df

def save_to_csv(df,filename):
	df['selection'] = 'Y'
	df['tag name'] = ''
	df['file name'] = ''
	df.to_excel(filename['success'],encoding = 'utf_8_sig')

def get_fund_title_all(driver,start_date,end_date,fund_list,filename,filecolumns,PATH_STR):
	title,fail_title = get_fund_name_list(driver,start_date,end_date,fund_list,PATH_STR)
	df = del_same_title(title,filecolumns)
	href = 'http://www.fullgoal.com.cn/news/reports/report/index.html'
	driver.get(href)
	path_str = PATH_STR['fund report']
	fund_name_href = ['基金公告',href]
	title,temp_fail = get_title_list(driver,href,'',path_str,start_date,end_date,fund_name_href,3,1)
	fail_title.extend(temp_fail)
	print('-------清单共失败'+str(len(fail_title))+'条记录----------------')
	logging.info('-------清单共失败'+str(len(fail_title))+'条记录----------------')
	title_new = []
	for item in title:
		if len(df[df['title url'] == item[0]]) == 0:
			title_new.append(item)
	df = df.append(del_same_title(title_new,filecolumns),ignore_index = True)
	save_to_csv(df,filename)
	df = pd.DataFrame(fail_title,columns = filecolumns['fail'])
	df.to_excel(filename['fail'],encoding = 'utf_8_sig')


def recover_fail_title(driver,start_date,end_date,k,filename,filecolumns,PATH_STR):
	df = pd.read_excel(filename['fail'])
	df_index = list(df.index)
	title_date = []
	fail_title_date = []
	for index in df_index:
		try:
			driver.get(df.loc[index,'fund url'])
			if df.loc[index,'fund name'] == '基金公告':
				path_str = PATH_STR['fund report']
			else:
				path_str = PATH_STR['fund']
			total_page = get_total_page(driver,path_str)
			print('------共'+str(total_page)+'页---------')
			logging.info('------共'+str(total_page)+'页---------')
			jud = 1
			for page in range(df.loc[index,'page']-1):
				driver,jud = better_turn_page(driver,path_str,page,total_page)
				if jud == 0:
					break
			if jud:
				temp_date = driver.find_element_by_xpath(path_str[2]%df.loc[index,'Number']).text
				if start_date <= datetime.strptime(temp_date, "%Y-%m-%d") and end_date >= datetime.strptime(temp_date, "%Y-%m-%d"):
					try:
						temp_title = driver.find_element_by_xpath(path_str[3]%df.loc[index,'Number'])
					except:
						temp_title = driver.find_element_by_xpath(path_str[4]%df.loc[index,'Number'])
					print(temp_title.get_attribute('title')+'*****DATE:'+temp_date)
					logging.info('TITLE:'+temp_title.get_attribute('title')+'*****DATE:'+temp_date)
					title_date.append([temp_title.get_attribute('title'),temp_title.get_attribute('href'),temp_date,df.loc[index,'fund name'],df.loc[index,'fund url']])
			else:
				fail_title_date.append([df.loc[index,'fund name'],df.loc[index,'fund url'],df.loc[index,'page'],df.loc[index,'Number']])
		except:
			fail_title_date.append([df.loc[index,'fund name'],df.loc[index,'fund url'],df.loc[index,'page'],df.loc[index,'Number']])
	print('-------第'+str(k)+'次处理失败清单,'+'-----------共失败'+str(len(fail_title_date))+'条记录----------------')
	logging.info('-------第'+str(k)+'次处理失败清单,'+'-----------共失败'+str(len(fail_title_date))+'条记录----------------')
	jud = 0
	if len(title_date) == 0 or zhuang
	len(title_date) == len(df_index):
		jud = 1
	df = pd.DataFrame(fail_title_date,columns = filecolumns['fail'])
	df.to_excel(filename['fail'],encoding = 'utf_8_sig')
	return title_date,jud

def recover_fail_title_multi(driver,start_date,end_date,filename,filecolumns,PATH_STR):
	title = []
	times = 0
	while True:
		times += 1
		temp_title,jud = recover_fail_title(driver,start_date,end_date,times,filename,filecolumns,PATH_STR)
		title.extend(temp_title)
		if jud:
			break
	df = pd.read_excel(filename['success'])
	df.drop(['selection','tag name','file name'],axis=1,inplace=True)
	df = df.append(del_same_title(title,filecolumns),ignore_index = True)
	save_to_csv(df,filename)

def get_file_by_title(driver,filename):
	df = pd.read_excel(filename['fail'],index_col = 0)
	selected_df = list(df[df['selection']=='Y'].index)
	fail_title = []
	for selection in selected_df:
		temp_file_name = ''
		try:
			if  '.pdf' in df['title url'][selection]:
				temp_file_name = df['title'][selection]+'.pdf'
				urllib.request.urlretrieve(df['title url'][selection],temp_file_name)
			elif '.html' in df['title url'][selection]:
				temp_path_str = ['/html/body/div[4]/div/div[3]/a','/html/body/div[4]/div/div[3]/div/p[1]/a']
				if load_file(driver,df['title url'][selection],temp_path_str,df['title'][selection]):
					temp_file_name = df['title'][selection]+'.html'
					urllib.request.urlretrieve(df['title url'][selection],temp_file_name)
				else:
					temp_file_name = df['title'][selection]+'.pdf'
			else:
				temp_file_name = df['title'][selection]+'.html'
				urllib.request.urlretrieve(df['title url'][selection],temp_file_name)
			df.loc[selection,'file name'] = temp_file_name
		except:
			fail_title.append(selection)
	print('----------------共有'+str(len(fail_title))+'条记录下载失败-------------------')
	df.to_excel(filename['success'],encoding ='utf_8_sig')
	logging.info('----------------共有'+str(len(fail_title))+'条记录下载失败-------------------')
	df = df.loc[fail_title]
	df.to_excel(filename['fail_download'],encoding ='utf_8_sig')

def load_file(driver,href,path_str,filename):
	try:
		driver.get(href)
		temp = driver.find_element_by_xpath(path_str)
		temp_url = temp.get_attribute('href')
		urllib.request.urlretrieve(temp_url,filename+'.pdf')
		return 0
	except:
		return 1

if __name__ =='__main__':
	#Action = input('Pease select your action -----get title list (Y) or download file (N): ')
	Action = 'Y'
	driver = webdriver.PhantomJS()
	driver.implicitly_wait(10)
	if Action =='Y' or Action =='y':
		driver.get('http://www.fullgoal.com.cn/funds/index.html')
		get_fund_url_list(driver)
		fund_list = pickle.load(open('fgfund.pkl', 'rb'))
		print('-----------筛选出'+str(len(fund_list))+'个基金-------------')
		logging.info('-----------筛选出'+str(len(fund_list))+'个基金-------------')
		#start_date = input('input start date: ')
		#end_date = input('input end date: ')
		start_date ='2016-1-1'
		end_date = '2018-11-21'
		start_date = datetime.strptime(start_date, "%Y-%m-%d")
		end_date = datetime.strptime(end_date, "%Y-%m-%d")
		get_fund_title_all(driver,start_date,end_date,fund_list,filename,filecolumns,PATH_STR)
		recover_fail_title_multi(driver,start_date,end_date,filename,filecolumns,PATH_STR)
	else:
		df = get_file_by_title(driver,filename)
	driver.quit()
	#input('press any key to quit')