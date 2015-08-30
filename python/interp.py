from parser import *

OPERAND_L	= 0
OPERATOR 	= 1
OPERAND_R	= 2

class Interpreter(object):

	class Memory(object):
		def __init__(self):
			self.instr 	= []
			self.stack	= []
			self.heap 	= {}	

	def __init__(self):
		self.parser 		= Parser(Doubletalk(), 'test.dtk')
		self.lang			= self.parser.lang
		self.memory			= Interpreter.Memory()
		self.ctrl_stack		= [True]
		self.block_stack	= ['<main>']
		self.pntr 			= 0

	def load(self):
	
		while True:
			instr = self.parser.parse()
			
			if instr is False or instr is None:
				return False

			#build grammar tree
			gtree = self.parser.build(instr)
			
			# append to instruction memory block
			self.memory.instr.append(gtree)
		
	def execute(self):

		try:
			# debugging
			print 'Pntr %s %s' % ('\t'*2, self.pntr)
			print 'Block %s %s' % ('\t'*2, self.block_stack)
			print 'Heap %s %s' % ('\t'*2, self.memory.heap)
			print 'Stack %s %s' % ('\t'*2, self.memory.stack)
			print 'Read %s %s' % ('\t'*2, self.ctrl_stack)
			print 'Instruction is %s %s' % ('\t'*1, self.memory.instr[self.pntr])
			
			print '-'*80
			# eval the instructions	
			r = self.eval(self.memory.instr[self.pntr])
		

		except IndexError as ie:
			return False
		self.pntr += 1
		return r


	def goto(self, n):
		self.pntr = n;
	
	def move(self, i):
		self.pntr += i
	
	def call(self, identifier, **kwargs):
		print 'Calling procedure %s' % (identifier)
		# push func call to stack
		self.stack_push({'ret_addr': self.pntr, 'kwargs': kwargs})
		# enable reading func block
		self.push_read_enabled(True)
		self.push_block('<proc>')
		self.goto(self.memory.heap[identifier])
	
	def endblock(self):
		self.pull_read_enabled()
		self.pull_block()
		
	def endproc(self):
		if self.is_read_enabled():
			stack = self.stack_pull()
			ret_addr = stack.get('ret_addr', None)
		
			if ret_addr is None:
				raise Exception('Return address missing')
		
			self.endblock()
			self.goto(ret_addr)	
		else:
			self.endblock()	
			
	def endif(self):
		self.endblock()
		
	def block(self):
		return self.block_stack[-1]
	
	def push_block(self, block):
		self.block_stack.append(block)
	
	def pull_block(self):
		return self.block_stack.pop()
	
	def stack(self):
		return self.memory.stack[-1]
	
	def stack_push(self, v):
		self.memory.stack.append(v)
	
	def stack_pull(self):
		return self.memory.stack.pop()
	
	def is_read_enabled(self):
		return self.ctrl_stack[-1]
	
	def toggle_read_enabled(self):
		# if parent block isn't executable, child blocks aren't neither
		if not self.ctrl_stack[-1:][0]: 
			self.ctrl_stack[-1] = False
		else:
			self.ctrl_stack[-1] = not self.ctrl_stack[-1]
		
	def push_read_enabled(self, boolean):
		# if parent block isn't executable, child blocks aren't neither
		if not self.is_read_enabled():
			self.ctrl_stack.append(False)
		else:
			self.ctrl_stack.append(boolean)
	
	def pull_read_enabled(self):
		return self.ctrl_stack.pop()
	
	def getval(self, i, **kwargs):

		# it's nested
		if isinstance(i, list):	
			return self.getval(i.pop(), **kwargs)
		# identifiers
		if isinstance(i, self.lang.Identifier):
			
			# return memory address identifier
			if kwargs.get('ref', None) is not None:
				return i
			# return value in memory
			else:
				return i.eval(self.memory.heap)
		# constants
		elif isinstance(i, self.lang.Constant):
			return i.eval()
		# a value
		else:
			return i
	
	def eval(self, i):
	
		if isinstance(i, list):
			
			# a control struct
			if isinstance(i[OPERAND_L], self.lang.Control):
				return i[OPERAND_L].eval(self, i[1:])
		
			if not self.is_read_enabled():
				return None
			
			# a keyword
			if isinstance(i[OPERAND_L], self.lang.Keyword):
				return i[OPERAND_L].eval(self, i[1:])
	
			# expressions
			for k,v in enumerate(i):
				if isinstance(v, list):
					i[k] = self.eval(v)
										
			# a value
			if len(i) < 2:
				return i.pop()
			
			# assign operations
			if isinstance(i[OPERATOR], self.lang.Assign):
				return i[OPERATOR].eval(i[OPERAND_L], self.getval(i[OPERAND_R]), self.memory.heap)
			# any other binary operation
			else:
				return i[OPERATOR].eval(self.getval(i[OPERAND_L]), self.getval(i[OPERAND_R]), self.memory.heap)
				
		else:
			return i
