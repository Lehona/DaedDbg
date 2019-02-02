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

	print("Sucessfully installed Breakpoint for Instruction Decoding. Continuing now to the first instruction.")
	CurrentMode = Modes.StepInto
	
def InitGlobals():
	global BreakpointList, InternalBreakpoints, CurrentMode, CurrentFuncId
	BreakpointList = []
	InternalBreakpoints = []
	CurrentMode = Modes.Nothing
	CurrentFuncId = None
	InitSymbTable()
	InitFuncList()
	InitSymbNameList()
	
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
	"""This command adds a daedalus breakpoint. Supports offset qualified with * and function names"""
	
	def __init__ (self):
		super (BreakCmd, self).__init__("dbreak", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		if args.startswith("*"):
			if "0x" in args:
				offset = int(args[1:], 16)
			else:
				offset = int(args[1:])
		else: 
			upper = args.strip().upper()
			
			# This has to be one of the weirdest bugs I have ever encountered
			# For some reason GetSymbIdByName fails to find functions that begin with a Z when called here
			# But when calling it from python directly, e.g. 'python print(GetSymbIdByName("ZS_GHOST"))'
			# it works perfectly fine. Even looking at the byte arrays of the string passed as argument
			# and a hardcoded string returns the same bytes. However, after a lot of trial and error
			# just calling str() on it fixes the issue and I get my sanity back.
			symbID = GetSymbIdByName(str(upper))
			Debug("Looking for symbol |" + upper + "| and found ID: " + str(symbID))
			offset = GetSymbTable()[symbID].content
			Debug("Found offset: " + str(offset))
		BreakpointList.append(offset)
		
		print("Installed breakpoint with ID " + str(len(BreakpointList)-1) + " at offset " + uhex(offset) + " in function " + GetFuncNameByOffset(offset))
		
BreakCmd()


class ShowBreaksCmd(gdb.Command):
	"""Prints all currently active daedalus breakpoints and in which function they are installed"""
	
	def __init__ (self):
		super (ShowBreaksCmd, self).__init__("dibreaks", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		ctr = 0
		# TODO: Formatting
		for bp in BreakpointList:
			print(str(ctr) + " " + GetFuncNameByOffset(bp) + " " + uhex(bp))
			ctr += 1
		
ShowBreaksCmd()

class PrintCurrentFunctionCmd(gdb.Command):
	"""Prints the currently executed daedalus function"""
	
	def __init__ (self):
		super (PrintCurrentFunctionCmd, self).__init__("dcurrentfunc", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		PrintCurrFuncName()
		
PrintCurrentFunctionCmd()

class ExamineVariableCmd(gdb.Command):
	"""Prints the value of a daedalus variable"""
	
	def __init__ (self):
		super (ExamineVariableCmd, self).__init__("dx", gdb.COMMAND_OBSCURE)

	def invoke(slf, args, from_tty):
		id = GetSymbIdByName(args.upper())
		print(GetSymbTable()[id].content)
		
ExamineVariableCmd()
 
 
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
			
		
		# DISABLED FOR NOW (SHOULD WORK FINE)
		# Step over instructions that were not in the original codestack
		# if currOffset > GetParserStackSize() or currOffset < 0:
			# Debug("Hit BP for instruction outside of codestack")
			# return False
			
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
	