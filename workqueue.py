#!/usr/bin/python

from threading import Thread
from Queue import Queue

class WorkQueue:
	def __init__(self, processor, num_workers=8, max_queue_size=50):
		self.queue = Queue(max_queue_size);
		self.threads = []
		self.processor = processor

		for i in range(0, num_workers):
			thread = Thread(target=self.threadfunc)
			thread.daemon = True
			self.threads.append(thread)
			thread.start()
			
	def threadfunc(self):
		while True:
			job = self.queue.get()
			self.processor(job)
			self.queue.task_done()


	def done(self):
		self.queue.join()

	def add(self, job):
		self.queue.put(job)

