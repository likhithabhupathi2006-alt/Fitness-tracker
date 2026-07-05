from flask import Flask, render_template, request, redirect,flash
import mysql.connector
app = Flask(__name__)
app.secret_key = "mypassword123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="fitness_tracker2"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()

    if search_query:
        if search_query.isdigit():  
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (search_query,))
        else:
            cursor.execute("SELECT * FROM users WHERE name LIKE %s", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS count FROM user_workouts")
    total_workouts = cursor.fetchone()['count']

    cursor.execute("""
        SELECT SUM((duration_minutes/60)*w.calories_burned_per_hour) AS total
        FROM user_workouts uw
        JOIN workouts w ON uw.workout_id = w.workout_id
    """)
    result = cursor.fetchone()
    total_calories = result['total'] if result['total'] else 0

    return render_template(
        'index.html',
        users=users,
        total_workouts=total_workouts,
        total_calories=int(total_calories),
        search_query=search_query
    )


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        cursor.execute("INSERT INTO users (name, age, gender, height, weight) VALUES (%s,%s,%s,%s,%s)",
                       (name, age, gender, height, weight))
        db.commit()
        flash("user added successfully","success")
        return redirect('/')
    return render_template('add_user.html')
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']

        cursor.execute("""
            UPDATE users 
            SET name=%s, age=%s, gender=%s, height=%s, weight=%s
            WHERE user_id=%s
        """, (name, age, gender, height, weight, user_id))
        db.commit()
        flash("user updated successfully","info")
        return redirect('/')

    return render_template('edit_user.html', user=user)


@app.route('/add_workout', methods=['GET', 'POST'])
def add_workout():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM workouts")
    workouts = cursor.fetchall()
    if request.method == 'POST':
        user_id = request.form['user_id']
        workout_id = request.form['workout_id']
        duration = request.form['duration']
        date = request.form['date']
        cursor.execute("INSERT INTO user_workouts (user_id, workout_id, duration_minutes, date) VALUES (%s,%s,%s,%s)",
                       (user_id, workout_id, duration, date))
        db.commit()
        flash("workout added successfully!", "success")
        return redirect('/')
    return render_template('add_workout.html', users=users, workouts=workouts)

@app.route('/progress', methods=['GET', 'POST'])
def progress():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if request.method == 'POST':
        user_id = request.form['user_id']
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        bmi = round(weight / ((height / 100) ** 2), 2)

        # BMI Category
        if bmi < 18.5:
            bmi_category = "Underweight"
            health_tips = "Increase calorie intake with nutritious foods. Include nuts, dairy, and protein-rich meals."
        elif 18.5 <= bmi < 24.9:
            bmi_category = "Normal"
            health_tips = "Maintain your healthy lifestyle with balanced eating and regular exercise."
        elif 25 <= bmi < 29.9:
            bmi_category = "Overweight"
            health_tips = "Try to incorporate daily walks, reduce sugar, and follow a calorie-controlled diet."
        else:
            bmi_category = "Obese"
            health_tips = "Consult a nutritionist, avoid junk food, and adopt a structured diet + exercise plan."
        date = request.form['date']

        cursor.execute("INSERT INTO progress (user_id, weight, bmi, log_date) VALUES (%s,%s,%s,%s)",
                       (user_id, weight, bmi, date))
        db.commit()
        flash("progress added successfully!", "success")

        return render_template(
            'progress.html',
            users=users,
            bmi=bmi,
            bmi_category=bmi_category,
            health_tips=health_tips
        )
    return render_template(
        'progress.html', 
        users=users
    )

@app.route('/report')
def report():
    query = """
    SELECT u.name, SUM((uw.duration_minutes/60)*w.calories_burned_per_hour) AS total_calories
    FROM user_workouts uw
    JOIN users u ON uw.user_id = u.user_id
    JOIN workouts w ON uw.workout_id = w.workout_id
    GROUP BY u.name
    """
    cursor.execute(query)
    data = cursor.fetchall()
    # Progress graph data (weight over time)
    cursor.execute("""
        SELECT u.name, p.weight, p.log_date
        FROM progress p
        JOIN users u ON p.user_id = u.user_id
        ORDER BY p.log_date
    """)
    progress = cursor.fetchall()
    return render_template('report.html', data=data,progress=progress)
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    cursor.execute("DELETE FROM progress WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM user_workouts WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    db.commit()
    flash("User deleted successfully!", "success")
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
