from chunithm import start_app

app = start_app()

app.run(debug=True, threaded=True, host="0.0.0.0", port=5555)