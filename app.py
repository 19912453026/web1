from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1932326378@localhost:3306/course_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    course_status = db.Column(db.String(20), default='未购买')

# 主页
@app.route('/')
def index():
    return render_template('index.html')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        else:
            return "登录失败，请检查用户名或密码"
    return render_template('login.html')

# 用户/管理员面板
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if user.is_admin:
        # 管理员界面
        users = User.query.filter_by(is_admin=False).all()
        return render_template('admin_dashboard.html', users=users)
    else:
        # 普通用户界面
        if user.course_status == '购买':
            course = 'math.mp4' if username == 'math' else 'english.mp4'  # 示例课程
            return f'您已购买，点击观看课程: <a href="/static/{course}">观看</a><br><a href="/logout">退出</a>'
        return render_template('user_dashboard.html')

# 购买课程
@app.route('/purchase')
def purchase():
    if 'username' not in session or session.get('is_admin', False):
        return redirect(url_for('login'))
    return '''
    <h2>请扫码支付，并加管理员QQ1932326378让其帮你修改状态</h2>
    <img src="/static/shoukuanma.png" alt="收款码">
    <br><a href="/logout">退出</a>
    '''

# 修改课程状态（管理员）
@app.route('/update_status/<int:user_id>', methods=['POST'])
def update_status(user_id):
    if not session.get('is_admin', False):
        return redirect(url_for('login'))
    status = request.form['status']
    user = User.query.get(user_id)
    user.course_status = status
    db.session.commit()
    return redirect(url_for('dashboard'))

# 退出
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
