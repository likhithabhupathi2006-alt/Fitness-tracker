CREATE DATABASE fitness_tracker;
USE fitness_tracker;

CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50),
  age INT,
  gender ENUM('Male','Female','Other'),
  height DECIMAL(5,2),
  weight DECIMAL(5,2)
);

CREATE TABLE workouts (
  workout_id INT PRIMARY KEY AUTO_INCREMENT,
  workout_name VARCHAR(50),
  workout_type VARCHAR(50),
  calories_burned_per_hour INT
);

CREATE TABLE user_workouts (
  log_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  workout_id INT,
  duration_minutes INT,
  date DATE,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (workout_id) REFERENCES workouts(workout_id)
);

CREATE TABLE progress (
  progress_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  weight DECIMAL(5,2),
  bmi DECIMAL(4,2),
  log_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);