import gdb
import struct
import sys
import os

sys.path.append(os.getcwd())
from CodeStackHelpers import *
from SymbTableHelpers import *
from TokenPrinter import *


class Modes(object):
	StepInto = 1
	StepOver = 2
	StepReturn = 3
	WaitForInternal = 4
	Nothing = 5

def Main():	
	global CurrentMode
	InitGlobals()
	
	# Just before the next token is popped
	PopInstrEa = 0x791A9D
	
	DecoderBP = InstrDecoderBP("*" + hex(PopInstrEa))

	print("Sucessfully installed Breakpoint for Instruction Decoding. Continuing now to the first Instruction hit.")
	CurrentMode = Modes.StepInto
	
def InitGlobals():
	global BreakpointList, InternalBreakpoints, CurrentMode, CurrentFuncId
	BreakpointList = []
	InternalBreakpoints = []
	CurrentMode = Modes.Nothing
	CurrentFuncId = None
	InitSymbTable()
	InitFuncList()
	
class DaedalusStepPrefixCmd(gdb.Command):
	"""A prefix for all stepping commands of the DaedDbg gdb script"""

	def __init__ (self):
		super (DaedalusStepPrefixCmd, self).__init__("dstep", gdb.COMMAND_OBSCURE, prefix=True)

	def invoke(slf, args, from_tty):
		pass

DaedalusStepPrefixCmd()

	
class StepIntoCmd(gdb.Command):
	"""This command steps a single daedalus instruction and displays the current tokens"""
	
	def __init__ (self):
		super (StepIntoCmd, self).__init__("dstep into", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		global CurrentMode
		CurrentMode = Modes.StepInto
		gdb.execute("continue")
		
StepIntoCmd()
	
class StepOverCmd(gdb.Command):
	"""This command steps a single daedalus instruction and displays the current tokens"""
	
	def __init__ (self):
		super (StepOverCmd, self).__init__("dstep over", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		global CurrentMode, InternalBreakpoints
		CurrentMode = Modes.StepOver
		if GetNextToken() == zPAR_TOK_CALL:
			InternalBreakpoints.append(GetCurrParserStackOffset()+5)
			CurrentMode = Modes.WaitForInternal
		gdb.execute("continue")
		
StepOverCmd()	

class StepReturnCmd(gdb.Command):
	"""This command steps a single daedalus instruction and displays the current tokens"""
	
	def __init__ (self):
		super (StepReturnCmd, self).__init__("dstep return", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		global CurrentMode, CurrentFuncId 
		CurrentMode = Modes.StepReturn
		CurrentFunc = GetFuncIdByOffset(GetCurrParserStackOffset())
		gdb.execute("continue")
		
StepReturnCmd()

class BreakCmd(gdb.Command):
	"""This command adds a daedalus breakpoint. Currently only supports offsets"""
	
	def __init__ (self):
		super (BreakCmd, self).__init__("dbreak", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		if "0x" in args:
			offset = int(args, 16)
		else:
			offset = int(args)
		BreakpointList.append(offset)
		
BreakCmd()

class PrintCurrentFunctionCmd(gdb.Command):
	"""Prints the currently executed daedalus function"""
	
	def __init__ (self):
		super (PrintCurrentFunctionCmd, self).__init__("dcurrentfunc", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		PrintCurrFuncName()
		
PrintCurrentFunctionCmd()
 
 
class InstrDecoderBP(gdb.Breakpoint):
	def __init__(self, location):
		super(InstrDecoderBP, self).__init__(location)
		self.silent = True
		
	def stop(self):
		global BreakpointList, CurrentMode, CurrentFuncId
		
		# Only do anything if we're dealing with the content parser
		if ECX() != (GetParserPtr() + 72):
			return False
			
		currOffset = GetCurrParserStackOffset()
			
		# Step over instructions that were not in the original codestack
		if currOffset > GetParserStackSize() or currOffset < 0:
			Debug("Hit BP for instruction outside of codestack")
			return False
			
		InstrByte = GetNextToken()
					
		
		DoBreak = False
		# TODO LOTS OF THINGS
		if currOffset in BreakpointList:
			print("Hit a breakpoint!")
			DoBreak = True
			
		if currOffset in InternalBreakpoints:
			Debug("Hit an internal breakpoint!")
			DoBreak = True
			InternalBreakpoints.remove(currOffset)
			
		if CurrentMode == Modes.StepInto or CurrentMode == Modes.StepOver: 
			DoBreak = True
			
		
		# This should stop _before_ the return is executed. I might want to step a single token further, 
		# but this would cause issues with functions that don't have a daedalus parent (i.e. are called by the engine)
		if CurrentMode == Modes.StepReturn:
			if GetFuncIdByOffset(currOffset) == CurrentFuncId and InstrByte == zPAR_TOK_RET:
				return True
			else: 
				return False
			
		if DoBreak:
			PrintCurrTokens(6)
			
		CurrentMode = Modes.Nothing
		return DoBreak

# Only works correctly during the DaedDbg-BP!		
def GetNextToken():
	return ReadByte(GetCurrParserStackPtr())
		
def EAX():
	return int(str(gdb.parse_and_eval("$eax")))
	
def ECX():
	return int(str(gdb.parse_and_eval("$ecx")))
	
	
Main()	
	