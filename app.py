#To-do:
#1) Add /api prefix to all routes
from flask import Flask
from apis import api

app = Flask(__name__)
api.init_app(app)

#Be sure to disable disable Debug mode for PROD
app.run(debug=True) 
# if __name__ == '__main__':
#     app.run(debug=True)