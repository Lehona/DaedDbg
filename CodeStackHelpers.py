import gdb
import struct

DoDebug = False

def Debug(string):
	global DoDebug
	if DoDebug:
		print(string)
		

def uhex(nr):
	return "0x%x" % (nr & 0xffffffff)


def ReadByte(ptr):
	buffer = gdb.selected_inferior().read_memory(ptr, 1)
	result = struct.unpack('b', buffer)[0]
	return result & 0xFF
	
def ReadInt(ptr):
	buffer = gdb.selected_inferior().read_memory(ptr, 4)
	result = struct.unpack('l', buffer)[0]
	return result	

def ReadString(ptr, length):
	buffer = gdb.selected_inferior().read_memory(ptr, length)
	result = str(buffer)
	return result
	
	
def GetParserPtr():
	return 11223232
	
def GetSymbTablePtr():
	return ReadInt(GetParserPtr() + 24)
	
def GetSymbTableLength():
	return ReadInt(GetParserPtr() + 24 + 8)
	
def GetSortedSymbTablePtr():
	return ReadInt(GetParserPtr() + 36)

def GetParserStackPtr():
	return ReadInt(GetParserPtr() + 72)

# Points to the current stack position	
def GetCurrParserStackPtr():
	return ReadInt(GetParserPtr() + 76)

def GetParserStackLastPtr():
	return ReadInt(GetParserPtr() + 80)
	
def GetParserStackSize():
	return GetParserStackLastPtr() - GetParserStackPtr()
	
	
def GetCurrParserStackOffset():
	return GetCurrParserStackPtr() - GetParserStackPtr()
	

	

TokenNames = [None] * 246
TokenNames[0] = "zPAR_OP_PLUS"
TokenNames[1] = "zPAR_OP_MINUS"
TokenNames[2] = "zPAR_OP_MUL"
TokenNames[3] = "zPAR_OP_DIV"
TokenNames[4] = "zPAR_OP_MOD"
TokenNames[5] = "zPAR_OP_OR"
TokenNames[6] = "zPAR_OP_AND"
TokenNames[7] = "zPAR_OP_LOWER"
TokenNames[8] = "zPAR_OP_HIGHER"

TokenNames[9] = "zPAR_OP_IS"
												   
TokenNames[11] = "zPAR_OP_LOG_OR"
TokenNames[12] = "zPAR_OP_LOG_AND"
TokenNames[13] = "zPAR_OP_SHIFTL"
TokenNames[14] = "zPAR_OP_SHIFTR"
TokenNames[15] = "zPAR_OP_LOWER_EQ"
TokenNames[16] = "zPAR_OP_EQUAL"
TokenNames[17] = "zPAR_OP_NOTEQUAL"
TokenNames[18] = "zPAR_OP_HIGHER_EQ"
TokenNames[19] = "zPAR_OP_ISPLUS"
TokenNames[20] = "zPAR_OP_ISMINUS"
TokenNames[21] = "zPAR_OP_ISMUL"
TokenNames[22] = "zPAR_OP_ISDIV"

TokenNames[30] = "zPAR_OP_UNARY"
TokenNames[30] = "zPAR_OP_UN_PLUS"
TokenNames[31] = "zPAR_OP_UN_MINUS"
TokenNames[32] = "zPAR_OP_UN_NOT"
TokenNames[33] = "zPAR_OP_UN_NEG"
TokenNames[33] = "zPAR_OP_MAX"

TokenNames[40] = "zPAR_TOK_BRACKETON"
TokenNames[41] = "zPAR_TOK_BRACKETOFF"
TokenNames[42] = "zPAR_TOK_SEMIKOLON"
TokenNames[43] = "zPAR_TOK_KOMMA"
TokenNames[44] = "zPAR_TOK_SCHWEIF"
TokenNames[45] = "zPAR_TOK_NONE"

TokenNames[51] = "zPAR_TOK_FLOAT"
TokenNames[52] = "zPAR_TOK_VAR"
TokenNames[53] = "zPAR_TOK_OPERATOR"


TokenNames[60] = "zPAR_TOK_RET"
TokenNames[61] = "zPAR_TOK_CALL"
TokenNames[62] = "zPAR_TOK_CALLEXTERN"
TokenNames[63] = "zPAR_TOK_POPINT"
TokenNames[64] = "zPAR_TOK_PUSHINT"
TokenNames[65] = "zPAR_TOK_PUSHVAR"
TokenNames[66] = "zPAR_TOK_PUSHSTR"
TokenNames[67] = "zPAR_TOK_PUSHINST"
TokenNames[68] = "zPAR_TOK_PUSHINDEX"
TokenNames[69] = "zPAR_TOK_POPVAR"
TokenNames[70] = "zPAR_TOK_ASSIGNSTR"
TokenNames[71] = "zPAR_TOK_ASSIGNSTRP"
TokenNames[72] = "zPAR_TOK_ASSIGNFUNC"
TokenNames[73] = "zPAR_TOK_ASSIGNFLOAT"
TokenNames[74] = "zPAR_TOK_ASSIGNINST"
TokenNames[75] = "zPAR_TOK_JUMP"
TokenNames[76] = "zPAR_TOK_JUMPF"

TokenNames[80] = "zPAR_TOK_SETINSTANCE"

TokenNames[90] = "zPAR_TOK_SKIP"
TokenNames[91] = "zPAR_TOK_LABEL"
TokenNames[92] = "zPAR_TOK_FUNC"
TokenNames[93] = "zPAR_TOK_FUNCEND"
TokenNames[94] = "zPAR_TOK_CLASS"
TokenNames[95] = "zPAR_TOK_CLASSEND"
TokenNames[96] = "zPAR_TOK_INSTANCE"
TokenNames[97] = "zPAR_TOK_INSTANCEEND"
TokenNames[98] = "zPAR_TOK_NEWSTRING"
TokenNames[180] = "zPAR_TOK_FLAGARRAY" 
TokenNames[245] = "zPAR_TOK_PUSH_ARRAYVAR"
		
zPAR_OP_PLUS = 0
zPAR_OP_MINUS = 1
zPAR_OP_MUL = 2
zPAR_OP_DIV = 3
zPAR_OP_MOD = 4
zPAR_OP_OR = 5
zPAR_OP_AND = 6
zPAR_OP_LOWER = 7
zPAR_OP_HIGHER = 8
zPAR_OP_IS = 9
zPAR_OP_LOG_OR = 11
zPAR_OP_LOG_AND = 12
zPAR_OP_SHIFTL = 13
zPAR_OP_SHIFTR = 14
zPAR_OP_LOWER_EQ = 15
zPAR_OP_EQUAL = 16
zPAR_OP_NOTEQUAL = 17
zPAR_OP_HIGHER_EQ = 18
zPAR_OP_ISPLUS = 19
zPAR_OP_ISMINUS = 20
zPAR_OP_ISMUL = 21
zPAR_OP_ISDIV = 22
zPAR_OP_UNARY = 30
zPAR_OP_UN_PLUS = 30
zPAR_OP_UN_MINUS = 31
zPAR_OP_UN_NOT = 32
zPAR_OP_UN_NEG = 33
zPAR_OP_MAX = 33
zPAR_TOK_BRACKETON = 40
zPAR_TOK_BRACKETOFF = 41
zPAR_TOK_SEMIKOLON = 42
zPAR_TOK_KOMMA = 43
zPAR_TOK_SCHWEIF = 44
zPAR_TOK_NONE = 45
zPAR_TOK_FLOAT = 51
zPAR_TOK_VAR = 52
zPAR_TOK_OPERATOR = 53
zPAR_TOK_RET = 60
zPAR_TOK_CALL = 61
zPAR_TOK_CALLEXTERN = 62
zPAR_TOK_POPINT = 63
zPAR_TOK_PUSHINT = 64
zPAR_TOK_PUSHVAR = 65
zPAR_TOK_PUSHSTR = 66
zPAR_TOK_PUSHINST = 67
zPAR_TOK_PUSHINDEX = 68
zPAR_TOK_POPVAR = 69
zPAR_TOK_ASSIGNSTR = 70
zPAR_TOK_ASSIGNSTRP = 71
zPAR_TOK_ASSIGNFUNC = 72
zPAR_TOK_ASSIGNFLOAT = 73
zPAR_TOK_ASSIGNINST = 74
zPAR_TOK_JUMP = 75
zPAR_TOK_JUMPF = 76
zPAR_TOK_SETINSTANCE = 80
zPAR_TOK_SKIP = 90
zPAR_TOK_LABEL = 91
zPAR_TOK_FUNC = 92
zPAR_TOK_FUNCEND = 93
zPAR_TOK_CLASS = 94
zPAR_TOK_CLASSEND = 95
zPAR_TOK_INSTANCE = 96
zPAR_TOK_INSTANCEEND = 97
zPAR_TOK_NEWSTRING = 98
zPAR_TOK_FLAGARRAY = 180
zPAR_TOK_PUSH_ARRAYVAR = 245