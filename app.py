from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import string
from static.py.data_user import User
from static.py.products import products
from cryptography.fernet import Fernet
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
import hashlib
import json
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this'

def get_products():
    PRODUCTS = products().get_products()
    return PRODUCTS
def get_user():
    """
    Lấy thông tin user từ database thay vì session
    """
    if 'username' not in session:
        return None
    
    username = session['username']
    user_obj = User()
    
    # Lấy thông tin user từ database
    user_data = user_obj.get_user_by_username(username)
    if not user_data:
        session.clear()
        return None
    
    return user_data

def generate_random_code(length=3):
    characters = string.ascii_uppercase + string.digits  # VD: A-Z, 0-9
    return ''.join(random.choices(characters, k=length))

def generate_key(secret, user_id, random_code):
    data = {
        "secret": secret,
        "user": user_id,
        "rand": random_code
    }
    json_str = json.dumps(data)
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    return encoded

@app.template_filter('vnd')
def vnd_format(value):
    try:
        return "{:,}".format(int(value))
    except Exception:
        return value
@app.context_processor
def inject_user():
    user = get_user()
    return dict(current_user=user)

@app.route('/')
def home():
    return render_template('index.html', products=get_products())

@app.route('/admin')
def admin_dashboard():
    user = get_user()
    if not user or user['username'] != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('home'))
    
    # Lấy danh sách thành viên từ database
    user_obj = User()
    members = user_obj.get_all_users()
    
    # Lấy lịch sử giao dịch từ database
    transactions = user_obj.get_transactions()
    
    return render_template(
        'admin.html',
        user=user,
        members=members,
        transactions=transactions,
        products=get_products()
    )

@app.route('/api/update_notify', methods=['POST'])
def update_notify():
    data = request.get_json()
    product_id = data.get('product_id')
    version_client = data.get('version_client')

    if not product_id or not version_client:
        return {'error': 'Thiếu product_id hoặc version_client'}, 400

    product_obj = products()
    # Giả sử bạn có hàm update_version_client(product_id, version_client)
    if product_obj.update_product(product_id, version_client):
        return {'message': 'Cập nhật version_client thành công'}, 200
    else:
        return {'error': 'Cập nhật thất bại'}, 500

@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    user = get_user()
    if not user or user['username'] != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['name']
        icon = request.form['icon']
        description = request.form['description']
        price = int(request.form['price'])
        category = request.form['category']
        features = request.form['features']
        download_link = request.form['download_link']
        
        # Lấy ID mới từ database
        product_obj = products()
        new_id = product_obj.get_next_id()
        
        if not product_obj.add_product(new_id, icon, name, price, description, category, features, download_link):
            flash('Thêm sản phẩm thất bại!', 'error')
            return render_template('add_product.html')
        else:
            flash('Thêm sản phẩm thành công!', 'success')
            # Refresh products list
            global PRODUCTS
            PRODUCTS = get_products()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_product.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_obj = User()
        if not user_obj.login_user(username, password):
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
            return render_template('login.html')
        else:
            # Chỉ lưu username vào session
            session['username'] = username
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('register.html')
        
        user_obj = User()
        if not user_obj.register_user(username, password, email):
            flash('Đăng ký thất bại! Tên đăng nhập đã tồn tại.', 'error')
            return render_template('register.html')
        else:
            flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    # Lấy danh sách purchases từ database
    user_obj = User()
    purchases = user_obj.get_user_purchases(user['username'])
    
    purchases_info = []
    for purchase in purchases:
        # Tìm thông tin sản phẩm
        product = next((prod for prod in get_products() if prod['id'] == purchase['product_id']), None)
        if product:
            purchases_info.append({
                'id': purchase['id'],
                'product_id': product['id'],
                'name': product['name'],
                'icon': product['icon'],
                'price': product['price'],
                'download_count': purchase.get('download_count', 0),
                'purchase_date': purchase.get('purchase_date', '---'),
                'key': purchase.get('key', '---')
            })
    
    return render_template('profile.html', user=user, purchases=purchases_info)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((prod for prod in get_products() if prod['id'] == product_id), None)
    if not product:
        flash('Sản phẩm không tồn tại!', 'error')
        return redirect(url_for('home'))
    return render_template('product_detail.html', product=product)
@app.route('/buy/<int:product_id>')
def buy_product(product_id):
    user = get_user()
    if not user:
        flash('Vui lòng đăng nhập để mua hàng!', 'error')
        return redirect(url_for('login'))
    
    user_obj = User()
    if user_obj.check_user_has_product(user['username'], product_id):
        flash('Bạn đã sở hữu sản phẩm này!', 'warning')
        return redirect(url_for('profile'))
    
    product = next((prod for prod in get_products() if prod['id'] == product_id), None)
    if not product:
        flash('Sản phẩm không tồn tại!', 'error')
        return redirect(url_for('home'))
    
    # Lấy version_client từ product
    version_client = product.get('version_client', '')

    if int(user['balance']) < int(product['price']):
        flash('Số dư không đủ! Vui lòng nạp thêm tiền.', 'error')
        return redirect(url_for('recharge'))
    
    # Secret cứng (không công khai)
    secret = "voletrieulan2007"

    # Tạo ngày hết hạn = hôm nay + 1 tháng
    expire_dt = datetime.now() + relativedelta(months=1)
    date_key_part = expire_dt.strftime("%Y-%m-%d")  # Dùng phần ngày để tạo key

    key = generate_key("voletrieulan2007", user['username'], generate_random_code())

    # Lưu cả encrypted_str và date_key_part vào purchase
    if user_obj.purchase_product(
        user['username'],
        product_id,
        key,
        product['price'],
        version_client,
        date_key_part  # <-- Thêm dòng này, truyền vào DB hoặc file
    ):
        flash(f'Mua {product["name"]} thành công! Check profile để download.', 'success')
    else:
        flash('Có lỗi xảy ra khi mua hàng!', 'error')
    
    return redirect(url_for('profile'))

@app.route('/recharge', methods=['GET', 'POST'])
def recharge():
    user = get_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        amount = int(request.form['amount'])
        
        user_obj = User()
        if user_obj.add_balance(user['username'], amount):
            flash(f'Nạp {amount:,} VNĐ thành công!', 'success')
        else:
            flash('Có lỗi xảy ra khi nạp tiền!', 'error')
        
        return redirect(url_for('profile'))
    
    return render_template('recharge.html')

@app.route('/download/<int:purchase_id>')
def download_product(purchase_id):
    user = get_user()
    if not user:
        return redirect(url_for('login'))

    user_obj = User()
    purchase = user_obj.get_purchase_by_id(purchase_id, user['username'])
    if not purchase:
        flash('Không tìm thấy sản phẩm!', 'error')
        return redirect(url_for('profile'))
    PRODUCTS = products().get_products()
    product = next((prod for prod in PRODUCTS if prod['id'] == purchase['product_id']), None)
    if not product:
        flash('Không tìm thấy sản phẩm!', 'error')
        return redirect(url_for('profile'))


    base_link = product["download_link"]  # vd: https://github.com/voletrieulan0907/tool_changemail
    version = product["version"]    
    version_client = product['version_client']      # vd: v0.0.6
    filename = "MyApp-windows.zip"        # hoặc lấy từ product nếu muốn tuỳ biến
    user_obj = User()
    user_obj.increment_download_count(purchase_id, user['username'],version_client)
    # Tạo link tải GitHub theo cấu trúc:
    # https://github.com/<repo>/releases/download/<version>/<filename>
    download_url = f"{base_link}/download/{version}/{filename}"

    return redirect(download_url)

# https://github.com/voletrieulan0907/tool_changemail/releases/download/v0.0.6/MyApp-windows.zip
if __name__ == '__main__':
    app.run(debug=True)