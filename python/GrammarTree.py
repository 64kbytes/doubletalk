class GrammarTree(object):
	def __init__(self):
		self.sentence 	= [] 

	def _up(self):
		pass

	def _down(self):
		pass

	def hint(self, sentence):
		for s in sentence:
			if s in self.syntax:
				print s

	def last(self):
		pass

	def get(self):
		return self.sentence;

	def __len__(self):
		return len(sentence)

	def clear(self):
		pass