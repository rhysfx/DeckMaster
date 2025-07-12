import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        db=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

@app.route('/')
def index():
    # Show all pages
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pages ORDER BY page_number ASC")
        pages = cur.fetchall()
    return render_template('pages.html', pages=pages)

@app.route('/page/<int:page_number>')
def edit_page(page_number):
    # Edit a page and show its buttons
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pages WHERE page_number=%s", (page_number,))
        page = cur.fetchone()
        cur.execute("SELECT * FROM buttons WHERE FIND_IN_SET(%s, page)", (page_number,))
        buttons = cur.fetchall()
    return render_template('edit_page.html', page=page, buttons=buttons)

@app.route('/page/new', methods=['GET', 'POST'])
def new_page():
    if request.method == 'POST':
        number = request.form['page_number']
        url = request.form.get('webpage_url', '')
        show_web = int(request.form.get('show_webpage', 0))
        bg = request.form.get('background_color', '#1e1e1e')
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pages (page_number, webpage_url, show_webpage, background_color) VALUES (%s, %s, %s, %s)",
                (number, url, show_web, bg)
            )
        flash('Page created!')
        return redirect(url_for('index'))
    return render_template('edit_page.html', page=None, buttons=[])

@app.route('/button/new/<int:page_number>', methods=['GET', 'POST'])
def new_button(page_number):
    if request.method == 'POST':
        label = request.form['label']
        pos_x = request.form['pos_x']
        pos_y = request.form['pos_y']
        color_bg = request.form.get('color_bg', '#333')
        color_fg = request.form.get('color_fg', '#fff')
        action = request.form.get('action', '')
        image_path = request.form.get('image_path', '')
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO buttons (label, pos_x, pos_y, color_bg, color_fg, action, image_path, page) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (label, pos_x, pos_y, color_bg, color_fg, action, image_path, str(page_number))
            )
        flash('Button added!')
        return redirect(url_for('edit_page', page_number=page_number))
    return render_template('edit_button.html', page_number=page_number, button=None)

@app.route('/button/edit/<int:button_id>', methods=['GET', 'POST'])
def edit_button(button_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM buttons WHERE id=%s", (button_id,))
        button = cur.fetchone()
    if request.method == 'POST':
        label = request.form['label']
        pos_x = request.form['pos_x']
        pos_y = request.form['pos_y']
        color_bg = request.form.get('color_bg', '#333')
        color_fg = request.form.get('color_fg', '#fff')
        action = request.form.get('action', '')
        image_path = request.form.get('image_path', '')
        page = request.form.get('page', button['page'])
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE buttons SET label=%s, pos_x=%s, pos_y=%s, color_bg=%s, color_fg=%s, action=%s, image_path=%s, page=%s WHERE id=%s",
                (label, pos_x, pos_y, color_bg, color_fg, action, image_path, page, button_id)
            )
        flash('Button updated!')
        return redirect(url_for('edit_page', page_number=page))
    return render_template('edit_button.html', page_number=button['page'], button=button)

@app.route('/button/delete/<int:button_id>')
def delete_button(button_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT page FROM buttons WHERE id=%s", (button_id,))
        button = cur.fetchone()
        if button:
            page_number = button['page']
            cur.execute("DELETE FROM buttons WHERE id=%s", (button_id,))
            flash('Button deleted!')
            return redirect(url_for('edit_page', page_number=page_number))
    flash('Button not found.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)