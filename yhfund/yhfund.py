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
from bs4 import BeautifulSoup
YHFUND_HREF	= 'http://www.galaxyasset.com/newproduct/jjcs.shtml'
TITLE_KIND = {
	'712':'招募说明书',
	'713':'发行公告',
	'714':'基金合同',
	'715':'上市公告',
	'716':'季度报告',
	'717':'中期报告',
	'718':'年度报告',
	'719':'分红公告',
	'720':'其他公告'
}
TITLE_PATH = '//UL[@class="ggao_list"]'
IS_TITLE_REPORT_PATH = '/html/body'
TITLE_REPORT_PATH = '//div[@class = "serv_deal"]/ul[@class = "serv_sound"]/li[%s]/a'
TITLE_HREF = 'http://www.galaxyasset.com/frontweb/runprogram/selectArticleByColumnid.do?fundcode=%s&columnid=%s&gotoPage=%s&pageSize=10'
TITLE_REPORT_HREF = 'http://www.galaxyasset.com/frontweb/home/search/articleListpage.do?columnId=622&gotoPage=%s&pageSize=10'
FUND_PKL = 'yhfund.pkl'
FUND_COLUMNS = ['fund name','fund url']
TITLE_COLUMNS = ['title','title url','date','fund name','fund url']
TITLE_SUC_EXCEL = 'yhfund.xls'
class Yhfund:
	def __init__(self):
		start_date = '2016-1-1'
		end_date = '2018-1-1'
		self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
		self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
		#self.start_date = datetime.strptime(input('input start date: '), "%Y-%m-%d")
		#self.end_date = datetime.strptime(input('input end date: '), "%Y-%m-%d")
		self.driver = webdriver.PhantomJS()
		self.driver.implicitly_wait(10)
		self.title = []
		self.fail_title = []
		self.df = []

	def get_fund_name(self):
		self.driver.get(YHFUND_HREF)
		bs = BeautifulSoup(self.driver.page_source, "lxml")
		temp = bs.find_all("span",attrs={'class':'shop_name'})
		r = re.compile(r'<a href="(.*)">')
		fund_name = []
		for item in temp:
			fund_name.append([item.find('a').text,'http://www.galaxyasset.com'+item.find('a').attrs['href']])
		df = pd.DataFrame(fund_name,columns = FUND_COLUMNS)
		df = df.drop_duplicates(FUND_COLUMNS)
		output = open(FUND_PKL, 'wb')
		pickle.dump(df,output)

	def get_title(self,fund_url_name):
		href = fund_url_name['fund url']
		fund_name = fund_url_name['fund name']
		temp = re.findall(r"fund/(.+?)/fundinfor",href)
		if temp:
			fundcode = temp[0]
		else:
			print(href)
			return None
		for (columnid,value) in TITLE_KIND.items():
			print('-------'+fund_name+':'+value+'-------')
			pagenum = 1
			jud = 1
			while jud:
				print('*****第'+str(pagenum)+'页*****')
				href = TITLE_HREF%(fundcode,columnid,pagenum)
				self.driver.get(href)
				jud = self.get_title_one_page(href,fund_name)
				pagenum += 1

	def get_title_one_page(self,href,fund_name):
		temp = self.driver.find_element_by_xpath(TITLE_PATH)
		if '暂无数据' in temp.text:
			return 0
		temp = temp.find_elements_by_tag_name('a')
		for item in temp:
			print(item.text.split('\n'))
			temp_title,temp_date = item.text.split('\n')
			if self.start_date <= datetime.strptime(temp_date, "%Y/%m/%d") and self.end_date >= datetime.strptime(temp_date, "%Y/%m/%d"):
				title_date_item = [temp_title,item.get_attribute('href'),temp_date,fund_name,href]
				self.title.append(title_date_item)
			if self.start_date > datetime.strptime(temp_date, "%Y/%m/%d"):
				return 0
		bs = BeautifulSoup(self.driver.page_source, "lxml")
		if bs.find("div",attrs = {"class" : "next_page"}):
			return 1
		else:
			return 0
	def get_report_title(self,fund_url_name):
		href = fund_url_name['fund url']
		fund_name = fund_url_name['fund name']
		pagenum = 1
		jud = 1
		while jud:
			print('*****第'+str(pagenum)+'页*****')
			href = TITLE_REPORT_HREF%(pagenum)
			self.driver.get(href)
			jud = self.get_report_title_one_page(href,fund_name)
			pagenum += 1

	def get_report_title_one_page(self,href,fund_name):
		temp_page = self.driver.find_element_by_xpath(IS_TITLE_REPORT_PATH)
		if '暂无数据' in temp_page.text or temp_page.text is '':
			return 0
		for k in range(1,11):
			try:
				temp = temp_page.find_element_by_xpath(TITLE_REPORT_PATH%k)
				temp_href = temp.get_attribute('href')
				temp_date = temp.find_element_by_xpath('//span[@class = "soo_time fr"]').text
				if self.start_date <= datetime.strptime(temp_date, "%Y/%m/%d") and self.end_date >= datetime.strptime(temp_date, "%Y/%m/%d"):
					temp_title = temp.find_element_by_xpath('//span[@class = "serv_span"]').text
					title_date_item = [temp_title,temp_href,temp_date,fund_name,href]
					print([temp_title,temp_date])
					self.title.append(title_date_item)
				if self.start_date > datetime.strptime(temp_date, "%Y/%m/%d"):
					return 0
			except:
				return 0
		bs = BeautifulSoup(self.driver.page_source, "lxml")
		if bs.find("div",attrs = {"class" : "next_page"}):
			return 1
		else:
			return 0

	def get_title_all(self,fund_df):
		index = list(fund_df.index)
		for item in index:
			self.get_title(fund_df.loc[item,:])
		fund_url_name = {'fund name':'基金公告','fund url':'http://www.galaxyasset.com/server/xxpl.shtml'}
		self.get_report_title(fund_url_name)
		df = self.del_same_title()
		self.save_to_csv(df)



	def del_same_title(self):
		df = pd.DataFrame(self.title,columns = TITLE_COLUMNS)
		group_df = df.groupby(['title url'])
		index = []
		for name,group in group_df:
			index.append(group.index[0])
		df = df.iloc[index,:]
		return df

	def save_to_csv(self,df):
		df['selection'] = 'Y'
		df['tag name'] = ''
		df['file name'] = ''
		df.to_excel(TITLE_SUC_EXCEL,encoding = 'utf_8_sig')

if __name__ =='__main__':
	#Action = input('Pease select your action -----get title list (Y) or download file (N): ')
	Action = 'Y'
	if Action =='Y' or Action =='y':
		yhfund = Yhfund()
		#yhfund.get_fund_name()
		fund_df = pickle.load(open(FUND_PKL, 'rb'))
		print('------共有'+str(len(fund_df))+'个基金---------')
		yhfund.get_title_all(fund_df)