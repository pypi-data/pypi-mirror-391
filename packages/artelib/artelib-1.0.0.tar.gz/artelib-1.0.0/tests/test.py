from artelib.web import Web, Request, Response

app = Web(__name__)

@app.get('/')
def home(request: Request, response: Response):
    return response.render_template("index.html")

@app.get('/hello')
def hello(request: Request, response: Response):
    name = request.query_params.get('name', ['World'])[0]
    return response.html(f'<h1>Hello, {name}!</h1>')

@app.get('/user/<user_id>')
def get_user(request: Request, response: Response, user_id: str):
    return response.json({
        'user_id': user_id,
        'name': f'User {user_id}',
        'status': 'active'
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)