from Parser import ExprNode
from Parser import Parser
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
import mpl_toolkits.axisartist as axisartist
from math import *
import re
import os

class SemanticError(Exception):
    def __init__(self, expression):
        self.message = "expression {} is wrong".format(expression)

    def __repr__(self):
        return self.message

#For-step：按start、end、step生成一序列，每个元素再带到func里，得到坐标集
#1.SCALE：给x,y坐标分别乘一个值
#2.ROT: x'=xcosθ-ysinθ，y'=xsinθ+ycosθ
#3.ORIGIN：给x,y坐标分别加一个值

single = ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt']
double = ['+', '-', '*', '**', '/']

#前缀式转中缀式
def trans_middle(exp):
	tmp = ''
	if len(exp) == 0:
		return ''
	for i in range(len(exp)):
		if type(exp[i]) != str:
			exp[i] = str(exp[i])
	while len(exp) > 1:
		for e in exp[::-1]:
			index = exp.index(e)
			if e in double:
				a = exp.pop(index+2)
				b = exp.pop(index+1)
				sig = exp[index]
				tmp = '(' + b + sig + a + ')'
				exp[index] = tmp
			elif e in single:
				a = exp.pop(index+1)
				doub = exp[index]
				tmp = doub + "(" + a + ")"
				exp[index] = tmp
			else:
				continue
	return exp[0]

#位置比例的正常化
#绘制多个函数
def Draw(for_start, for_end, for_step, start_x, start_y, scale_x, scale_y, rot_angele, origin_x, origin_y):
	#创建画布
	global fig, ax, majorFormatter
	#使用axisartist.Subplot方法创建一个绘图区对象ax
	#ForPlot
	step = np.linspace(for_start, for_end, for_step)
	try:
		start_x = eval('['+start_x+' for T in step]')
	except:
		raise SemanticError(start_x)
	try:
		start_y = eval('['+start_y+' for T in step]')
	except:
		raise SemanticError(start_y)
	#ScalePlot
	#print(type(scale_x))
	start_x = [T*scale_x for T in start_x]
	start_y = [T*scale_y for T in start_y]
	#RotPlot
	start_x = [start_x[i]*cos(rot_angele)-start_y[i]*sin(rot_angele) for i in range(len(start_x))]
	start_y = [start_x[i]*sin(rot_angele)+start_y[i]*cos(rot_angele) for i in range(len(start_y))]
	#OriginPlot
	start_x = [T+origin_x for T in start_x]
	start_y = [T+origin_y for T in start_y]
	#绘图
	plt.plot(start_x, start_y)
	#plt.show()

def Interpreter(filename):#局部变量问题
    global origin_x, origin_y, rot_angele, scale_x, scale_y, for_start, for_end, for_step, scale_x, scale_y
    global result_dict
    parser = Parser(filename)
    parser.parser_program()
    parser.getResultDict()
    parser.Print_result()
    parser.final_result()
    result_dict = {}
    result_dict = parser.resultDict2
    #前缀式转中缀式
    #print(result_dict)
    for key in result_dict:
    	result_dict[key] = trans_middle(result_dict[key])
    globals().update(result_dict)
    print(start_y)
    #变量处理
    if origin_x == '':
    	origin_x = '0'
    if origin_y == '':
    	origin_y = '0'
    if rot_angele == '':
    	rot_angele = '0'
    if scale_x == '':
    	scale_x = '1'
    if scale_y == '':
    	scale_y = '1'
    try:
    	for_start = eval(for_start)
    except:
    	raise SemanticError(for_start)
    try:
    	for_end = eval(for_end)
    except:
    	raise SemanticError(for_end)
    try:
    	for_step = eval(for_step)
    except:
    	raise SemanticError(for_step)
    try:
    	origin_x = eval(origin_x)
    except:
    	raise SemanticError(origin_x)
    try:
    	origin_y = eval(origin_y)
    except:
    	raise SemanticError(origin_y)
    try:
    	rot_angele = eval(rot_angele)
    except:
    	raise SemanticError(rot_angele)
    try:
    	scale_x = eval(scale_x)
    except:
    	raise SemanticError(scale_x)
    try:
    	scale_y = eval(scale_y)
    except:
    	raise SemanticError(scale_y)
    #绘图
    Draw(for_start, for_end, for_step, start_x, start_y, scale_x, scale_y, rot_angele, origin_x, origin_y)

if __name__ == "__main__":
    origin_x = ''
    origin_y = ''
    rot_angele = ''
    scale_x = ''
    scale_y = ''
    for_start = ''
    for_end = ''
    for_step = ''
    scale_x = ''
    scale_y = ''
    result_dict = {}
    
    #文件处理
    filename = input("Source filename:")
    tempfiles = []
    source = open(filename, encoding='UTF-8')
    f = source.read().upper()
    regex = re.compile("(FOR[\t ]*T[\t ]*FROM.*?TO.*?STEP.*?DRAW[\t ]*\(.*?,.*?\);[\t\n\r ]*)")
    count = 0
    while 1:
    	result = re.search(regex, f)
    	if result == None:
    		break
    	else:
    		#文件操作
    		tempfiles.append(open('f%d' % count, 'w+'))
    		tempfiles[count].write(f[:result.span()[1]])
    		tempfiles[count].close()
    		f = f[result.span()[1]:]
    		count += 1
    #画图准备
    fig = plt.figure(figsize=(8, 8))
    ax = axisartist.Subplot(fig, 111)  
	#将绘图区对象添加到画布中
    fig.add_axes(ax)
	#x、y轴
    ax.axis[:].set_visible(False)
    ax.axis["x"] = ax.new_floating_axis(0,0)
    ax.axis["x"].set_axisline_style("->", size = 1.0)
    ax.axis["y"] = ax.new_floating_axis(1,0)
    ax.axis["y"].set_axisline_style("-|>", size = 1.0)
    ax.axis["x"].set_axis_direction("top")
    ax.axis["y"].set_axis_direction("right")
    majorFormatter = FormatStrFormatter('%1.1f')
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.yaxis.set_major_formatter(majorFormatter)
    #坐标上限
    plt.xlim((-5,5))
    plt.ylim((5,-5))
    #刻度
    plt.xticks(np.linspace(-5,5,11))
    plt.yticks(np.linspace(-5,5,11))
    #依次处理
    for tmp in tempfiles:
    	Interpreter(tmp.name)
    #关闭删除临时文件
    for tmp in tempfiles:
    	tmp.close()
    	os.remove(tmp.name)
    source.close()
    plt.show()