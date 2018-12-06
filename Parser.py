# coding=utf-8
#from Lexer import Scanner
from LexScan import lexScanner
from LexScan import Token
from collections import defaultdict

# 错误信息
class ErrorMessage(Exception):
    def __init__(self,message_code,error_word,line):
        #语法错误
        if message_code == 1:
            self.error_message = "line {}: Error token {} type in this".format(line,error_word)
        #词法错误
        if message_code == 2:
            self.error_message = "line {}: Error token {} in this".format(line,error_word)
        #结束符错误（语法错误）
        if message_code == 3:
            self.error_message = "line {}: Terminator exception".format(line)

    def __repr__(self):
        return self.error_message

# 空行
class Emptyline(Exception):
    def __init__(self,line):
        self.message = "line {} is empty".format(line)

    def __repr__(self):
        return self.message

# 节点
class ExprNode:
    def __init__(self,token_type):
        self.child_number = 0
        self.TokenType = token_type
        self.left_child = None
        self.right_child = None

    def set_content(self,content):
        self.content = content

    #0代表无、1代表左、2代表右、3代表都有
    def set_left_child(self,left_child):
        self.child_number += 1
        self.left_child = left_child

    def set_right_child(self,right_child):
        self.child_number += 2
        self.right_child = right_child

    def get_left_child(self):
        if self.child_number == 1 or self.child_number == 3:
            return self.left_child
        else:
            return None

    def get_right_child(self):
        if self.child_number == 2 or self.child_number == 3:
            return self.right_child
        else:
            return None

# 总解释器、包含打印树
class Parser:
    def __init__(self,filename):
        # 启动后进行词法分析，获得Tokens_list
        self.scanner = lexScanner(filename)
        self.Tokens_list = self.scanner.scanFile()
        self.paramters = [] #一个盛有数个字典的列表
        self.resultDict = defaultdict(str)
        #默认值
        self.resultDict2 = defaultdict(list,{'for_start':[], 'for_end':[], 'for_step':[], 'start_x':[], 'start_y':[], 'origin_x':[], 'origin_y':[], 'rot_angele':[], 'scale_x':[], 'scale_y':[]})
        
    # 分析主函数
    def parser_program(self):
        # 对Tokens_list里的每行进行语法分析，得到parameters
        while(self.Tokens_list):
            Token_list = self.Tokens_list.pop(0)
            try:
                line_parser = LineParser(Token_list.Tokens[0],Token_list.LineNo)
                line_parser.parser()
                self.paramters.append(line_parser.parameter)
            except Emptyline:
                continue
    
    #打印树
    def traceTree(self,treeRoot,space_count): #defaultdict
        #该节点分析
        if treeRoot.TokenType == "PLUS":
            print("\t"*space_count+"+")
        elif treeRoot.TokenType == "MINUS":
            print("\t"*space_count+"-")
        elif treeRoot.TokenType == "MULTIPLICATION":
            print("\t"*space_count+"*")
        elif treeRoot.TokenType == "DIVISION":
            print("\t"*space_count+"/")
        elif treeRoot.TokenType == "POWER":
            print("\t"*space_count+"**")
        elif treeRoot.TokenType == "FUNC":
            print("\t"*space_count+str(treeRoot.content))
        elif treeRoot.TokenType == "CONST_ID":
            print("\t"*space_count+str(treeRoot.content))
        elif treeRoot.TokenType == "T":
            print("\t"*space_count+"T")
        else:
            print("\t"*space_count+"Error node!")
        #子节点分析
        if treeRoot.TokenType == "CONST_ID" or treeRoot.TokenType == "T":
            return
        #有函数
        elif treeRoot.TokenType == "FUNC":
            self.traceTree(treeRoot.get_left_child(), space_count+1)
        #有算式
        else:
            self.traceTree(treeRoot.get_left_child(), space_count+1)
            self.traceTree(treeRoot.get_right_child(), space_count+1)
    
    # 整理结果
    def getResultDict(self):
        for paramter in self.paramters:
            for key in paramter.keys(): #对一组树进行打印
                self.resultDict[key] = paramter[key]

    # 打印四棵树
    def Print_result(self):
        for key in self.resultDict:
            print("the {} expr tree is :".format(key))
            self.traceTree(self.resultDict[key],0)

    #最终字典处理
    def final_result(self):
        for key in self.resultDict:
            self.traceTree2(key, self.resultDict[key])

    def traceTree2(self,key,treeRoot): #defaultdict
        #该节点分析  
        if treeRoot.TokenType == "PLUS":
            self.resultDict2[key].append("+")
        elif treeRoot.TokenType == "MINUS":
            self.resultDict2[key].append("-")
        elif treeRoot.TokenType == "MULTIPLICATION":
            self.resultDict2[key].append("*")
        elif treeRoot.TokenType == "DIVISION":
            self.resultDict2[key].append("/")
        elif treeRoot.TokenType == "POWER":
            self.resultDict2[key].append("**")
        elif treeRoot.TokenType == "FUNC":
            self.resultDict2[key].append(treeRoot.content)
        elif treeRoot.TokenType == "CONST_ID":
            self.resultDict2[key].append(treeRoot.content)
        elif treeRoot.TokenType == "T":
            self.resultDict2[key].append("T")
        else:
            self.resultDict2[key].append("Error node!")
        if treeRoot.TokenType == "CONST_ID" or treeRoot.TokenType == "T":
            return
        elif treeRoot.TokenType == "FUNC":
            self.traceTree2(key,treeRoot.get_left_child())
        else:
            self.traceTree2(key,treeRoot.get_left_child())
            self.traceTree2(key,treeRoot.get_right_child())

# 行解释器
class LineParser:
    def __init__(self,Token_list,line):
        self.T = 0.0
        self.token_list = Token_list
        self.parameter = {}
        self.token = None
        self.line = line
        self.end_judge()

    # 判断结束符是否正常，判断空行
    def end_judge(self):
        if len(self.token_list) == 0:
            raise Emptyline(self.line)
        if self.token_list[-1].type == "SEMICO":
            del(self.token_list[-1])
            if self.token_list[-1].type == "SEMICO":
                raise ErrorMessage(3,None,self.line)
            else:
                return True
        else:
            raise ErrorMessage(3,None,self.line)

    #令self.token获取self.token_list的一个token
    def get_token(self):
        if len(self.token_list):
            self.token = self.token_list.pop(0)
            if "Error" in self.token.type: #词法错误
                raise ErrorMessage(2,self.token.value,self.line)
        else:
            self.token = Token("NoneToken",None,None)

    #与目标类型匹配，成功则触发get_token()，失败返回错误1
    def match_token(self,aimed):
        if self.token.type == aimed:
            self.get_token()
            return True
        else:
            raise ErrorMessage(1,self.token.value,self.line)

    #主方法
    def parser(self):
        self.get_token()
        self.pargram()

    #语法分析
    def pargram(self):
        while(self.token.type != "NoneToken"):
            self.Statement()
            if self.token.type=="NoneToken":
                break

    #看是哪种关键字，都不是报错误1
    def Statement(self):
        if self.token.type == "ORIGIN":
            self.OriginStatement()
        elif self.token.type == "ROT":
            self.RotStatement()  
        elif self.token.type == "SCALE":
            self.ScaleStatement()
        elif self.token.type == "FOR":
            self.ForStatement()
        else:
            raise ErrorMessage(1,self.token.value,self.line)

    #4个关键字对应自身的结构，去match_token寻找所需
    def OriginStatement(self):
        self.match_token("ORIGIN")
        self.match_token("IS")
        self.match_token("L_BRACKET")
        
        origin_x = self.Expression()
        self.parameter['origin_x'] = origin_x
        self.match_token("COMMA")

        origin_y = self.Expression()
        self.parameter['origin_y'] = origin_y
        self.match_token("R_BRACKET")

    def RotStatement(self):
        self.match_token("ROT")
        self.match_token("IS")
       
        rot_angle = self.Expression()
        self.parameter['rot_angele'] = rot_angle

    def ScaleStatement(self):
        self.match_token("SCALE")
        self.match_token("IS")
        self.match_token("L_BRACKET")
        
        scale_x = self.Expression()
        self.parameter['scale_x'] = scale_x
        self.match_token("COMMA")
        
        scale_y = self.Expression()
        self.parameter['scale_y']  = scale_y
        self.match_token("R_BRACKET")
        
    def ForStatement(self):
        self.match_token("FOR")
        self.match_token("T")
        self.match_token("FROM")
        
        # for start
        start = self.Expression()
        self.parameter['for_start'] = start
        self.match_token("TO")
        
        # for end
        end = self.Expression()
        self.parameter['for_end'] = end
        self.match_token("STEP")
    
        step = self.Expression()
        self.parameter['for_step'] = step

        self.match_token("DRAW")
        self.match_token("L_BRACKET")

        start_x = self.Expression()
        self.parameter['start_x'] = start_x
        self.match_token("COMMA")

        start_y = self.Expression()
        self.parameter['start_y'] = start_y
        self.match_token("R_BRACKET")

    #优先级排序：Expression、Term、Factor、Component、Atom
    def Expression(self):
        left = None
        right = None
        temp_type = None
        left = self.Term()
        #消除左递归
        while(self.token.type == "PLUS" or self.token.type == "MINUS"):
            temp_type = self.token.type
            self.match_token(temp_type)
            #将Term拼在Expression'前
            right = self.Term()
            left = self.make_expr_node(temp_type,None,left,right)
        # self.get_token()
        return left

    def Term(self):
        left = self.Factory()
        #消除左递归
        while(self.token.type == "MULTIPLICATION" or self.token.type == "DIVISION"):
            tmp_type = self.token.type
            self.match_token(tmp_type)
            #将Factor拼在Term'前
            right = self.Factory()
            left = self.make_expr_node(tmp_type,None,left,right)
        return left

    def Factory(self):
        left = ExprNode(None)
        right = ExprNode(None)
        if self.token.type == "PLUS":
            self.match_token("PLUS")
            right = self.Factory()
        elif self.token.type == "MINUS":
            self.match_token("MINUS")
            right = self.Factory()
            left.TokenType = "CONST_ID"
            left.set_content(0.0)
            right = self.make_expr_node("MINUS",None,left,right)
        else:
            right = self.Component()
        return right

    def Component(self):
        right = ExprNode(None)
        left = self.Atom()
        if self.token.type == "POWER":
            self.match_token("POWER")
            right = self.Component()
            left = self.make_expr_node("POWER",None,left,right)
        return left
    
    #原子表达式，错误则返回错误1
    def Atom(self):
        address = ExprNode(None)
        tmp = ExprNode(None)
        if self.token.type == "CONST_ID":
            tmp_token = self.token
            self.match_token("CONST_ID")
            address = self.make_expr_node("CONST_ID",tmp_token.value)
        elif self.token.type == "T":
            self.match_token("T")
            address = self.make_expr_node("T")
        elif self.token.type == "FUNC":
            tmp_token = self.token
            self.match_token("FUNC")
            self.match_token("L_BRACKET")
            tmp = self.Expression()
            address = self.make_expr_node("FUNC",tmp_token.function,tmp)
            self.match_token("R_BRACKET")
        elif self.token.type == "L_BRACKET":
            self.match_token("L_BRACKET")
            address = self.Expression()
            self.match_token("R_BRACKET")
        else:
            raise ErrorMessage(1,self.token.value,self.line)
        return address
    
    #根据需要创建子节点
    def make_expr_node(self,token_type,token_value = None,left_child = None,right_child =None):
        node = ExprNode(token_type)
        if node.TokenType == "CONST_ID":
            node.set_content(token_value)
        elif node.TokenType == "T":
            node.set_content(self.T)
        elif node.TokenType == "FUNC":
            node.set_content(token_value)
            node.set_left_child(left_child)
        else:
            node.set_left_child(left_child)
            node.set_right_child(right_child)
        return node

# 插入节点
def InsertNode(NowNode,value):
    newNode = ExprNode('int')
    newNode.set_content(value)
    if newNode.content < NowNode.content:
        NowNode.set_left_child(newNode)
    else:
        NowNode.set_right_child(newNode)

# 寻找插入位置
def FindInsertPosition(root,value):
    node = root
    while(node.child_number):
        if node.child_number == 3:
            if value < node.content:
                node = node.get_left_child()
                continue
            else:
                node = node.get_right_child()
                continue
        elif node.child_number == 1:
            if value < node.content:
                node = node.get_left_child()
                continue
            else:
                break
        elif node.child_number == 2:
            if value < node.content:
                break
            else:
                node = node.get_right_child()
                continue
    return node

# 生成树
def CreateTree(value_list):
    root = ExprNode('int')
    root.set_content(value_list[0])
    for value in value_list[1:]:
        node = FindInsertPosition(root,value)
        InsertNode(node,value)
    return root