import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.font_manager import FontProperties



ORGPATH=os.path.dirname(os.path.abspath(__file__))
PATH=ORGPATH+"/{}"
# 读取xlsx文件


def yearly_bill(data_list):
    pass

def monthly_bill(data_list):
    pass

def daily_bill(data_list):
    arr=add_all(data_list)
    date = [data[0].strftime('%Y-%m-%d') for data in arr]
    costs = [data[1] for data in arr]
    
    colors=[color_select(cost) for cost in costs]
    all_costs=sum(costs)

    

    # 创建柱形图
    font = FontProperties(fname=PATH.format("files/font.ttf"))
    
    print(colors)
    plt.figure(figsize=(10, 6))
    plt.bar(date, costs, color=plt.cm.hsv(colors))
    plt.xlabel('日期', fontproperties=font)
    plt.ylabel('花费(英镑)', fontproperties=font)
    plt.title(f'每日花费清单---共{round(all_costs,2)}英镑', fontproperties=font)

    # 自动旋转 x 轴标签以避免重叠
    plt.xticks(rotation=45, ha='right')

    # 显示图形
    plt.tight_layout()
    plt.show()
    
def color_select(cost):
    # if cost<=10:
    #     return 0.75
    if cost>=0 and cost<=20:
        return 0.4-cost*0.3/20
    else:
        return 0
    #0.4
def add_all(data_list):
    day_list=[]
    for datas in data_list:
        sun_money=0
        for data in datas[1:]:
            if pd.notna(data):
                money=data.split("-")[0]
                sun_money+=float(money)
        day_list.append([datas[0],sun_money])
    return day_list



def main():

    df = pd.read_excel(PATH.format('files/记账.xlsx'))
    
    df['date']=pd.to_datetime(df['date'] ,origin='1900-01-01', unit='D')- pd.Timedelta(days=2)
    data_list = df.values.tolist()
    #print(data_list)


    # for data in data_list:
    #     data[0]=pd.to_datetime(data[0],format='%d/%m/%Y')
        
        #print(data_list)
        # df["日期"] = pd.to_datetime(df["日期"])
    daily_bill(data_list)

# 绘制数据表
# plt.figure(figsize=(10, 6))
# plt.axis('off')
# plt.table(cellText=df.head().values,
#           colLabels=df.columns,
#           cellLoc = 'center', loc='center')

# plt.show()
if __name__=="__main__":
    main()