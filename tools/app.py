#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (C) yanghongshun@gmail.com
#

import os,sys,configparser,getopt
import csv,shutil
from openpyxl import Workbook
from openpyxl import load_workbook

# get custom columns data from data files 

APP_TOOLS_DIRNAME = 'tools'
APP_DATA_DIRNAME = 'data'
APP_RESULT_DIRNAME = 'result'

def usage():
    print('get columns data from single file or directory')
    print('./app.py -i ../data/10262016 -c 0,1,2,3,4,5,6,7,8,9,10,17,18,19 -s "" -d "," ')

def getDataFromCSV(title,spliter,filePath):
	print("reading data from csv file:%s" % filePath)
	data = []
	if not os.path.isfile(filePath):
		print("%s not exist!" % filePath)
		sys.exit()
	
	csvfile=csv.reader(open(filePath, 'r'),delimiter=spliter)
	
	for line in csvfile:
		data.append(line)
	if title == True:
		print("delete first row:title row")
		del data[0]
	print("reading end")
	
	return data


def saveDataToCSV(title,data,filePath,fmt=''):
	print("saving data to csv file:%s" % filePath)
	
	if os.path.isfile(filePath):
		print("delete old csv file:%s" % filePath)
		os.remove(filePath)
	
	file_handle = open(filePath,'w')
	
	if fmt=='':
		csv_writer = csv.writer(file_handle,delimiter=' ')
	else:
		csv_writer = csv.writer(file_handle,delimiter=fmt)
	
	if len(title) >0 :
		csv_writer.writerow(title)
	
	csv_writer.writerows(data)
	
	file_handle.close()
	
	print("saved end")

def generateResultFilePath(dataFilePath,prefix=''):
	
	print("generating result file path from data file path:%s" % dataFilePath)
	filename,fileext=os.path.splitext(os.path.basename(dataFilePath))
	
	if prefix=='':
		resultFileName = 'result_'+filename+'.csv'
	else:
		resultFileName = 'result'+prefix+filename+'.csv'


	dataFileAbsPath = os.path.abspath(dataFilePath)
	
	app_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))	
	app_data_dir = app_root_dir + os.sep + APP_DATA_DIRNAME+os.sep
	app_result_dir = app_root_dir + os.sep + APP_RESULT_DIRNAME+os.sep
	
	result_tmp_dirstr = os.path.dirname(dataFileAbsPath).replace(app_data_dir,'')
	
	resultFileDir = os.path.join(app_result_dir,result_tmp_dirstr)

	if not os.path.exists(resultFileDir):
		print("create directory:%s " % resultFileDir)
		os.makedirs(resultFileDir)
	
	resultFilePath = os.path.join(resultFileDir,resultFileName)
	print("result file path is:%s" % resultFilePath)
	print("generated end")
	return resultFilePath

def getColDataFromFile(dataFilePath,res_cols,space_replace,delimiter):
	_getColDataFromFile(dataFilePath,res_cols,space_replace,delimiter)
	
def _getColDataFromFile(dataFilePath,res_cols,space_replace,delimiter):
	print("acting input   data file")
	if os.path.isdir(dataFilePath):
		print("  data file is a directory:%s" % dataFilePath)
		for root,dirs,files in os.walk(os.path.abspath(dataFilePath)):
		    for file in files:
                        filename,fileext=os.path.splitext(file)
                        if fileext in ['.csv','.xlsx']:
                             datafileabspath = root+os.sep+file					
                             _getColDataFromSingleFile(datafileabspath,res_cols,space_replace,delimiter)
					
	elif os.path.isfile(dataFilePath):
            print("  data file is a single file:%s" % dataFilePath)
            datafileabspath = os.path.abspath(dataFilePath)
            filename,fileext=os.path.splitext(datafileabspath)
            if fileext in ['.csv','.xlsx']:
                _getColDataFromSingleFile(datafileabspath,res_cols,space_replace,delimiter)
	print("action is end")

def _getColDataFromSingleFile(datafileabspath,res_cols,space_replace,delimiter):
    print("data file :%s" % datafileabspath)
    if not os.path.isfile(datafileabspath):
        print("data file :%s is not exist!" % datafileabspath)
        sys.exit()


    resultFilePath = generateResultFilePath(datafileabspath)
    if os.path.isfile(resultFilePath):
        print("delete old  result file :%s" % resultFilePath)
        os.remove(resultFilePath)

    print("loading file")
    # print(datafileabspath)
    i=0
    filename,fileext=os.path.splitext(datafileabspath)
    if fileext in ['.csv','.xlsx']:
        inputFileDataSetOrig = []
        if fileext=='.csv':
            inputFileDataSetOrig = getDataFromCSV(False,',',datafileabspath)
        elif fileext == '.xlsx':
            wb=load_workbook(filename=datafileabspath,data_only=True,read_only=True)##fast mode
            ws=wb.active
            for row in ws.rows:
                file_row=[]
                for cell in row:
                    file_row.append(cell.value)
                inputFileDataSetOrig.append(file_row)
        
        inputFileDataSetOrigTitleRow = inputFileDataSetOrig[0]
        for col in inputFileDataSetOrigTitleRow:
            print(i,col)	
            i+=1	    
        inputFileColIndexMax = len(inputFileDataSetOrigTitleRow)-1
        
        res_cols = [x for x in res_cols if x <= inputFileColIndexMax]
        print("check valid column index")
        print(res_cols)
        colDataSet=[]       
        for cl in inputFileDataSetOrig:
            row=[]
            for idx in range(len(cl)):
                if idx in res_cols:
                    # no value is -1
                    if space_replace !='' and  cl[idx]=='':
                        cl[idx]=space_replace
                    row.append(cl[idx])
            
            colDataSet.append(row)
                
    saveDataToCSV([],colDataSet,resultFilePath,delimiter)	


def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hi:c:s:d:",["--input=","--columns=","--space-replace=","--delimiter="])
    except getopt.GetoptError as err:
        print(err) 
        usage()
        sys.exit(2)

    input_data=""	
    
    res_cols=""

    space_replace = ""

    delimiter = ""

    for opt,arg in opts:
        if opt in ('-h',"--help"):
            usage()
            sys.exit()
        elif opt in ('-i','--input'):
            input_data=arg
        elif opt in ('-c','--columns'):
            res_cols = arg.replace(',','|').replace(' ','|').split('|')
            # delete null
            res_cols = [x for x in res_cols if x !=''] 
            # delete duplicates
            res_cols = [int(res_cols[i]) for i in range(len(res_cols)) if i == res_cols.index(res_cols[i])]
        elif opt in ('-s','--space-replace'):
            space_replace = arg
        elif opt in ('-d','--delimiter'):
            delimiter = arg



    if input_data != '':
        getColDataFromFile(input_data,res_cols,space_replace,delimiter)
    else:
        sys.exit()


if __name__ == "__main__":
	main()





    
