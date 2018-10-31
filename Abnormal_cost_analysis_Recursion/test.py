# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 14:57:36 2018

@author: 赵忠祥
"""

import mysql.connector as mc   
    ###数据库配置    
config = {
              'host': '132.232.81.34',
              'user':'root',
              'password':'root1234',
              'database':'kndb'
              }
    
    ###数据库连接
try:
    conn = mc.connect(**config)
except mc.Error as e:
    print('connect fails!{}'.format(e))
cursor=conn.cursor()
			
sql = ('SELECT'
				   ' a.labor_hour*b.labor_hour_rate'
				   '+a.machine_hour*b.equip_hour_rate'
				   '+a.burning_hour*b.fuel_hour_rate'
				   '+a.auxiliary_hour*b.auxiliary_hour_rate'
				   '+a.other_hour*b.other_hour_rate'
				   ' FROM product_process_maintenance a JOIN hour_rate b ON a.cost_center_code = b.cost_center_code'
				   ' WHERE a.main_part_number="{0}" AND a.process_name="{1}" AND a.version_number="{2}";'
				   ).format(020100012201,准备,1.0.0)
try:
	cursor.execute(sql)
	proc_cost = float(cursor.fetchone()[0])				
finally:
    cursor.close()
print(proc_cost)