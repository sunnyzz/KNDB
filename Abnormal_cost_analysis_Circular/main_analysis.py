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
              'host': '131.232.81.34',
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
        
    cost_mining = Cost_mining.CostMining(conn)
    bsa = Bom_alteration.BomStrucAlteration(conn)
    
    #自定义0阶对比
    def finance_analysis(material,version_1,version_2,use_1,use_2):
        use_total_cost = cost_mining.total_cost_check(material,version_1,version_2,use_1,use_2)
        if use_total_cost:
            
            unit_total_cost = cost_mining.total_cost_check(material,version_1,version_2)    
            
            if unit_total_cost:
                cost_mining.cost_stage_component_check(material,version_1,version_2)
                
                cost_accumulated_value = cost_mining.cost_accumulated_component_diff(material,version_1,version_2)
            
                if cost_accumulated_value:
                    
                    bom_alter_set =  bsa.check(material,version_1,version_2)
                
                    for i_code in bom_alter_set[0]:
                    #cost_mining.single_work_cost_total(i_code, bom_vision_2, material_code)
                        cost_mining.sub_cost_total_diff_with_matnr(material,version_1,i_code,version_2)
                        
                    return bom_alter_set[1]
            return []
        else:
            return []
                
        
                    
                #for i_code in bom_alter_set[1]:
                
                    
       
    init_cost_result = list(finance_analysis(material_code,bom_version_1,bom_version_2,1,1))
    
    material_codes = []
    for i in range(len(init_cost_result)):
        material_codes.append(material_code)


# =============================================================================
#     material_codes = []
# 
#     material_codes.append(list(material_code) * len(init_cost_result))
#     print(material_codes)
# =============================================================================
        
    
    while len(init_cost_result) != 0:
        matnr_code = []
        sub_code = []
        
        number = 0
        for i_code in init_cost_result:
            
            value_1 = cost_mining.use_lost_cat(material_codes[number], i_code, bom_version_1)
            value_2 = cost_mining.use_lost_cat(material_codes[number], i_code, bom_version_2)
            sub_list = list(finance_analysis(i_code,bom_version_1,bom_version_2,value_1,value_2))

            number +=1
            sub_code.extend(sub_list)
          
            for i in range(len(sub_list)):
                matnr_code.append(i_code)

# =============================================================================
#             matnr_code.append(list(i_code) * len(sub_list))           
#             
# =============================================================================
           
        material_codes = matnr_code
        init_cost_result = sub_code
            
        
    
    conn.close()   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    