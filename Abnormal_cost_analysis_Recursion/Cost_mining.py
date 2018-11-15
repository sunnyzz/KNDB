# -*- coding: utf-8 -*-

#各字段代表的成本内涵
cost_stage_dic={'material_cost_stage':'本阶物料成本',
						 'labor_hour':'本阶人工成本',
					   'machine_hour':'本阶设备成本',
					   'burning_hour':'本阶燃动成本',
					 'auxiliary_hour':'本阶辅助成本',
						 'other_hour':'本阶其他成本'}


import time

class CostMining(object):
	def __init__(self,conn,weight):
		self.conn = conn
		self.weight = weight

#==============================================================================
		
	#总成本获取	 
	def cost_cat(self,code,v,use_number_,lostrat_):
		cursor = self.conn.cursor()
		sql = ('select'
			   ' a.material_cost_stage'
			   '+b.labor_cost_stage+b.equip_cost_stage+b.burning_cost_stage+b.auxiliary_cost_stage+b.other_cost_stage'
			   '+c.material_cost_accumulated'
			   '+d.labor_cost_accumulated+d.equip_cost_accumulated+d.burning_cost_accumulated+d.auxiliary_cost_accumulated+d.other_cost_accumulated'
			   ' as total_cost'
			   ' from cost_material_stage a,cost_stage b,cost_material_accumulated c,cost_accumulated d'
			   ' where a.material_number="{0}" and b.material_number="{0}" and c.material_number="{0}" and d.material_number="{0}"'
			   ' and a.version_number="{1}" and b.version_number="{1}" and c.version_number="{1}" and d.version_number="{1}"'.format(code,v)
			   )		
		try:			
			cursor.execute(sql)
			coca = float(cursor.fetchone()[0])*use_number_*(1+lostrat_)
		finally:
			cursor.close()
		return coca
	
	
	#循环总成本对比结果
	def sub_total_cost_check(self,code,v1,v2,use_number_1,use_number_2,lostrat_1,lostrat_2,diff_value):
		cost1 = self.cost_cat(code,v1,use_number_1,lostrat_1)
		cost2 = self.cost_cat(code,v2,use_number_2,lostrat_2)
		diff_cost = cost2-cost1
			 
		if diff_cost:
			print("物料%s在%s>>>%s阶段总成本上升%.3f"%(code,v1,v2,diff_cost))
			self.query_records_insert("2100",code,v1,v2,"1","1",cost1,cost2,diff_cost,diff_cost,"(*用量)物料总成本变化",time.strftime("%F")) 
		
		if diff_cost < diff_value * self.weight:
			
			return 0
		else:
			print("物料%s在%s>>>%s阶段总成本变化差异值超出权重，正在挖掘具体原因"%(code,v1,v2))
			return 1
		
	#初始总成本对比结果
	def total_cost_check(self,code,v1,v2,use_number_1=1,use_number_2=1,lostrat_1=0,lostrat_2=0):
		cost1 = self.cost_cat(code,v1,use_number_1,lostrat_1)
		cost2 = self.cost_cat(code,v2,use_number_2,lostrat_2)
		diff_cost = abs(cost1-cost2)
		
		notif_red = "单位物料%s总成本降低%.3f" 
		notif_same = "单位物料%s总成本未发生改变" 
		notif_incre = "单位物料%s总成本上升%.3f," 
		if cost1 > cost2:			
			print(notif_red%(code,diff_cost))
			return 0
		
		elif cost1 == cost2:
			print(notif_same%code)			   
			return 0
		else:
			print(notif_incre%(code,diff_cost),end='')
			if (cost2-cost1) < (cost1*0.03):
				print("但差异值未超出阈值")
				return 0
			else:
				print("差异值超出阈值，正在挖掘具体原因")
				self.query_records_insert("2100",code,v1,v2,"1","1",cost1,cost2,diff_cost,diff_cost,"查询物料总成本变化",time.strftime("%F"))
				return 1
 
	#本阶材料成本差异对比
	def cost_stage_material_diff(self, code, version_1, version_2, select_object, select_table):
		cursor = self.conn.cursor()
		sql_1 = 'select {0} from {1} where material_number = "{2}" and \
				 version_number = "{3}"'.format(select_object, select_table, code, version_1)
		sql_2 = 'select {0} from {1} where material_number = "{2}" and \
				 version_number = "{3}"'.format(select_object, select_table, code, version_2)
				 
		try:
			cursor.execute(sql_1)
			value_1 = float(cursor.fetchone()[0])
			cursor.execute(sql_2)
			value_2 = float(cursor.fetchone()[0])
			diff_value = value_2 - value_1
			
			if diff_value:
				print("单位物料%s在%s>>>%s阶段%s变化:%.3f"%(code,version_1,version_2,cost_stage_dic[select_object],diff_value))
				self.query_records_insert("2100",code,version_1,version_2,"1","1",value_1,value_2,diff_value,diff_value,"本阶材料成本变化",time.strftime("%F"))
			
		except :
			print("执行cursor.execute和fetchone语句出错！")
			
		finally:
			cursor.close()
			
	 
	#本阶总成本（不含本材）
	def cost_stage_total(self, code, v):
		cursor = self.conn.cursor()
		sql = 'select (labor_cost_stage + equip_cost_stage + burning_cost_stage + auxiliary_cost_stage + other_cost_stage) from cost_stage where material_number = "{0}" and \
			   version_number = "{1}"'.format(code, v)
		try:
			cursor.execute(sql)
			value = float(cursor.fetchone()[0])
			return value
		except :
			print("执行cursor.execute和fetchone语句出错！")
			
		finally:
			cursor.close()
		
		
		
	#本阶总成本（不含本材）差异对比
	def cost_stage_total_diff(self, code, version_1, version_2,c_diff):
		value_1 = self.cost_stage_total(code, version_1)
		value_2 = self.cost_stage_total(code, version_2)
		diff_value = value_2 - value_1
		
		if diff_value:
			print("单位物料%s在%s>>>%s阶段本阶总成本变化:%.3f"%(code,version_1,version_2,diff_value))
			self.query_records_insert("2100",code,version_1,version_2,"1","1",value_1,value_2,diff_value,diff_value,"本阶总成本（不含本材）变化",time.strftime("%F"))
			
		if diff_value < c_diff * self.weight:
			return 0,0
		else:
			print("单位物料%s在%s>>>%s阶段本阶总成本变化差异值超出权重,正在挖掘具体原因"%(code,version_1,version_2))
			return 1,diff_value
			
	
	#本阶各成本差异对比汇总
	def cost_stage_component_check(self,code, version_1, version_2, cost_diff):
		self.cost_stage_material_diff(code, version_1, version_2, select_object = "material_cost_stage", select_table = "cost_material_stage")
		cost,diff_value = self.cost_stage_total_diff(code, version_1, version_2,cost_diff)
		return cost,diff_value
			
	
	#累计成本获取
	def cost_accumulated_component(self, code, version_number):
		cursor = self.conn.cursor()
		sql = 'select \
			   a.material_cost_accumulated + b.labor_cost_accumulated + b.equip_cost_accumulated + b.burning_cost_accumulated + b.auxiliary_cost_accumulated + b.other_cost_accumulated \
			   as total_accumulated_cost \
			   from cost_material_accumulated a, cost_accumulated b \
			   where a.material_number = "{0}" and b.material_number = "{0}" and a.version_number = "{1}" and b.version_number = "{1}"'.format(code, version_number)
			   
		try:
			cursor.execute(sql)
			value = float(cursor.fetchone()[0])
			return value
		
		except :
			print("执行cursor.execute和fetchone语句出错！")
			
		finally:
			cursor.close()



	#累计成本差异对比	
	def cost_accumulated_component_diff(self, code, version_1, version_2,c_diff):
		value_1 = self.cost_accumulated_component(code, version_1)
		value_2 = self.cost_accumulated_component(code, version_2)
		
		diff_value = value_2 - value_1
		
		if diff_value:
			print("单位物料%s在%s>>>%s阶段的累计总成本变化:%.3f"%(code,version_1,version_2, diff_value))
			self.query_records_insert("2100",code,version_1,version_2,"1","1",value_1,value_2,diff_value,diff_value,"单位物料累计总成本变化",time.strftime("%F"))
		
		if diff_value < c_diff * self.weight:
			
			return 0,0
		else:
			print("单位物料%s在%s>>>%s阶段的累计总成本变化差异值超出权重，正在挖掘具体原因"%(code,version_1,version_2))
			return 1,diff_value
	
	#bom增加子件（用量，损耗率）总成本计算  
	def sub_cost_total(self, sub_code, v, matnr_code):
		cursor = self.conn.cursor()
		sql = ('select'
			   ' (a.material_cost_stage'
			   '+b.labor_cost_stage+b.equip_cost_stage+b.burning_cost_stage+b.auxiliary_cost_stage+b.other_cost_stage'
			   '+c.material_cost_accumulated'
			   '+d.labor_cost_accumulated+d.equip_cost_accumulated+d.burning_cost_accumulated+d.auxiliary_cost_accumulated+d.other_cost_accumulated)'
			   '*e.menge'
			   ' as total_cost'
			   ' from cost_material_stage a,cost_stage b,cost_material_accumulated c,cost_accumulated d,bom_relevancy e'
			   ' where a.material_number="{0}" and b.material_number="{0}" and c.material_number="{0}" and d.material_number="{0}"'
			   ' and a.version_number="{1}" and b.version_number="{1}" and c.version_number="{1}" and d.version_number="{1}" and'
			   ' e.matnr = "{2}" and e.idnrk = "{0}" and e.version_number = "{1}"'.format(sub_code, v, matnr_code)
			   )
		
		try:			
			cursor.execute(sql)
			coca = float(cursor.fetchone()[0])
		finally:
			cursor.close()
		return coca
	
	#bom增加子件的成本
	def sub_cost_total_diff_with_matnr(self, matnr_code, version_1, sub_code, version_2):
		sub_cost = self.sub_cost_total(sub_code, version_2, matnr_code)
				
		if sub_cost:
			print("单位物料%s在%s>>>%s阶段多出子件物料%s，造成累计总成本变化%.3f"%(matnr_code, version_1,version_2, sub_code, sub_cost))
			self.query_records_insert("2100",matnr_code,version_1,version_2,"0","1",0,sub_cost,sub_cost,sub_cost,"多出子件"+sub_code,time.strftime("%F"))
	
	#bom减少子件的成本
	def sub_bom_red_record(self, matnr_code, version_1, sub_code, version_2):
		sub_cost = self.sub_cost_total(sub_code, version_2, matnr_code)
			
		if sub_cost:
			print("单位物料%s在%s>>>%s阶段减少子件物料%s，造成累计总成本变化%.3f"%(matnr_code, version_1,version_2, sub_code, -sub_cost))
			self.query_records_insert("2100",matnr_code,version_1,version_2,"1","2",sub_cost,0,-sub_cost,-sub_cost,"减少子件"+sub_code,time.strftime("%F"))	
	
	#子件用量、损耗率获取
	def use_lost_cat(self, matnr_code, sub_code, version_number):
		cursor = self.conn.cursor()
		sql = 'select menge,ausch from bom_relevancy where matnr = "{0}" and idnrk = "{1}" and version_number = "{2}"'.format(matnr_code, sub_code, version_number)
			   
		try:
			cursor.execute(sql)
			value = cursor.fetchone()
			use = float(value[0])
			lostrat = float(value[1])
			return use,lostrat
		
		except :
			print("执行cursor.execute和fetchone语句出错！")
			
		finally:
			cursor.close()
	
	#单位总成本、用量（*损耗率)两类判断
	def check_unitcost_menge_ausch(self, matnr_code, version_1, version_2,use_1,use_2,lostrat_1,lostrat_2):
		
		cost_v1 = self.cost_cat(matnr_code, version_1,1,0)#版本一物料单位总成本
		cost_v2 = self.cost_cat(matnr_code, version_2,1,0)#版本二物料单位总成本
		
		cost_inf = cost_v2 - cost_v1
		use_inf = use_2*(1+lostrat_2)- use_1*(1+lostrat_1)
		
		cost_diff = (cost_v2 - cost_v1) * use_2*(1+lostrat_2)
		use_diff = (use_2*(1+lostrat_2) - use_1*(1+lostrat_1)) * cost_v1
		
		cost_M_1 = self.cost_cat(matnr_code, version_1,use_1,lostrat_1)
		cost_M_2 = self.cost_cat(matnr_code, version_2,use_2,lostrat_2)
		
		if use_inf :
			print ('物料%s在%s>>>%s阶段用量变化:%.3f，总成本变化:%.3f'%(matnr_code, version_1, version_2, use_inf, use_diff))			 
			self.query_records_insert("2100",matnr_code,version_1,version_2,"1","1",use_1*(1+lostrat_1),use_2*(1+lostrat_2),use_inf,use_diff,"物料用量(损耗率)变化",time.strftime("%F"))
		if cost_inf:
			print ('物料%s在%s>>>%s阶段单位总成本变化:%.3f，总成本变化:%.3f'%(matnr_code, version_1, version_2, cost_inf, cost_diff))
			self.query_records_insert("2100",matnr_code,version_1,version_2,"1","1",cost_v1,cost_v2,cost_inf,cost_diff,"单位物料总成本变化",time.strftime("%F"))
		
		if cost_diff >= (cost_M_2 - cost_M_1) * self.weight :
			print ('物料%s在%s>>>%s阶段单位总成本变化差异值超出权值，正在挖掘具体原因'%(matnr_code, version_1, version_2))
			return 1,cost_diff
		
		return 0,0
	
	
	#单个工序总成本
	def process_cost(self,code, process_name, v):
		cursor = self.conn.cursor()

		sql = ('SELECT'
				   ' a.labor_hour*b.labor_hour_rate'
				   '+a.machine_hour*b.equip_hour_rate'
				   '+a.burning_hour*b.fuel_hour_rate'
				   '+a.auxiliary_hour*b.auxiliary_hour_rate'
				   '+a.other_hour*b.other_hour_rate'
				   ' FROM product_process_maintenance a JOIN hour_rate b ON a.cost_center_code = b.cost_center_code'
				   ' WHERE a.main_part_number="{0}" AND a.process_name="{1}" AND a.version_number="{2}"AND b.version_number="{2}"'
				   ).format(code, process_name, v)
		try:			
			cursor.execute(sql)
			proc_cost = float(cursor.fetchone()[0])
			
		finally:
			cursor.close()
		return proc_cost
	
	#增加的工序成本
	def process_add_check(self, code, process_name, version_1, version_2):
		process_add_cost = self.process_cost(code, process_name, version_2)
		
		print("物料%s在%s阶段多出工序：%s，造成本阶总成本变化%.3f"%(code, version_2, process_name, process_add_cost))
		self.query_records_insert("2100",code,version_1,version_2,"0","1",0,process_add_cost,process_add_cost,process_add_cost,"增加工序"+process_name,time.strftime("%F"))

	#减少的工序成本降低记录
	def process_red_record(self, code, process_name, version_1, version_2):
		process_red_cost = self.process_cost(code, process_name, version_2)
		
		print("物料%s在%s阶段减少工序：%s，造成本阶总成本变化%.3f"%(code, version_2, process_name, -process_red_cost))
		self.query_records_insert("2100",code,version_1,version_2,"1","0",process_red_cost,0,-process_red_cost,-process_red_cost,"减少工序"+process_name,time.strftime("%F"))	
			
	#相同的工序阈值判别
	def process_same_check(self, code, process_name, version_1, version_2,diff_value):
		process_same_cost_1 = self.process_cost(code, process_name, version_1)
		process_same_cost_2 = self.process_cost(code, process_name, version_2)
		cost_diff = process_same_cost_2 - process_same_cost_1
		
		if cost_diff:
			print("物料%s的工序：%s，在%s>>>%s阶段费用总成本（不含本材）变化%.3f"%(code, process_name, version_1, version_2, cost_diff))
			self.query_records_insert("2100",code,version_1,version_2,"1","1",process_same_cost_1,process_same_cost_2,cost_diff,cost_diff,"工序"+process_name+"的费用总成本发生变化",time.strftime("%F"))
			
		if cost_diff > diff_value * self.weight :
			print("物料%s的工序：%s，在%s>>>%s阶段费用总成本（不含本材）变化差异值超出权重，正在挖掘具体原因"%(code, process_name, version_1, version_2))
			return 1,cost_diff
		
		else:
			print("物料%s的工序：%s，在%s>>>%s阶段费用总成本（不含本材）变化差异值未超出权重"%(code, process_name, version_1, version_2))
			return 0,0
		
	#单个工序下本阶（人工、设备、燃动、辅料、其他）成本、工时、小时费率判别	
	def single_process_cost_stage_hour_rate_check(self, code, process_name, version_1, version_2, process_cost_diff,select_hour, select_rate):
		cursor = self.conn.cursor()
		sql_1 = ('SELECT'
				   ' a.{0}, b.{1}'				   
				   ' FROM product_process_maintenance a JOIN hour_rate b ON a.cost_center_code = b.cost_center_code'
				   ' WHERE a.main_part_number="{2}" AND a.process_name="{3}" AND a.version_number="{4}" AND b.version_number="{4}";'
				   ).format(select_hour, select_rate, code, process_name, version_1)
		sql_2 = ('SELECT'
				   ' a.{0}, b.{1}'				   
				   ' FROM product_process_maintenance a JOIN hour_rate b ON a.cost_center_code = b.cost_center_code'
				   ' WHERE a.main_part_number="{2}" AND a.process_name="{3}" AND a.version_number="{4}" AND b.version_number="{4}";'
				   ).format(select_hour, select_rate, code, process_name, version_2)
		
		try:
			cursor.execute(sql_1)
			hour_1, rate_1 = cursor.fetchone()
			cursor.execute(sql_2)
			hour_2, rate_2 = cursor.fetchone()
			hour_1 = float(hour_1)
			rate_1 = float(rate_1)
			hour_2 = float(hour_2)
			rate_2 = float(rate_2)
			cost_1 = hour_1 * rate_1
			cost_2 = hour_2 * rate_2
			cost_diff = cost_2 - cost_1
			
			if cost_diff:
				print("物料%s的工序：%s 在%s>>>%s阶段，%s变化%.3f"%(code,process_name,version_1,version_2,cost_stage_dic[select_hour],cost_diff))
				self.query_records_insert("2100",code,version_1,version_2,"1","1",cost_1,cost_2,cost_diff,cost_diff,"工序"+process_name+cost_stage_dic[select_hour]+"发生变化",time.strftime("%F"))
			
			if cost_diff > process_cost_diff * self.weight:
				print("物料%s的工序：%s 在%s>>>%s阶段，%s变化差异值超出权重，正在挖掘具体原因"%(code,process_name,version_1,version_2,cost_stage_dic[select_hour]))
				
				rate_diff = (rate_2 - rate_1) * hour_2
				hour_diff = (hour_2 - hour_1) * rate_1
				
				if rate_diff:
					print("物料%s的工序：%s 在%s>>>%s阶段，小时费率变化%.3f，造成成本变化%.3f"%(code,process_name,version_1,version_2,(rate_2-rate_1),rate_diff))
					self.query_records_insert("2100",code,version_1,version_2,"1","1",rate_1,rate_2,rate_2-rate_1,rate_diff,"工序"+process_name+cost_stage_dic[select_hour]+"小时费率发生变化",time.strftime("%F"))
				if hour_diff:
					print("物料%s的工序：%s 在%s>>>%s阶段，工时变化%.3f，造成成本变化%.3f"%(code,process_name,version_1,version_2,(hour_2-hour_1),hour_diff))
					self.query_records_insert("2100",code,version_1,version_2,"1","1",hour_1,hour_2,hour_2-hour_1,hour_diff,"工序"+process_name+cost_stage_dic[select_hour]+"工时发生变化",time.strftime("%F"))
							
		finally:
			cursor.close()
				
	#汇总工序下本阶（人工、设备、燃动、辅料、其他）成本、工时、小时费率判别			  
	def all_process_cost_stage_hour_rate_check(self, code, process_name, version_1, version_2,process_cost_diff):
			self.single_process_cost_stage_hour_rate_check(code, process_name, version_1, version_2,process_cost_diff, select_hour="labor_hour", select_rate="labor_hour_rate")
			self.single_process_cost_stage_hour_rate_check(code, process_name, version_1, version_2,process_cost_diff, select_hour="machine_hour", select_rate="equip_hour_rate")
			self.single_process_cost_stage_hour_rate_check(code, process_name, version_1, version_2,process_cost_diff, select_hour="burning_hour", select_rate="fuel_hour_rate")
			self.single_process_cost_stage_hour_rate_check(code, process_name, version_1, version_2,process_cost_diff, select_hour="auxiliary_hour", select_rate="auxiliary_hour_rate")
			self.single_process_cost_stage_hour_rate_check(code, process_name, version_1, version_2,process_cost_diff, select_hour="other_hour", select_rate="other_hour_rate")
			
	#导出表		
	def query_records_insert(self,factory,material_number,standard_version,actual_version,material_in_standard,material_in_actual,standard_value,actual_value,diff_value,diff_cost,cause,query_time):
		
		cursor = self.conn.cursor()
			
		sql = 'INSERT INTO contrast_cause_output VALUES ("{0}","{1}","{2}","{3}","{4}","{5}",{6},{7},{8},{9},"{10}","{11}")'.format(factory,material_number,standard_version,actual_version, \
																										 material_in_standard,material_in_actual,standard_value,\
																										 actual_value,diff_value,diff_cost,cause,query_time)
		try:
			
		    cursor.execute(sql)
			#self.conn.commit()
		except :
			print("执行cursor.execute和fetchone语句出错！")
		cursor.close()
			