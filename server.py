from flask import Flask
import chunithm

app = Flask(__name__)

@app.route('/')
def hello():
	return chunithm.CalcRate('akashisn','vAw7ujeheta6efrA')

if __name__ == '__main__':
	import os
	HOST = os.environ.get('SERVER_HOST', 'localhost')
	try:
		PORT = int(os.environ.get('SERVER_PORT', '5555'))
	except ValueError:
		PORT = 5555
	app.run(HOST, PORT)
