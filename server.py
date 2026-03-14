from flask import Flask, request
import sqlite3

app = Flask(__name__)

# create database
conn = sqlite3.connect("survey.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS results
(name TEXT, score INTEGER, level TEXT)""")

conn.commit()
conn.close()


@app.route('/')
def home():
    with open("index.html") as f:
        return f.read()


@app.route('/survey', methods=['POST'])
def survey():

    name = request.form['student_name']

    score = 0

    for i in range(1,11):
        if request.form.get(f"q{i}") == "yes":
            score += 1

    # stress levels
    if score <=3:
        level = "Low Stress"
        color = "green"
        suggestion = "Great! Keep maintaining your healthy routine 😊"
        alert = ""

    elif score <=7:
        level = "Medium Stress"
        color = "orange"
        suggestion = "Try meditation, exercise and proper sleep."
        alert = ""

    else:
        level = "High Stress"
        color = "red"
        suggestion = "Please talk to a teacher or counselor."
        alert = "<h2 style='color:red;'>⚠ Teacher Alert: High Stress Student</h2>"

    # save database
    conn = sqlite3.connect("survey.db")
    c = conn.cursor()

    c.execute("INSERT INTO results VALUES (?,?,?)",(name,score,level))

    conn.commit()
    conn.close()

    return f"""
    <html>

    <head>

    <style>

    body{{
    font-family:Arial;
    background:#f4f6f9;
    }}

    .card{{
    width:450px;
    margin:auto;
    margin-top:80px;
    background:white;
    padding:30px;
    border-radius:10px;
    box-shadow:0px 0px 10px gray;
    text-align:center;
    }}

    </style>

    </head>

    <body>

    <div class="card">

    <h1>Stress Result</h1>

    <h2>{name}</h2>

    <h3>Score : {score}/10</h3>

    <h2 style='color:{color};'>{level}</h2>

    {alert}

    <p>{suggestion}</p>

    <canvas id="chart"></canvas>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>

    var ctx=document.getElementById('chart');

    new Chart(ctx,{{
    type:'pie',
    data:{{
    labels:['Stress','Remaining'],
    datasets:[{{data:[{score},{10-score}]}}]
    }}
    }});

    </script>

    <br><br>

    <a href="/">Back</a>

    </div>

    </body>

    </html>
    """


@app.route('/admin')
def admin():

    conn=sqlite3.connect("survey.db")
    c=conn.cursor()

    data=c.execute("SELECT * FROM results").fetchall()

    conn.close()

    low=0
    medium=0
    high=0

    for row in data:

        if row[2]=="Low Stress":
            low+=1

        elif row[2]=="Medium Stress":
            medium+=1

        else:
            high+=1

    table="""
    <h1>Teacher Dashboard</h1>

    <table border=1>
    <tr>
    <th>Name</th>
    <th>Score</th>
    <th>Stress</th>
    </tr>
    """

    for row in data:

        table+=f"""
        <tr>
        <td>{row[0]}</td>
        <td>{row[1]}</td>
        <td>{row[2]}</td>
        </tr>
        """

    table+="</table>"

    chart=f"""

    <h2>Class Stress Analysis</h2>

    <canvas id="chart"></canvas>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>

    var ctx=document.getElementById('chart');

    new Chart(ctx,{{
    type:'bar',
    data:{{
    labels:['Low','Medium','High'],
    datasets:[{{
    label:'Students',
    data:[{low},{medium},{high}]
    }}]
    }}
    }});

    </script>
    """

    return table+chart


app.run(debug=True)