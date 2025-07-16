from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for the flash message

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory_db'

mysql = MySQL(app)

# ROUTES

@app.route('/', methods=['GET'])
def index():
    cur = mysql.connection.cursor()
    search = request.args.get('search')

    if search:
        cur.execute("SELECT * FROM items WHERE name LIKE %s", ('%' + search + '%',))
    else:
        cur.execute("SELECT * FROM items")

    data = cur.fetchall()
    # Calculate total value
    total_value = sum(item[2] * item[3] for item in data)
    cur.close()
    return render_template('index.html', items=data, search=search, total_value=total_value)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']

        if not name or not quantity or not price:
            flash('All fields are required','danger')
            return redirect(url_for('create'))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO items (name, quantity, price) VALUES (%s, %s, %s)", (name, quantity, price))
        mysql.connection.commit()
        cur.close()
        flash('Item added', 'success')
        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']

        if not name or not quantity or not price:
            flash('All fields are requierd','danger')
            return redirect(url_for('update', id=id))

        cur.execute("UPDATE items SET name=%s, quantity=%s, price=%s WHERE id=%s", (name, quantity, price, id))
        mysql.connection.commit()
        cur.close()
        flash('Item updated', 'success')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM items WHERE id = %s", (id,))
    item = cur.fetchone()
    cur.close()
    return render_template('update.html', item=item)


@app.route('/delete/<int:id>')
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Item deleted', 'success')
    return redirect(url_for('index'))

#THE MAIN APP

if __name__ == '__main__':
    app.run(debug=True)
