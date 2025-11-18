import requests, json
from .util import Basic
from .config import config

class Runner(Basic):
	def __init__(self, name, config):
		self.name = name
		self.config = config

	def runner(self, fname, args=[], noblock=False):
		path = self.config.path
		rstr = "%s %s"%(path.py, path.run[fname])
		if args:
			rstr = "%s %s"%(rstr, " ".join(['"%s"'%(a,) for a in args]))
		return self.out(rstr, noblock)

	def start(self, fname, port):
		self.log("start", fname, port)
		self.runner(fname, noblock=True)

	def run(self, fname, *args, **kwargs):
		cfg = self.config
		rcfg = config.request
		self.log("run", *args, kwargs)
		if cfg.persistent:
			self.log("persistent (via post)")
			for attempt in range(rcfg.retry):
				try:
					resp = requests.post("http://localhost:%s/"%(cfg.registered[fname],), json={
						"args": args,
						"kwargs": kwargs
					}, timeout=(rcfg.connect, rcfg.read)).content.decode()
					break
				except Exception as e:
					tries = attempt + 1
					self.log("run request", tries, "failed with", str(e))
					if tries == rcfg.retry:
						raise e
			try:
				resp = json.loads(resp)
			except:
				pass
			self.log(resp)
			return resp
		else:
			self.log("single (dropping kwargs)", *args)
			return self.runner(fname, args)