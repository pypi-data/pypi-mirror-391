from fyg import Config

config = Config({
	"port":{
		"slice": 10,
		"block": 100,
		"start": 17000
	},
	"vstore": "venvrs",
	"request": {
		"wait": 2,
		"retry": 3,
		"read": 600,
		"connect": 6,
		"withpause": False
	}
})

def getPortBlock():
	pcfg = config.port
	start = pcfg.start
	pcfg.update("start", pcfg.start + pcfg.block)
	return start