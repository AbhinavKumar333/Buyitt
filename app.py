from flask import Flask, render_template, request, make_response, redirect, url_for, session
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'dbpro'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Dbms@123'
app.config['MYSQL_DATABASE_DB'] = 'DB_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
app.secret_key = 'asdf123'

def connect(query, var):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(query, var)			
	conn.commit()
	result = cursor.fetchall()
	return result

@app.route("/cart")
def cart():
	if 'email' not in session:
		return '<script>alert("Login to Continue")</script>',render_template('account.html')
	x = request.args.get('action')
	y = session['email']
	a = connect("select id from users where email = %s", (y))
	if x is not None:
		if x == 'addItem':
			b = connect("select Id from Items where I_name = %s", (request.args.get('name')))
			check = connect("select count from cart where Uid = %s and Pid = %s", (a[0],b[0]))
			if not check:
				print check
				connect("insert into cart values(%s,%s,1)", (a[0], b[0]))
			else:
				print check[0][0]+1
				connect("update cart set count = %s where Uid = %s and Pid = %s", (check[0][0]+1,a[0], b[0]))

		elif x == 'deleteItem':
			connect("delete from cart where Uid = %s and Pid = %s", (a[0], request.args.get('pid')))
	pid = connect("select * from cart where Uid = %s ", (a[0]))
	d ={}
	c = []
	i = 0
	if pid:
		for p in pid:
			d[i] = connect("select * from Items where Id = %s", (p[1]))
			print d[i]
			c.append(p[2])
			i += 1
	return render_template('cart.html', data=d, sess = y, c=c)
		
@app.route("/search", methods = ['POST', 'GET'])
def search():
	key = request.args.get('search')
	ser = connect("select * from Items where I_name like %s", ('%'+key+'%'))
	print '%'+key+'%'
	if 'email' in session:
		return render_template('search.html', arg = key, sess = session['email'], data=ser)
	return render_template('search.html', arg = key, data=ser)

@app.route("/signup", methods = ['POST', 'GET'])
def signup():
	if request.method == 'POST':
		form = request.form
		session['email'] = form['email']
		if form['pass'] == form['conpass']:
			connect("insert into users values (0,%s,%s,%s)",(form['username'], form['email'], form['pass']))
			return redirect(url_for('main'))			
	return render_template('signup.html')

@app.route("/signin", methods = ['POST', 'GET'])
def signin():
	if request.args.get('action') == 'logout':
		session.clear()
	elif request.method == 'POST':
		form = request.form
		r = connect("select * from users where email = %s and password = %s", (form['email'], form['pass']))
		if not r:
			return '<script>alert("Email isn`t registered");</script>',render_template('signup.html')
		else:
			session['email'] = form['email']
			sess = session['email']
			return redirect(url_for('main'))
	return render_template('account.html')

#@app.route("/getcookie")
#def getcookie():
#	e = request.cookies.get('Email')
#	return '<h1>welcome '+e+'</h1>'

@app.route("/")
def main():
	result = connect("select * from Items", None)
	if 'email' in session:
		return render_template('index.html', data = result, sess = session['email'])	
	else:
		return render_template('index.html', data = result)	


if __name__ == "__main__":
	app.run(debug = True)
