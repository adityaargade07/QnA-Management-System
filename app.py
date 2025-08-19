from app import create_app
from flask import Flask, redirect, url_for

app = create_app()  # Use the factory function to create the app instance
@app.route('/')
def home():
    return redirect(url_for('auth.login'))  # Redirect to the login page initially

if __name__ == '__main__':
    app.run(debug=True)
