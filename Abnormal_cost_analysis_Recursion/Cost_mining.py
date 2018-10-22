# -*- coding: utf-8 -*-

cost_stage_dic={'material_cost_stage':'本阶物料成本',
                    'labor_cost_stage':'本阶人工成本',
                    'equip_cost_stage':'本阶设备成本',
                    'burning_cost_stage':'本阶燃动成本',
                    'auxiliary_cost_stage':'本阶辅助成本',
                    'other_cost_stage':'本阶其他成本'}

class CostMining(object):
    def __init__(self,conn):
        self.conn = conn
        
    def cost_cat(self,code,v,use_number):
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
            coca = float(cursor.fetchone()[0])*use_number
        finally:
            cursor.close()
        return coca
        
    def total_cost_check(self,code,v1,v2,use_number_1=1,use_number_2=1):
        cost1 = self.cost_cat(code,v1,use_number_1)
        cost2 = self.cost_cat(code,v2,use_number_2)
        diff_cost = abs(cost1-cost2)
        
        notif_red = "单位物料%s总成本降低%.3f" if use_number_1==use_number_2==1 else "物料%s总成本降低%.3f"
        notif_same = "单位物料%s总成本未发生改变" if use_number_1==use_number_2==1 else "物料%s总成本未发生改变"
        notif_incre = "单位物料%s总成本上升%.3f," if use_number_1==use_number_2==1 else "物料%s总成本上升%.3f,"
        if cost1 > cost2:
            
            print(notif_red%(code,diff_cost))
            return 0
        
        elif cost1 == cost2:
            #print(notif_same%code)            
            return 0
        else:
            print(notif_incre%(code,diff_cost),end='')
            if (cost2-cost1) < (cost1*0.03):
                print("但未超出阈值")
                return 0
            else:
                print("超出阈值")
                return 1
 

    def cost_stage_component_diff(self, code, version_1, version_2, select_object, select_table):
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
            diff_value = abs(value_1 - value_2)
            
            if value_1 > value_2:
                print("单位物料%s的%s降低%.3f"%(code,cost_stage_dic[select_object],diff_value))
                return 0
            
            elif value_1 == value_2:
                #print("单位物料%s的%s未发生改变"%(code, select_object))
                return 0
            
            else:
                print("单位物料%s的%s上升%.3f"%(code,cost_stage_dic[select_object],diff_value), end='')
                if diff_value < (value_1 * 0.03):
                    print("但未超出阈值")
                    return 0
                else:
                    print("超出阈值")
                    return 1
            
        except :
            print("执行cursor.execute和fetchone语句出错！")
            
        finally:
            cursor.close()   
    
    def cost_stage_component_check(self,code, version_1, version_2):
        self.cost_stage_component_diff(code, version_1, version_2, select_object = "material_cost_stage", select_table = "cost_material_stage")
        self.cost_stage_component_diff(code, version_1, version_2, select_object = "labor_cost_stage", select_table = "cost_stage")
        self.cost_stage_component_diff(code, version_1, version_2, select_object = "equip_cost_stage", select_table = "cost_stage")
        self.cost_stage_component_diff(code, version_1, version_2, select_object = "burning_cost_stage", select_table = "cost_stage")
        self.cost_stage_component_diff(code, version_1, version_2, select_object = "auxiliary_cost_stage", select_table = "cost_stage")
        self.cost_stage_component_diff(code, version_1, version_2, select_object = "other_cost_stage", select_table = "cost_stage")
    
    
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



        
    def cost_accumulated_component_diff(self, code, version_1, version_2):
        value_1 = self.cost_accumulated_component(code, version_1)
        value_2 = self.cost_accumulated_component(code, version_2)
        
        diff_value = abs(value_1 - value_2)
        
        if value_1 > value_2:
            print("单位物料%s的累计总成本降低%.3f"%(code, diff_value))
            return 0
        
        elif value_1 == value_2:
            #print("单位物料%s的累计总成本未发生改变"%(code))
            return 0
        
        else:
            print("单位物料%s的累计总成本上升%.3f"%(code, diff_value), end='')
            if diff_value < (value_1 * 0.03):
                print("但未超出阈值")
                return 0
            else:
                print("超出阈值")
                return 1
                    
            
        
        
    def sub_cost_total(self, sub_code, v, matnr_code):
        cursor = self.conn.cursor()
        sql = ('select'
               ' (a.material_cost_stage'
               '+b.labor_cost_stage+b.equip_cost_stage+b.burning_cost_stage+b.auxiliary_cost_stage+b.other_cost_stage'
               '+c.material_cost_accumulated'
               '+d.labor_cost_accumulated+d.equip_cost_accumulated+d.burning_cost_accumulated+d.auxiliary_cost_accumulated+d.other_cost_accumulated)'
               '*e.menge * (1 + e.ausch)'
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
    
    
    def sub_cost_total_diff_with_matnr(self, matnr_code, version_1, sub_code, version_2):
        sub_cost = self.sub_cost_total(sub_code, version_2, matnr_code)
        matnr_cost = self.cost_accumulated_component(matnr_code, version_1)
        #diff_value = abs(idnrk_cost - matnr_cost * 0.03)
        if sub_cost > matnr_cost * 0.03:
            print("单位物料%s的%s阶段多出子件物料%s，造成累计总成本上升%.3f"%(matnr_code, version_2, sub_code, sub_cost))
        
        else:
            print("单位物料%s的%s阶段多出子件物料%s，但未超出阈值"%(matnr_code, version_2, sub_code))
        
    def use_lost_cat(self, matnr_code, sub_code, version_number):
        cursor = self.conn.cursor()
        sql = 'select menge * (1 + ausch) as total from bom_relevancy where matnr = "{0}" and idnrk = "{1}" and version_number = "{2}"'.format(matnr_code, sub_code, version_number)
               
        try:
            cursor.execute(sql)
            value = float(cursor.fetchone()[0])
            return value
        
        except :
            print("执行cursor.execute和fetchone语句出错！")
            
        finally:
            cursor.close()