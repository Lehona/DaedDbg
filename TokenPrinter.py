import gdb
import struct
import sys
import os

sys.path.append(os.getcwd())
from CodeStackHelpers import *
from SymbTableHelpers import *

	
def PrintCurrTokens(amount):
	PrintTokens(GetCurrParserStackPtr(), amount)
	
def PrintToken(tok, param, offset, is_current=False):
	global TokenNames
	offsetStr = '0x%06x' % offset

	if is_current:
		prefix = " => "
	else:
		prefix = "    "
	
	if param is None:
		print(offsetStr + prefix + TokenNames[tok])
	else:
		if ParamIsSymbol(tok):
			paramStr = GetSymbTable()[int(param)].name
		elif tok == zPAR_TOK_CALL:
			paramStr = GetSymbTable()[GetFuncIdByOffset(param)].name
		else:
			paramStr = uhex(param)
		print(offsetStr + prefix + "{0: <20}".format(TokenNames[tok]) + paramStr)

def PrintTokens(ptr, amount):
	currentPtr = GetCurrParserStackPtr()
	stackBegin = GetParserStackPtr()
	for i in range(amount):
		offset = ptr - stackBegin
		isCurrent = (ptr == currentPtr)
		param = None
		token = ReadByte(ptr)
		ptr += 1
		if RequiresParameter(token):
			param = ReadInt(ptr)
			ptr += 4
		PrintToken(token, param, offset, isCurrent)
			
def PrintTokensOffset(offset, amount):
	PrintTokens(GetParserStackPtr()+offset, amount)
	
def RequiresParameter(tok):
	if (tok == zPAR_TOK_CALL      or tok == zPAR_TOK_CALLEXTERN) \
	or (tok == zPAR_TOK_PUSHINT   or tok == zPAR_TOK_PUSHVAR) \
	or (tok == zPAR_TOK_PUSHINST  or tok == zPAR_TOK_SETINSTANCE) \
	or (tok == zPAR_TOK_JUMP      or tok == zPAR_TOK_JUMPF) \
	or (tok == zPAR_TOK_PUSH_ARRAYVAR):
		return True
	return False
	
def ParamIsSymbol(tok):
	if (tok == zPAR_TOK_SETINSTANCE 		or tok == zPAR_TOK_CALLEXTERN) \
	or (tok == zPAR_TOK_PUSHVAR 	or tok == zPAR_TOK_PUSHINST):
		return True
	return False