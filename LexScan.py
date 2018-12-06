#词法分析器
from collections import namedtuple
import math

Token = namedtuple('Token',['type','value','function'])
#标记行
LINETOKEN = namedtuple("LINETOKEN",['LineNo','Tokens'])

class lexScanner:
	def __init__(self, filename):
		self.filename = filename
		#特殊符号
		self.special = ('*','/','-','+','(',')',',',';','.')
		#关键字
		self.Token_table = {
				'T': Token('T', 0.0,None),
				'SIN': Token('FUNC', 0.0, 'sin'),
				'COS': Token('FUNC', 0.0, 'cos'),
				'TAN': Token('FUNC', 0.0, 'tan'),
				'LN': Token('FUNC', 0.0, 'log'),
				'EXP': Token('FUNC', 0.0, 'exp'),
				'SQRT':Token('FUNC', 0.0, 'sqrt'),
				'PI': Token('CONST_ID', 3.1415926, None),
				'E': Token('CONST_ID', 2.71828, None),
				'ORIGIN': Token('ORIGIN', 0.0, None),
				'SCALE': Token('SCALE',0.0, None),
				'ROT': Token('ROT', 0.0, None),
				'IS': Token('IS', 0.0, None),
				'FOR': Token('FOR', 0.0, None),
				'FROM': Token('FROM', 0.0, None),
				'TO': Token('TO', 0.0, None),
				'STEP': Token('STEP', 0.0, None),
				'DRAW': Token('DRAW', 0.0, None)
			}
		#状态机
		self.DFA_status = {
				0 : { 'letter': 1, 'digit': 2, '*':4, '/': 6, '-': 7,'+': 8, ',': 9, ';': 10, '(': 11, ')': 12},
				1 : {'letter' : 1, 'break':'ID'},
				2 : {'digit': 2, '.': 3,'break': 'CONST_ID'},
				3 : {'digit': 3, 'break': 'CONST_ID'},#小数
				4 : {'*': 5 ,'break': 'MULTIPLICATION'},
				5 : {'break': 'POWER'}, #乘方
				6 : {'/': 13,'break': 'DIVISION'},
				7 : {'-' : 13, 'break': 'MINUS'},
				8 : {'break': 'PLUS'},
				9 : {'break': 'COMMA'},
				10 : {'break': 'SEMICO'},
				11 : {'break': 'L_BRACKET'},
				12 : {'break': 'R_BRACKET'},
				13 : {'break': 'COMMENT'},
				14 : 'Digit Error' #小数错误
			}

		#绝对终态，直接返回
		self.final_status = (5,8,9,10,11,12,13)

	#状态转移
	def move(self, status, condition):
		try:
			next_status = self.DFA_status[status]
			return next_status[condition]
		except:
			return 14  #发生错误，返回ERROR

	def getWord(self, word):
		token = self.Token_table.get(word)
		if token is None: # 获取失败
			return Token("Word Error",word,None)
		else:
			return token

	#判断是否是终态，是则返回内容，不是返回None，错误返回“Error”
	def isFinal(self, status, nextword):
		if status in self.final_status:
			# 绝对终态，不管下一个是什么直接返回
			return self.DFA_status[status]['break']
		elif status == 1:
			if nextword.isalpha():#判断是否读完
				return None
			else:
				return self.DFA_status[status]['break']
		elif status == 2:
			if nextword.isdigit() or nextword== '.':
				return None
			else:
				return self.DFA_status[status]['break']
		elif status == 3: # 小数
			if nextword.isdigit():
				return None
			elif nextword == '.':
				return "ERROR"
			else:
				return self.DFA_status[status]['break']
		elif status == 4:
			if nextword == "*": #乘方
				return None
			else:
				return self.DFA_status[status]['break']
		elif status == 6:
			if nextword == "/": #注释
				return None
			else:
				return self.DFA_status[status]['break']
		elif status == 7:
			if nextword == '-': #注释
				return None
			else:
				return self.DFA_status[status]['break']
		elif status == 14:
			if nextword.isdigit() or nextword == '.':
				return "ERROR" #数字错误
			else:
				return None
		else:
			return None

	#分析
	def Parse(self, buffer):
		result = 1 # 分析结果
		status = 0 # 初态
		word = "" # 当前字符
		token_list = []
		buffer = buffer.strip() + " " #补充一多余字符
		if buffer is None:
			return
		for ch in buffer:
			#用当前ch判断下一字符的状态转移，少一个
			token_type = self.isFinal(status,ch)
			if token_type is not None:
				if token_type == 'ERROR':
					result = 0
					status = 14
					word += ch
					continue
				elif token_type == 'ID':
					tmp = self.getWord(word)
					token_list.append(tmp)
					if tmp[0] == "Word Error":
						result = 0
				elif token_type == 'CONST_ID':
					token_list.append(Token('CONST_ID',float(word),None))
				elif token_type == 'COMMENT':# 遇到注释直接返回
					return token_list, result
				else:
					token_list.append(Token(token_type,word,None))
				word = ""
				status = 0 # 回归初态
			if status == 14: 
				token_list.append(Token("Digit Error",word,None))
				word = ""
				status = 0
			if ch.isspace():# 跳过空格
				continue
			if ch in self.special:# 特殊符号
				status = self.move(status, ch)
			elif ch.isdigit():# 数字
				status = self.move(status,'digit')
			elif ch.isalpha():# 单词
				status = self.move(status,'letter')
			word += ch
		return token_list, result

	# 扫描文件读取数据
	def scanFile(self,buffer = " "):
		Tokens_list = []
		with open(self.filename, 'r', encoding='UTF-8') as source:
			line = 1
			while 1:
				buffer = source.readline().upper()
				if buffer is not "":
					Tokens_list.append(LINETOKEN(line,self.Parse(buffer)))
				else:
					break
				line+=1
		return Tokens_list

if __name__ == '__main__':
	file_name = input("Input source file:")
	scanner = lexScanner(file_name)
	tokens_list = scanner.scanFile()
	print(tokens_list)
	for tokens in tokens_list:
		if len(tokens.Tokens) > 0:
			print("line {}".format(tokens.LineNo))
			if tokens.Tokens[1] == 0:
				print("analysis failed.")
			for token in tokens.Tokens[0]:
				print(token)