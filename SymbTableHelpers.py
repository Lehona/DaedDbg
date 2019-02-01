import gdb
import sys
import os

sys.path.append(os.getcwd())
from CodeStackHelpers import *
from SortedCollection import *

def GetSymbolByIndexFromGothic(index):
	return zCPar_Symbol(ReadInt(GetSymbTablePtr()+4*index))
	

def ReadZString(ptr):
	charPtr = ReadInt(ptr + 8)
	length = ReadInt(ptr + 12)
	return ReadString(charPtr, length)
	
	
zCPar_Symbol_bitfield_ele         = ((1 << 12) - 1) <<  0
zCPar_Symbol_bitfield_type        = ((1 <<  4) - 1) << 12
zCPar_Symbol_bitfield_flags       = ((1 <<  6) - 1) << 16
zCPar_Symbol_bitfield_space       = ((1 <<  1) - 1) << 22

zPAR_TYPE_VOID        = 0 << 12
zPAR_TYPE_FLOAT       = 1 << 12
zPAR_TYPE_INT         = 2 << 12
zPAR_TYPE_STRING      = 3 << 12
zPAR_TYPE_CLASS       = 4 << 12
zPAR_TYPE_FUNC        = 5 << 12
zPAR_TYPE_PROTOTYPE   = 6 << 12
zPAR_TYPE_INSTANCE    = 7 << 12

        
zPAR_FLAG_CONST       =  1 << 16
zPAR_FLAG_RETURN      =  2 << 16
zPAR_FLAG_CLASSVAR    =  4 << 16
zPAR_FLAG_EXTERNAL    =  8 << 16
zPAR_FLAG_MERGED      = 16 << 16
class zCPar_Symbol():
	def __init__(self, ptr):
		self.name = ReadZString(ptr)
		self.content = ReadInt(ptr + 0x18)
		self.offset = ReadInt(ptr + 0x1C)
		self.bitfield = ReadInt(ptr + 0x20)
		self.parent = ReadInt(ptr + 0x38)
		
		
	def GetType(self):
		return self.bitfield & zCPar_Symbol_bitfield_type
		
	def GetFlags(self):
		return self.bitfield & zCPar_Symbol_bitfield_flags
		
	def IsFunc(self):
		return (self.GetType() & zCPar_Symbol_bitfield_type) == zPAR_TYPE_FUNC
		
	def IsDaedalusFunc(self):
		return self.IsFunc() \
			and not (self.GetFlags() & zPAR_FLAG_EXTERNAL == zPAR_FLAG_EXTERNAL) \
			and (self.GetFlags() & zPAR_FLAG_CONST == zPAR_FLAG_CONST)
		
	def IsExternal(self):
		return self.IsFunc() and (self.GetFlags() & zPAR_FLAG_EXTERNAL == zPAR_FLAG_EXTERNAL)
		
	def __repr__(self):
		return self.name


# Preprocess all Gothic symbols into Python zCPar_Symbols	
def InitSymbTable():
	global SymbTable
	SymbTable = []
	for i in range(GetSymbTableLength()):
		SymbTable.append(GetSymbolByIndexFromGothic(i))
		
def GetSymbTable():
	global SymbTable
	if len(SymbTable) == 0:
		InitSymbTable()
		
	return SymbTable
		
# List of all functions (for faster searching)
def InitFuncList():
	global FuncIdList, SymbTable
	FuncIdList = SortedCollection(key=lambda id: SymbTable[id].content)
	for i in range(GetSymbTableLength()):
		if SymbTable[i].IsDaedalusFunc():
			FuncIdList.insert(i)
		
def GetFuncIdByOffset(offset):
	global SymbTable, FuncIdList
	try:
		return FuncIdList.find_le(offset)
	except ValueError: # Value not found - happens with hook etc., generally any code that was constructed at runtime
		return None

		
def PrintFuncNameByOffset(offset):
	id = GetFuncIdByOffset(offset)
	print(SymbTable[id].name)
	
def PrintCurrFuncName():
	offset = GetCurrParserStackOffset()
	PrintFuncNameByOffset(offset)