import sqlite3


def get_data(user_id):
	conn = None
	try:
		conn = sqlite3.connect('users.db')
		cursor = conn.cursor()

		cursor.execute('''
				CREATE TABLE IF NOT EXISTS users (
						id INTEGER PRIMARY KEY,
						points INTEGER,
						time INTEGER
				)
		''')

		cursor.execute("SELECT points, time FROM users WHERE id = ?", (user_id, ))
		result = cursor.fetchone()

		if result:
			return result
		else:
			cursor.execute("INSERT INTO users (id, points, time) VALUES (?, ?, ?)",
				       (user_id, 100, 0))
			conn.commit()
			return (100, 0)
	except sqlite3.Error as e:
		print(f"An error occurred: {e}")
		return None
	finally:
		if conn:
			conn.close()


def get_alldata():
	conn = None
	try:
		conn = sqlite3.connect('users.db')
		cursor = conn.cursor()

		cursor.execute('''
				CREATE TABLE IF NOT EXISTS users (
						id INTEGER PRIMARY KEY,
						points INTEGER,
						time INTEGER
				)
		''')
		cursor.execute("SELECT * FROM users")
		result = cursor.fetchall()
		return result
	except sqlite3.Error as e:
		print(f"An error occurred: {e}")
		return None
	finally:
		if conn:
			conn.close()


def update_points(user_id, points):
	conn = None
	try:
		conn = sqlite3.connect('users.db')
		cursor = conn.cursor()

		cursor.execute("UPDATE users SET points = ? WHERE id = ?",
			       (points, user_id))

		conn.commit()
	except sqlite3.Error as e:
		print(f"An error occurred: {e}")
	finally:
		if conn:
			conn.close()


def update_time(user_id, time):
	conn = None
	try:
		conn = sqlite3.connect('users.db')
		cursor = conn.cursor()

		cursor.execute("UPDATE users SET time = ? WHERE id = ?", (time, user_id))

		conn.commit()
	except sqlite3.Error as e:
		print(f"An error occurred: {e}")
	finally:
		if conn:
			conn.close()
