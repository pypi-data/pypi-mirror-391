RTMP = """from optparse import OptionParser
parser = OptionParser("run.py [arg1] [arg2] ...")
args = parser.parse_args()[1]

%s
%s(*args)"""

PTMP = """import json, rel
from subprocess import getoutput
from dez.http.application import HTTPApplication

def log(*msgs):
	print("venvr bridge", *msgs, flush=True)
	with open("venvr.log", "a") as f:
		f.write(" ".join([str(m) for m in msgs]) + "\\n")

%s
caller = %s

def call(req):
	d = json.loads(req.body)
	log("calling with", d["args"], d["kwargs"])
	if WITHPAUSE:
		log("rel pause")
		rel.pause()
	resp = caller(*d["args"], **d["kwargs"])
	app.daemon.respond(req, resp)
	if WITHPAUSE:
		log("rel resume")
		rel.resume()

def pcheck():
	if not getoutput("ps -ef | grep PID | grep -v grep"):
		log("parent process ended - quitting")
		app.stop()
	return True

if WITHPATH:
	import os, sys
	callerpath = os.path.abspath(".")
	log("adding", callerpath, "to path")
	sys.path.insert(0, callerpath)

if LOGGY:
	rel.set_verbose(True)
	from fyg.util import log as flog
	from dez.logging import get_logger_getter
	logger_getter = get_logger_getter("venvr", flog,
		["access", "info", "log", "warn", "debug", "error", "detail"])
	app = HTTPApplication("", PORT, logger_getter)
else:
	app = HTTPApplication("", PORT)

app.add_cb_rule("/", call)
rel.timeout(5, pcheck)
log("starting")
app.start()"""