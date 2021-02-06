from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/https://discord.com/api/webhooks/806943861825863750/Y6x3bGQejFm0eWkS-8IgVYoSOYIirhPyPa0_QcknyMy2yqtUMwLVWHP1nZZ8C6fCOVe9',methods=['POST'])
def foo():
   data = json.loads(request.data)
   print(data)
#    print "New commit by: {}".format(data['commits'][0]['author']['name'])
   return "OK"

if __name__ == '__main__':
   app.run()