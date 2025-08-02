from flask import Flask, render_template
import os  # For running GUI script in a new command window (Windows)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start_script():
    # Windows-specific: opens handsome.py in a new terminal window
    os.system('start python new.py')
    return 'Swara Player Started! You can close this tab now.'

if __name__ == '__main__':
    app.run(debug=True)