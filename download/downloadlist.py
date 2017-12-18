# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 16:07:41 2017

@author: NY535WP
"""
from selenium import webdriver
import urllib
import pandas as pd
#import numpy as np
import os
import time
#import random
class DownloadFile:
	def __init__(self):
		self.driver = webdriver.PhantomJS()
		self.filename = "gdfund.xls"
		self.filepath = os.path.splitext(self.filename)[0]
		if not os.path.exists(self.filepath):
			os.mkdir(self.filepath)
		self.filepath = self.filepath+"/"
		#self.mode = input("请选择下载模式1（公司,使用代理）2（家里）：")
		self.mode = 2
		if self.mode ==1:
			proxyaddress =  '10.192.2.211:80'
			proxy =urllib.request.ProxyHandler({'http': proxyaddress})  # 设置proxy
			self.opener = urllib.request.build_opener(proxy)  # 挂载opener
			urllib.request.install_opener(self.opener)  # 安装opener
		self.rename_type = None
		self.data = None
		self.note = None
		self.name_type = None
		self.path = ['/html/body/div[3]/div/div[2]/ul/li[1]/a','/html/body/div[3]/div/div[2]/ul/li[2]/a']

	def readlistform(self,skiprows=[]):
		self.data = pd.read_excel(self.filename,'gd_fund',index_col = 0,skiprows = skiprows,dtype = "category")
		self.data['final_path'] = self.data['final_path'].astype('object')

	def get_rename_type(self):
		df = pd.read_excel(self.filename,'Sheet1')
		self.note = df
		self.rename_type =  list(df[df.loc[:,'需要重命名的公告类型'] == 'Y'].loc[:,'公告类型'])
		self.name_type =  list(df['公告类型']) 
		for item in self.name_type:
			if not os.path.exists(self.filepath+str(item)):
				os.mkdir(self.filepath+str(item))  
		print("-----需要重命名的公告类型："+','.join(self.rename_type)+'-----')

	def copyxls(self):
		self.readlistform([0])
		self.get_rename_type()
		writer = pd.ExcelWriter('NEW'+self.filename)
		self.data.to_excel(writer,sheet_name = 'gd_fund',encoding ='utf_8_sig')
		self.note.to_excel(writer,sheet_name = 'Sheet1',encoding ='utf_8_sig')
		writer.save()
		self.filename = 'NEW'+self.filename

	def download_file_by_url(self):
		fail_index = []
		temp_list = list(self.data[(self.data.loc[:,'download'] == 'Y') & (pd.isnull(self.data.loc[:,'final_path']))].index)
		print("-----共有"+str(len(temp_list))+'个文件需要下载-----')
		for item in temp_list:
			print('***第'+str(item)+'个文件***')
			#time.sleep(random.randint(1,5))
			try:
				if '.pdf' in self.data.loc[item,'url']:
					filename = self.savefile(self.data.loc[item,:],'.pdf')
				else:
					filename = self.find_pdfdoc_by_xpath(self.data.loc[item,:])
				if self.data.loc[item,'type'] in self.name_type:
					self.data.loc[item,'final_path'] = self.filepath+self.data.loc[item,'type']+'/'+filename
				else:
					self.data.loc[item,'final_path'] = self.filepath+filename
				print('>>>'+self.data.loc[item,'final_path']+'>>>')
			except Exception as e:
				print(str(e))
				fail_index.append(item)
		writer = pd.ExcelWriter(self.filename)
		self.data.to_excel(writer,sheet_name = 'gd_fund',encoding ='utf_8_sig')
		self.note.to_excel(writer,sheet_name = 'Sheet1',encoding ='utf_8_sig')
		self.data.loc[fail_index,:].to_excel(writer,sheet_name = 'fail',encoding ='utf_8_sig')
		writer.save()
		print('----下载完毕，共'+str(len(fail_index))+'个文件下载失败-----')
		return fail_index
				
	def find_pdfdoc_by_xpath(self,item):
		item = item.fillna('')
		item = item.to_dict()
		temp_item = {}
		temp_item['fund_ey_seriel'] = item['fund_ey_seriel']
		temp_item['fund_full_name'] = item['fund_full_name']
		temp_item['type'] = item['type']
		temp_item['year_times'] = item['year_times']
		temp_item['title'] = item['title']
		url = item['url']
		self.driver.get(url)
		file_dict = {'pdf':{},'doc':{},'docx':{}}
		for item in self.path:
			jud,temp = self.find_pdfdoc_by_onepath(item)
			if jud:
				temp_key = list(temp.keys())[0]
				file_dict[temp_key] = temp[temp_key]

		if file_dict['pdf']:
			temp_item['url'] = file_dict['pdf']['url']
			temp_item['title'] = file_dict['pdf']['title']
			filename = self.savefile(pd.Series(temp_item),'.pdf')
			return filename

		if file_dict['doc']:
			temp_item['url'] = file_dict['doc']['url']
			temp_item['title'] = file_dict['doc']['title']
			filename = self.savefile(pd.Series(temp_item),'.doc')
			return filename

		if file_dict['docx']:
			temp_item['url'] = file_dict['docx']['url']
			temp_item['title'] = file_dict['docx']['title']
			filename = self.savefile(pd.Series(temp_item),'.docx')
			return filename
		filename = self.savefile(self,pd.Series(item),'.html')
		return filename

	def find_pdfdoc_by_onepath(self,item):
		file_dict = {}
		try:
			temp = self.driver.find_element_by_xpath(item)
			file_name = temp.text
			if '.pdf' in file_name:
				file_name = file_name.replace('.pdf','')
				file_dict['pdf'] = {'url':temp.get_attribute('href'),'title':file_name}
				return 1,file_dict

			if '.docx' in file_name:
				file_name = file_name.replace('.doc','')
				file_dict['doc'] = {'url':temp.get_attribute('href'),'title':file_name}
				return 1,file_dict

			if '.doc' in file_name:
				file_name = file_name.replace('.docx','')
				file_dict['doc'] = {'url':temp.get_attribute('href'),'title':file_name}
				return 1,file_dict

		except:
			return 0,file_dict

	def savefile(self,item,filetype):
		url = item['url']
		if item['type'] in self.rename_type:
			item = item.fillna('')
			if item['year_times']:
				filename = str(item['fund_ey_seriel'])+' '+str(item['fund_full_name'])+' '+str(item['type'])+'('+' '+str(item['year_times'])+')'
			else:
				filename = str(item['fund_ey_seriel'])+' '+str(item['fund_full_name'])+' '+str(item['type'])
		else:
			filename = item['title']
		if self.mode == 1:
			page = self.opener.open(url).read()
		else:
			page = urllib.request.urlopen(url).read()
		if item['type'] in self.name_type:
			if os.path.exists(self.filepath+item['type'] + "/"+filename+filetype):
				filename = filename+';'+str(time.time())+filetype
			else:
				filename = filename+filetype
			f = open(self.filepath + item['type'] + "/" + filename,'wb')
		else:
			if os.path.exists(self.filepath+filename+filetype):
				filename = filename+';'+str(time.time())+filetype
			else:
				filename = filename+filetype
			f = open(self.filepath + filename,'wb')
		f.write(page)
		f.close()
		return filename

if __name__ =='__main__':
	downloadfile = DownloadFile()
	downloadfile.copyxls()
	times = 1
	if os.path.exists(downloadfile.filename):
		while times <10:
			fail_index = downloadfile.download_file_by_url()
			print('-----第'+str(times)+'次下载完成-----')
			if len(fail_index) == 0:
				break
			times += 1
			
		 
