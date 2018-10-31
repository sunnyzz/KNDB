# -*- coding: utf-8 -*-
import sys
import mysql.connector as mc
import Cost_mining
import Bom_alteration


        
        
if __name__ == "__main__":
    
    #==========================================================================
    ###参数输入    
    material_code = sys.argv[1]
    bom_version_1 = sys.argv[2]
    bom_version_2 = sys.argv[3]
    
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

    #==========================================================================
    ###实例化方法对象   
    cost_mining = Cost_mining.CostMining(conn,0.03)
    bsa = Bom_alteration.BomStrucAlteration(conn)
    
    ###定义递归对比
    def finance_analysis(material,version_1,version_2,use_1,use_2,lost_1,lost_2):
        
        print('+===========================================================+')              
        class_cost,_use_diff = cost_mining.check_unitcost_menge_ausch(material,version_1,version_2,use_1,use_2,lost_1,lost_2)
        
        if class_cost:
            print('+___________________________________________________________+')
            #cost_mining.cost_stage_component_check(material,version_1,version_2)
            
            cost_stage,_diff_value = cost_mining.cost_stage_component_check(material, version_1, version_2,_use_diff)  #本材、本阶总成本（不含本材）阈值判别
            
            if cost_stage:    #本阶总成本（不含本材）阈值判别为1
                process_add, process_same = bsa.process_bom_check(material, version_1, version_2)
                
                for process_name in process_add:    #增加的工序逐个阈值判别
                    
                    cost_mining.process_add_check(material, process_name, version_1, version_2,_diff_value)
                    
                for process_name in process_same:   #相同的工序逐个阈值判别
                    
                    pro_same,_cost_diff = cost_mining.process_same_check(material, process_name, version_1, version_2,_diff_value)
                    
                    if pro_same:
                        cost_mining.all_process_cost_stage_hour_rate_check(material, process_name, version_1, version_2,_cost_diff)
            
            
            
            cost_accumulated_value,diff_value_ = cost_mining.cost_accumulated_component_diff(material,version_1,version_2,_use_diff)
        
            if cost_accumulated_value:
                print('+___________________________________________________________+')
                bom_add,bom_same =  bsa.check(material,version_1,version_2)
            
                for i_code in bom_add:
                
                    cost_mining.sub_cost_total_diff_with_matnr(material,version_1,i_code,version_2,diff_value_)
                
                for i_code in bom_same:
                    
                    
                    u_1,l_1 = cost_mining.use_lost_cat(material,i_code,version_1)
                    u_2,l_2 = cost_mining.use_lost_cat(material,i_code,version_2)
                    
                    use_total_cost_ = cost_mining.sub_total_cost_check(i_code,version_1,version_2,u_1,u_2,l_1,l_2,diff_value_)
                    
                    if use_total_cost_:
                        finance_analysis(i_code,version_1,version_2,u_1,u_2,l_1,l_2)
       
    #==========================================================================
    
    ###执行
    use_total_cost = cost_mining.total_cost_check(material_code,bom_version_1,bom_version_2)
        
    if use_total_cost:
        
        finance_analysis(material_code,bom_version_1,bom_version_2,1,1,0,0)
    conn.commit()
    conn.close()   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    