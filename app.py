from flask import Flask, render_template, g
from datetime import datetime
import pytz
import random
import psycopg2

#!/usr/bin/python
from config import config


def connect():
    """ Connect to the PostgreSQL database server """
    global conn
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        print('Database name: ', params["database"])
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
def disconnect():
    if conn is not None:
        conn.close()
        print('Database connection closed.')


### Make the flask app
app = Flask(__name__)

### Routes
@app.route("/")
def hello_world():
    return "Hello, world!"  # Whatever is returned from the function is sent to the browser and displayed.

@app.route("/time")
def get_time():
    now = datetime.now().astimezone(pytz.timezone("US/Central"))
    timestring = now.strftime("%Y-%m-%d %H:%M:%S")  # format the time as a easy-to-read string
    return render_template("time.html", timestring=timestring)


@app.route("/me")
def get_me():
  return "Yevhenii<br> Hitchenko<br> KID-21"

@app.route("/random")
def pick_number():
    number = random.randint(1, 10)
    return render_template("random.html", number=number)

@app.route("/dump")
def dump_entries():
    params = config()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rows = cursor.fetchall()
    output = ""
    for r in rows:
        app.logger.debug(str(r))
        q = (r[0], r[1].strftime("%Y-%m-%d %H:%M:%S"),) + r[2:]
        output += str(q)
        output += "\n"
    return "<pre>" + output + "</pre>"

@app.route("/unik")
def unik():
    params = config()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rows = cursor.fetchall()
    for r in rows:
        if "Yevhenii Hitchenko" in r: return render_template('unik.html', is_include="YES! YES! YES!")
    return render_template('unik.html', is_include="No")

@app.route("/unique")
def unique():
    params = config()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date limit 2')
    rows = cursor.fetchall()
    return render_template('browse.html', entries=rows)

@app.route("/browse")
def browse():
    params = config()
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rowlist = cursor.fetchall()
    return render_template('browse.html', entries=rowlist)


@app.cli.command("initdb")
def init_db():
    """Clear existing data and create new tables."""
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    with app.open_resource("schema.sql") as file: # open the file
        alltext = file.read() # read all the text
        cur.execute(alltext) # execute all the SQL in the file
    conn.commit()
    print("Initialized the database.")

@app.cli.command('populate')
def populate_db():
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    with app.open_resource("populate.sql") as file: # open the file
        alltext = file.read() # read all the text
        cur.execute(alltext) # execute all the SQL in the file
    conn.commit()
    print("Populated DB with sample data.")

### Start flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    
