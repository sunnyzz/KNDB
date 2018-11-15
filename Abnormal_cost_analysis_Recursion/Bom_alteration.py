# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 21:32:03 2018

@author: 赵忠祥
"""

class BomStrucAlteration(object):
	def __init__(self,conn):
		self.conn = conn
	
	def subnodecat(self,code,v):
		cursor = self.conn.cursor()
		sql = 'SELECT idnrk FROM bom_relevancy WHERE matnr = "%s" AND version_number = "%s"'%(code,v)
		cursor.execute(sql)
		subnode = set([each[0] for each in cursor.fetchall()])	   
		return subnode
	
	def check(self,code,v1,v2):
		subnode_1 = self.subnodecat(code,v1)
		subnode_2 = self.subnodecat(code,v2)
		inter = subnode_1.intersection(subnode_2)	 #两个序列的交集
		#union = subnode_1.union(subnode_2)			  #两个序列的并集
		difference2 = subnode_1.difference(subnode_2)#1存在2无序列
		difference1 = subnode_2.difference(subnode_1)#2存在1无序列
		
		if len(difference2) != 0:
			print('物料%s在%s>>>%s阶段子物料删减项:'%(code,v1,v2),difference2)
			
				 
		if len(difference1) != 0:
			print('物料%s在%s>>>%s阶段子物料增加项:'%(code,v1,v2),difference1)	 
				
		return difference1,inter,difference2

	def processescat(self,code,v):
		cursor = self.conn.cursor()
		sql = 'SELECT process_name FROM product_process_maintenance WHERE main_part_number = "%s" AND version_number = "%s"'%(code,v)
		cursor.execute(sql)
		processes = set([each[0] for each in cursor.fetchall()])	 
		return processes
	
	def process_bom_check(self,code,v1,v2):
		processes_1 = self.processescat(code,v1)
		processes_2 = self.processescat(code,v2)
		inter = processes_1.intersection(processes_2)	 #两个序列的交集
		#union = processes_2.union(processes_2)			  #两个序列的并集
		difference2 = processes_1.difference(processes_2)#1存在2无序列
		difference1 = processes_2.difference(processes_1)#2存在1无序列
		
		if len(difference2) != 0:
			print('物料%s在%s>>>%s阶段工序删减项:'%(code,v1,v2),difference2)
				 
		if len(difference1) != 0:
			print('物料%s在%s>>>%s阶段工序增加项:'%(code,v1,v2),difference1)	
				
		return difference1,inter,difference2
	
	
