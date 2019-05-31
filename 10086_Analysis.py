import xlrd
import matplotlib.pyplot as plt
from UserData import UserDataInfo
import datetime
import pandas as pd
import json
from station2location import station2location
import os
# def readData(url):
#     data = xlrd.open_workbook(url)
#     table = data.sheets()[0]  # 多张sheet的情况读取第一张
#     nrows = table.nrows
#     ncols = table.ncols
#     list = []
#     for rownum in range(0, nrows):
#         row = table.row_values(rownum)
#         print(row)
#         # for i in range(0, ncols):  # 转码unicode转utf-8
#         #     row[i] = row[i]
#         if row:
#             list.append(row)
#     return list

#读取文件，返回data（类型dataframe）
#同时读取多个excel文件进行合并

#从excel中读取数据
def readDate_pd(url):
    data = pd.read_excel(url,usecols=[u'起始时间', u'通信地点', u'通信方式',
                                        u'对方号码', u'通信时长', u'通信类型',
                                        u'基站小区号', u'IMEI', u'IMSI'],
                        dtype={'IMEI':str,'IMSI':str,u'基站小区号':str})
    # print(data.index)
    return data
'''
Operation	                    Syntax	        Result
Select column	                df[col]	        Series
Select row by label	            df.loc[label]	Series
Select row by integer location	df.iloc[loc]	Series
Slice rows	                    df[5:10]	DataFrame
Select rows by boolean vector	df[bool_vec]	DataFrame
'''
#处理data中相关数据,添加loc和cid选项后合并表
def dealData(data):

    for i in data.index:
        # 将表中通话起始时间序列化，转换成timestamp
        datetimes = data['起始时间'].at[i]
        data['起始时间'].at[i] = datetimeDecode(datetimes)
        # 将表中通信时长序列化，str转换成int，单位为秒
        calltimes = data['通信时长'].at[i]
        data['通信时长'].at[i] = timeDecode(calltimes)
        # 处理小区基站号,并加入到新表当中
    stationlists = data['基站小区号'].str.split('/',expand=True)
    data['loc'] = stationlists[0].str.upper()
    data['cid'] = stationlists[1].str.upper()

    return data
# # 行为分析
# def behavior_analysis(datalist):
#     t = 1
#     for line in datalist:
#         if (t == 1):
#             t = 3
#             continue
#         dh = dateDecode(line[2])
#         day = int(dh[0])
#         hour = int(dh[-1])
#
#         user.day_intervel[day] += 1
#         user.time_intervel[hour / 2] += 1
#
#         timeStr = line[3]
#         timelong = timeDecode(timeStr)
#
#         if line[4] == '主叫':
#             user.calling_times += 1
#             user.calling_long += timelong
#         if line[4] == '被叫':
#             user.called_times += 1
#             user.called_long += timelong
#
#     user.call_times = user.calling_times + user.called_times  # 总次数
#     user.call_long = user.calling_long + user.called_long  # 总时长


# 序列化通话时间,返回为(int类型)秒
#将字符串转成timestamp格式
def timeDecode(timeStr):
    call_time = 0
    if timeStr.find('时') != -1:
        call_time = pd.to_datetime(timeStr, format='%H时%M分%S秒')
        # print((call_time-basetime).seconds)
        return (call_time-basetime).seconds
    if timeStr.find('时') == -1 and timeStr.find('分') !=-1:
        call_time = pd.to_datetime(timeStr, format='%M分%S秒')
        # print((call_time-basetime).seconds)
        return (call_time-basetime).seconds
    if timeStr.find('时') == -1 and timeStr.find('分') ==-1:
        call_time = pd.to_datetime(timeStr, format='%S秒')
        # print((call_time-basetime).seconds)
        return (call_time-basetime).seconds
    else:
        return call_time

#通话时间里面定义一个基准时间
basetime = pd.to_datetime('1900-01-01 00:00:00',format='%Y-%m-%d %H:%M:%S')

# 序列化通话时间戳
def datetimeDecode(datetimeStr):
    datetime = pd.to_datetime(datetimeStr,format='%Y-%m-%d %H:%M:%S')
    return datetime

# def printout():
#     print
#     "被叫次数：", user.called_times
#     print
#     "被叫时长：", timeEncode(user.called_long)
#
#     print
#     "主叫次数：", user.calling_times
#     print
#     "主叫时长：", timeEncode(user.calling_long)
#
#     print
#     "总次数：", user.call_times
#     print
#     "总时长：", timeEncode(user.call_long)
#
#     print
#     "日期", user.day_intervel
#     print
#     "时段", user.time_intervel

#类型str，基站返回列表[0]:lac,[1]:cid
#基站数据16进制转换10进制
def stationDecode(data):
    hex_header = '0x'
    for i in data.index:
        if data['loc'].at[i] == 'NULL':
            data['loc'].at[i] = None
        else:
            data['loc'].at[i] = hex_header + data['loc'].at[i]

        if data['cid'].at[i] == 'NULL':
            data['cid'].at[i] = None
        else:
            data['cid'].at[i] = hex_header + data['cid'].at[i]
    # print(data)
        return data

#格式化基站代码，station2location解析出经纬度和地址，返回
def getlocation(data):
    locations = stationDecode(data)
    for i in range(20):
        stations = []
        stations.extend([data['loc'].at[i],data['cid'].at[i]])
        station2location(stations)


# 数据可视化
def dataVisualization(data):
    plt.plot(data[u'通信时长'].sum(), 'k')
    plt.plot(data[u'起始时间'].sum(), 'bo')
    plt.xlabel(u'date')
    plt.ylabel(u'通话次数')
    plt.title(u'每日通话分析')
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.4)
    plt.show()

#连续读取多个文件话单
def listDir(rootdir):
    filelist = []
    files_num = 0
    for filename in os.listdir(rootdir):
        pathname = os.path.join(rootdir, filename)
        if (os.path.isfile(pathname)):
            filelist.append(pathname)
            files_num= files_num+1
        else:
            listDir(pathname)
    print('一共{}个话单文件'.format(files_num))
    return filelist

#合并多个话单
def append_list(filelist):
    load_files_Num = 0
    big_data = 0
    for filename in filelist:
        try:
            #读取每一个话单文件
            data_temp = readDate_pd(filename)
            #按条件处理好每个话单文件
            datas = dealData(data_temp)
            load_files_Num = load_files_Num +1
            if load_files_Num ==1:
                big_data = datas
            else:
                big_data = big_data.append(datas,ignore_index=True)
        except:
            print("格式出错,请确认文件格式是否为xlsx或者标准导出格式")
    print('共处理了{}个话单文件'.format(load_files_Num))
    big_data.to_excel('D:/data/1/1.xlsx')

# # stationDecode(' /0169ba83')
# url = "D:/data/1.xlsx"
# # datalist = readData(url)
# a = readDate_pd(url)
# b = dealData(a)
# getlocation(b)
# datetimeDecode('2019-01-01 14:06:48')
# user = UserDataInfo()
# behavior_analysis(datalist)
#
# printout()

HD_file_name_list = listDir('D:/data/1')
append_list(HD_file_name_list)