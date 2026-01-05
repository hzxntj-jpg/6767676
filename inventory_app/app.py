from flask import Flask, render_template, request, redirect, url_for, send_file, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from datetime import datetime, timedelta
import csv
import io
import sqlite3
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
import os as _os
_base_dir = _os.path.abspath(_os.path.dirname(__file__))
_db_env = _os.environ.get("SQLALCHEMY_DATABASE_URI") or _os.environ.get("DATABASE_URL")
if _db_env:
    if _db_env.startswith("postgres://"):
        _db_env = _db_env.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = _db_env
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + _os.path.join(_base_dir, "inventory.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = _os.environ.get("FLASK_SECRET_KEY", "change-this-key")
db = SQLAlchemy(app)

TRANSLATIONS = {
    "en": {
        "Dashboard": "Dashboard",
        "Orders": "Orders",
        "Products": "Products",
        "Products label": "Products",
        "New Sale": "New Sale",
        "Purchases": "Purchases",
        "New Purchase": "New Purchase",
        "Customers": "Customers",
        "Suppliers": "Suppliers",
        "Supplier": "Supplier",
        "Admin": "Admin",
        "Keys": "Keys",
        "Settings": "Settings",
        "Users": "Users",
        "Logout": "Logout",
        "Login": "Login",
        "Register": "Register",
        "Search": "Search",
        "Search customers": "Search customers",
        "Search suppliers": "Search suppliers",
        "Search by customer": "Search by customer",
        "Search by supplier": "Search by supplier",
        "Search customer": "Search customer",
        "Search supplier": "Search supplier",
        "Search product": "Search product",
        "Add Purchase": "Add Purchase",
        "Add Supplier": "Add Supplier",
        "Add Customer": "Add Customer",
        "Add Order": "Add Order",
        "New Product": "New Product",
        "Add Item": "Add Item",
        "Create": "Create",
        "Qty": "Qty",
        "Finish": "Finish",
        "Sales Orders": "Sales Orders",
        "Purchase Orders": "Purchase Orders",
        "Low Stock": "Low Stock",
        "Recent Sales": "Recent Sales",
        "Recent Purchases": "Recent Purchases",
        "Sales Today": "Sales Today",
        "Purchases Today": "Purchases Today",
        "Email": "Email",
        "Password": "Password",
        "Name": "Name",
        "Phone": "Phone",
        "Create Account": "Create Account",
        "No account? Register": "No account? Register",
        "Already have an account? Login": "Already have an account? Login",
        "ID": "ID",
        "Customer": "Customer",
        "Date": "Date",
        "Status": "Status",
        "Total": "Total",
        "Product": "Product",
        "Quantity": "Quantity",
        "Unit Price": "Unit Price",
        "Export CSV": "Export CSV",
        "No items": "No items",
        "SKU": "SKU",
        "Category": "Category",
        "Price": "Price",
        "Stock": "Stock",
        "Edit": "Edit",
        "Uncategorized": "Uncategorized",
        "Search Results": "Search Results",
        "Real-time Inventory": "Real-time Inventory",
        "Track stock with instant updates": "Track stock with instant updates",
        "Smart Purchases": "Smart Purchases",
        "Plan and restock with confidence": "Plan and restock with confidence",
        "Sales Insights": "Sales Insights",
        "Clear reports to grow faster": "Clear reports to grow faster",
        "Secure & Multi-Account": "Secure & Multi-Account",
        "Data isolated per user": "Data isolated per user",
        "Achievements": "Achievements",
        "Level up while you work": "Level up while you work",
        "Buy": "Buy",
        "Choose your plan": "Choose your plan",
        "Choose your currency": "Choose your currency",
        "Monthly": "Monthly",
        "Yearly": "Yearly",
        "BRL (PIX)": "BRL (PIX)",
        "USD (Card)": "USD (Card)",
        "Plans": "Plans",
        "Choose Your Plan": "Choose Your Plan",
        "Access for 30 days": "Access for 30 days",
        "Access for 365 days": "Access for 365 days",
        "Already paid?": "Already paid?",
        "Enter your email to retrieve your license key.": "Enter your email to retrieve your license key.",
        "Retrieve Key": "Retrieve Key",
        "Cancel": "Cancel",
        "Purchase": "Purchase",
        "Get Started": "Get Started",
        "Best Value": "Best Value",
        "Most Popular": "Most Popular",
        "Save 75% vs monthly": "Save 75% vs monthly",
        "Equivalent to $1.25/month": "Equivalent to $1.25/month",
        "Benefits": "Benefits",
        "Instant license key": "Instant license key",
        "Priority support": "Priority support",
        "All features included": "All features included",
        "Buy Now": "Buy Now"
    },
    "pt": {
        "Dashboard": "Painel",
        "Orders": "Pedidos",
        "Products": "Produtos",
        "Products label": "Produtos",
        "New Sale": "Nova Venda",
        "Purchases": "Compras",
        "New Purchase": "Nova Compra",
        "Customers": "Clientes",
        "Suppliers": "Fornecedores",
        "Supplier": "Fornecedor",
        "Admin": "Admin",
        "Keys": "Chaves",
        "Settings": "Configurações",
        "Users": "Usuários",
        "Logout": "Sair",
        "Login": "Entrar",
        "Register": "Registrar",
        "Search": "Buscar",
        "Search customers": "Buscar clientes",
        "Search suppliers": "Buscar fornecedores",
        "Search by customer": "Buscar por cliente",
        "Search by supplier": "Buscar por fornecedor",
        "Search customer": "Buscar cliente",
        "Search supplier": "Buscar fornecedor",
        "Search product": "Buscar produto",
        "Add Purchase": "Adicionar Compra",
        "Add Supplier": "Adicionar Fornecedor",
        "Add Customer": "Adicionar Cliente",
        "Add Order": "Adicionar Pedido",
        "New Product": "Novo Produto",
        "Add Item": "Adicionar Item",
        "Create": "Criar",
        "Qty": "Qtd",
        "Finish": "Finalizar",
        "Sales Orders": "Pedidos de Venda",
        "Purchase Orders": "Pedidos de Compra",
        "Low Stock": "Baixo estoque",
        "Recent Sales": "Vendas recentes",
        "Recent Purchases": "Compras recentes",
        "Sales Today": "Vendas Hoje",
        "Purchases Today": "Compras Hoje",
        "Email": "E-mail",
        "Password": "Senha",
        "Name": "Nome",
        "Phone": "Telefone",
        "Create Account": "Criar Conta",
        "No account? Register": "Sem conta? Registrar",
        "Already have an account? Login": "Já tem conta? Entrar",
        "ID": "ID",
        "Customer": "Cliente",
        "Date": "Data",
        "Status": "Status",
        "Total": "Total",
        "Product": "Produto",
        "Quantity": "Quantidade",
        "Unit Price": "Preço Unitário",
        "Unit Cost": "Custo Unitário",
        "Export CSV": "Exportar CSV",
        "No items": "Sem itens",
        "SKU": "SKU",
        "Category": "Categoria",
        "Price": "Preço",
        "Stock": "Estoque",
        "Edit": "Editar",
        "Uncategorized": "Sem categoria",
        "Search Results": "Resultados da pesquisa",
        "Real-time Inventory": "Estoque em tempo real",
        "Track stock with instant updates": "Acompanhe o estoque com atualizações instantâneas",
        "Smart Purchases": "Compras inteligentes",
        "Plan and restock with confidence": "Planeje e reabasteça com segurança",
        "Sales Insights": "Insights de vendas",
        "Clear reports to grow faster": "Relatórios claros para crescer mais rápido",
        "Secure & Multi-Account": "Seguro e Multi-conta",
        "Data isolated per user": "Dados isolados por usuário",
        "Achievements": "Conquistas",
        "Level up while you work": "Evolua enquanto trabalha",
        "Buy": "Comprar",
        "Choose your plan": "Escolha seu plano",
        "Choose your currency": "Escolha a moeda",
        "Monthly": "Mensal",
        "Yearly": "Anual",
        "BRL (PIX)": "BRL (PIX)",
        "USD (Card)": "USD (Cartão)",
        "Plans": "Planos",
        "Choose Your Plan": "Escolha seu Plano",
        "Access for 30 days": "Acesso por 30 dias",
        "Access for 365 days": "Acesso por 365 dias",
        "Already paid?": "Já pagou?",
        "Enter your email to retrieve your license key.": "Informe seu e-mail para recuperar sua chave.",
        "Retrieve Key": "Recuperar Chave",
        "Cancel": "Cancelar",
        "Purchase": "Comprar",
        "Get Started": "Começar",
        "Best Value": "Melhor custo-benefício",
        "Most Popular": "Mais popular",
        "Save 75% vs monthly": "Economize 75% vs mensal",
        "Equivalent to $1.25/month": "Equivale a US$ 1,25/mês",
        "Benefits": "Benefícios",
        "Instant license key": "Chave de licença instantânea",
        "Priority support": "Suporte prioritário",
        "All features included": "Todos os recursos inclusos",
        "Buy Now": "Comprar agora"
    }
}

def get_lang():
    l = session.get("lang", "en")
    return l if l in ("en", "pt") else "en"

def t(key):
    lang = get_lang()
    m = TRANSLATIONS.get(lang, {})
    return m.get(key, key)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    theme_primary_color = db.Column(db.String(16), default="#3b82f6")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(128))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Float, default=0)
    stock = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    category_rel = db.relationship("Category")
    __table_args__ = (db.UniqueConstraint("user_id", "sku", name="uq_product_user_sku"),)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class LicenseKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    plan = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    issued_to_email = db.Column(db.String(255))
    redeemed_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    redeemed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    payment_source = db.Column(db.String(32))
    status = db.Column(db.String(16), default="active")
    currency = db.Column(db.String(8))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), default="open")
    total = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    customer = db.relationship("Customer")

class SalesOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("sales_order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    product = db.relationship("Product")
    order = db.relationship("SalesOrder", backref=db.backref("items", lazy=True))

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("supplier.id"))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), default="open")
    total = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    supplier = db.relationship("Supplier")

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)
    unit_cost = db.Column(db.Float, default=0)
    product = db.relationship("Product")
    po = db.relationship("PurchaseOrder", backref=db.backref("items", lazy=True))

class InventoryMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    change = db.Column(db.Integer)
    reason = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    reference = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product = db.relationship("Product")

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    key = db.Column(db.String(64))
    title = db.Column(db.String(255))
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

def ensure_schema():
    with db.engine.begin() as conn:
        # add is_admin to user if missing
        ucols = conn.execute(text("PRAGMA table_info(user)")).fetchall()
        unames = {row[1] for row in ucols}
        if "is_admin" not in unames:
            conn.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
        if "theme_primary_color" not in unames:
            conn.execute(text("ALTER TABLE user ADD COLUMN theme_primary_color TEXT DEFAULT '#3b82f6'"))
        res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='product'"))
        exists = res.fetchone() is not None
        if not exists:
            return
        cols_res = conn.execute(text("PRAGMA table_info(product)")).fetchall()
        cols = {row[1] for row in cols_res}
        if "category_id" not in cols:
            conn.execute(text("ALTER TABLE product ADD COLUMN category_id INTEGER"))
        if "created_at" not in cols:
            conn.execute(text("ALTER TABLE product ADD COLUMN created_at DATETIME"))
            conn.execute(text("UPDATE product SET created_at = datetime('now')"))
        if "user_id" not in cols:
            conn.execute(text("ALTER TABLE product ADD COLUMN user_id INTEGER"))
        def add_user_id(table):
            c = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
            names = {r[1] for r in c}
            if "user_id" not in names:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER"))
        for t in ["category","customer","supplier","sales_order","purchase_order","inventory_movement"]:
            add_user_id(t)
        pil = conn.execute(text("PRAGMA index_list('product')")).fetchall()
        product_has_global_unique = False
        for idx in pil:
            if idx[2] == 1:
                info = conn.execute(text(f"PRAGMA index_info('{idx[1]}')")).fetchall()
                cols_idx = [r[2] for r in info]
                if cols_idx == ["sku"]:
                    product_has_global_unique = True
        if product_has_global_unique:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.execute(text("""
                CREATE TABLE product_new (
                    id INTEGER PRIMARY KEY,
                    sku TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT,
                    category_id INTEGER,
                    created_at DATETIME,
                    price REAL DEFAULT 0,
                    stock INTEGER DEFAULT 0,
                    user_id INTEGER,
                    FOREIGN KEY(category_id) REFERENCES category(id),
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            """))
            conn.execute(text("CREATE UNIQUE INDEX uq_product_user_sku ON product_new(user_id, sku)"))
            conn.execute(text("INSERT INTO product_new(id, sku, name, category, category_id, created_at, price, stock, user_id) SELECT id, sku, name, category, category_id, created_at, price, stock, user_id FROM product"))
            conn.execute(text("DROP TABLE product"))
            conn.execute(text("ALTER TABLE product_new RENAME TO product"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
        cil = conn.execute(text("PRAGMA index_list('category')")).fetchall()
        category_has_global_unique = False
        for idx in cil:
            if idx[2] == 1:
                info = conn.execute(text(f"PRAGMA index_info('{idx[1]}')")).fetchall()
                cols_idx = [r[2] for r in info]
                if cols_idx == ["name"]:
                    category_has_global_unique = True
        if category_has_global_unique:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.execute(text("""
                CREATE TABLE category_new (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            """))
            conn.execute(text("CREATE UNIQUE INDEX uq_category_user_name ON category_new(user_id, name)"))
            conn.execute(text("INSERT INTO category_new(id, name, description, user_id) SELECT id, name, description, user_id FROM category"))
            conn.execute(text("DROP TABLE category"))
            conn.execute(text("ALTER TABLE category_new RENAME TO category"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
        lk_cols = conn.execute(text("PRAGMA table_info(license_key)")).fetchall()
        lk_names = {row[1] for row in lk_cols} if lk_cols else set()
        if "payment_source" not in lk_names:
            conn.execute(text("ALTER TABLE license_key ADD COLUMN payment_source TEXT"))
        if "status" not in lk_names:
            conn.execute(text("ALTER TABLE license_key ADD COLUMN status TEXT DEFAULT 'active'"))
        if "currency" not in lk_names:
            conn.execute(text("ALTER TABLE license_key ADD COLUMN currency TEXT"))

with app.app_context():
    db.create_all()
    ensure_schema()
    admin_email = "rafael.athaydee@gmail.com"
    adm = User.query.filter_by(email=admin_email).first()
    if adm and not adm.is_admin:
        adm.is_admin = True
        db.session.commit()

def unlock(uid, key, title):
    if Achievement.query.filter(Achievement.user_id == uid, Achievement.key == key).first():
        return
    a = Achievement(user_id=uid, key=key, title=title, unlocked_at=datetime.utcnow())
    db.session.add(a)
    db.session.commit()

def check_achievements_post_sale(uid):
    total_sales = db.session.query(func.count(SalesOrder.id)).filter(SalesOrder.user_id == uid).scalar() or 0
    if total_sales >= 1:
        unlock(uid, "first_sale", "First Sale")
    if total_sales >= 10:
        unlock(uid, "ten_sales", "10 Sales")
    if total_sales >= 50:
        unlock(uid, "fifty_sales", "50 Sales")

def check_achievements_post_purchase(uid):
    total_purchases = db.session.query(func.count(PurchaseOrder.id)).filter(PurchaseOrder.user_id == uid).scalar() or 0
    if total_purchases >= 1:
        unlock(uid, "first_purchase", "First Purchase")
    if total_purchases >= 10:
        unlock(uid, "ten_purchases", "10 Purchases")

def check_achievements_post_product(uid):
    total_products = db.session.query(func.count(Product.id)).filter(Product.user_id == uid).scalar() or 0
    if total_products >= 100:
        unlock(uid, "inventory_100", "Inventory 100 Items")

def unlock_no_low(uid, low_count):
    if (low_count or 0) == 0:
        unlock(uid, "no_low_stock", "No Low Stock")

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("uid"):
            return redirect(url_for("auth_login"))
        return f(*args, **kwargs)
    return wrapper

def current_user():
    uid = session.get("uid")
    return User.query.get(uid) if uid else None

@app.context_processor
def inject_globals():
    u = current_user()
    return {
        "user": u,
        "is_admin": bool(u and u.is_admin),
        "logged_in": bool(session.get("uid")),
        "paid_access": bool(u and has_active_access(u.id)),
        "t": t,
        "lang": get_lang()
    }
def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        uid = session.get("uid")
        u = User.query.get(uid) if uid else None
        if not u or not u.is_admin:
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/auth/register", methods=["GET","POST"])
def auth_register():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        name = request.form.get("name","").strip()
        password = request.form.get("password","")
        if not email or not password:
            return render_template("auth_register.html", error="Email and password required")
        if User.query.filter_by(email=email).first():
            return render_template("auth_register.html", error="Email already registered")
        u = User(email=email, name=name, password_hash=generate_password_hash(password), is_admin=(email=="rafael.athaydee@gmail.com"))
        db.session.add(u)
        db.session.commit()
        session["uid"] = u.id
        return redirect(url_for("dashboard"))
    return render_template("auth_register.html")

@app.route("/auth/login", methods=["GET","POST"])
def auth_login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        u = User.query.filter_by(email=email).first()
        if not u or not check_password_hash(u.password_hash, password):
            return render_template("auth_login.html", error="Invalid credentials")
        session["uid"] = u.id
        return redirect(url_for("dashboard"))
    return render_template("auth_login.html")

@app.route("/auth/logout")
def auth_logout():
    session.clear()
    return redirect(url_for("auth_login"))

@app.route("/i18n/set", methods=["GET","POST"])
def i18n_set():
    lang = request.values.get("lang","en")
    session["lang"] = "pt" if lang == "pt" else "en"
    ref = request.headers.get("Referer")
    return redirect(ref or url_for("dashboard"))
def has_active_access(uid):
    now = datetime.utcnow()
    q = LicenseKey.query.filter(LicenseKey.redeemed_by_user_id == uid, LicenseKey.status == "active")
    q = q.filter((LicenseKey.expires_at == None) | (LicenseKey.expires_at > now))
    return q.first() is not None
def require_paid(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        uid = session.get("uid")
        if not uid or not has_active_access(uid):
            return redirect(url_for("buy"))
        return f(*args, **kwargs)
    return wrapper
@app.route("/dashboard")
@require_login
def dashboard():
    uid = session.get("uid")
    low_stock = Product.query.filter(Product.user_id == uid, Product.stock < 5).order_by(Product.stock.asc()).limit(10).all()
    recent_sales = SalesOrder.query.filter(SalesOrder.user_id == uid).order_by(SalesOrder.date.desc()).limit(10).all()
    recent_purchases = PurchaseOrder.query.filter(PurchaseOrder.user_id == uid).order_by(PurchaseOrder.date.desc()).limit(10).all()
    product_count = db.session.query(func.count(Product.id)).filter(Product.user_id == uid).scalar()
    alerts = []
    low_count = db.session.query(func.count(Product.id)).filter(Product.user_id == uid, Product.stock < 5).scalar()
    if low_count > 0:
        alerts.append(f"{low_count} products are low on stock")
    now = datetime.utcnow()
    day = timedelta(days=1)
    s1 = db.session.query(func.coalesce(func.sum(SalesOrder.total), 0)).filter(SalesOrder.user_id == uid, SalesOrder.date >= now - day).scalar() or 0
    s2 = db.session.query(func.coalesce(func.sum(SalesOrder.total), 0)).filter(SalesOrder.user_id == uid, SalesOrder.date < now - day, SalesOrder.date >= now - day*2).scalar() or 0
    if s2 > 0 and s1 < s2 * 0.7:
        alerts.append("Sales have dropped compared to yesterday")
    badges = Achievement.query.filter(Achievement.user_id == uid).order_by(Achievement.unlocked_at.desc()).all()
    return render_template("index.html", low_stock=low_stock, recent_sales=recent_sales, recent_purchases=recent_purchases, product_count=product_count, alerts=alerts, badges=badges)

@app.route("/")
def landing():
    if session.get("uid"):
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/low-stock")
@require_login
def low_stock_view():
    uid = session.get("uid")
    items = Product.query.filter(Product.user_id == uid, Product.stock < 5).order_by(Product.stock.asc()).all()
    return render_template("low_stock.html", items=items)
@app.route("/api/stats")
@require_login
def api_stats():
    uid = session.get("uid")
    now = datetime.utcnow()
    day = timedelta(days=1)
    sales_today = db.session.query(func.coalesce(func.sum(SalesOrder.total), 0)).filter(SalesOrder.user_id == uid, SalesOrder.date >= now - day).scalar() or 0
    purchases_today = db.session.query(func.coalesce(func.sum(PurchaseOrder.total), 0)).filter(PurchaseOrder.user_id == uid, PurchaseOrder.date >= now - day).scalar() or 0
    low_stock_count = db.session.query(func.count(Product.id)).filter(Product.user_id == uid, Product.stock < 5).scalar()
    product_count = db.session.query(func.count(Product.id)).filter(Product.user_id == uid).scalar()
    prev_sales = db.session.query(func.coalesce(func.sum(SalesOrder.total), 0)).filter(SalesOrder.user_id == uid, SalesOrder.date < now - day, SalesOrder.date >= now - day*2).scalar() or 0
    drop = bool(prev_sales > 0 and sales_today < prev_sales * 0.7)
    return jsonify({"sales_today": float(sales_today or 0), "purchases_today": float(purchases_today or 0), "low_stock_count": int(low_stock_count or 0), "product_count": int(product_count or 0), "sales_drop": drop})
def _issue_key(plan):
    import secrets
    raw = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(16))
    code = "-".join([raw[i:i+4] for i in range(0, 16, 4)])
    now = datetime.utcnow()
    if plan == "monthly":
        exp = now.replace(microsecond=0) + timedelta(days=30)
    else:
        exp = now.replace(microsecond=0) + timedelta(days=365)
    lk = LicenseKey(code=code, plan=plan, expires_at=exp)
    db.session.add(lk)
    db.session.commit()
    return lk

@app.route("/buy")
@require_login
def buy():
    return render_template("buy.html")

@app.route("/buy/issue")
def buy_issue():
    plan = request.args.get("plan","monthly")
    if plan not in ("monthly","annual"):
        plan = "monthly"
    lk = _issue_key(plan)
    return render_template("buy_key.html", license_key=lk)

def _issue_paid_key(email, plan, source):
    now = datetime.utcnow()
    lk = _issue_key(plan)
    lk.issued_to_email = email
    lk.payment_source = source
    lk.status = "active"
    lk.currency = "USD" if source == "stripe" else "BRL"
    u = User.query.filter_by(email=email).first()
    if u:
        lk.redeemed_by_user_id = u.id
        lk.redeemed_at = datetime.utcnow()
    db.session.commit()
    return lk

@app.route("/buy/retrieve", methods=["POST"])
def buy_retrieve():
    email = request.form.get("email","").strip().lower()
    if not email:
        return redirect(url_for("buy"))
    lk = LicenseKey.query.filter(LicenseKey.issued_to_email == email, LicenseKey.redeemed_by_user_id == None).order_by(LicenseKey.created_at.desc()).first()
    if not lk:
        return render_template("buy.html", not_found=True)
    return render_template("buy_key.html", license_key=lk)

@app.route("/buy/key")
def buy_key():
    email = request.args.get("email","").strip().lower()
    if not email:
        return redirect(url_for("buy"))
    lk = LicenseKey.query.filter(LicenseKey.issued_to_email == email, LicenseKey.redeemed_by_user_id == None).order_by(LicenseKey.created_at.desc()).first()
    if not lk:
        return render_template("buy.html", not_found=True)
    return render_template("buy_key.html", license_key=lk)

@app.route("/buy/check_key")
def buy_check_key():
    email = request.args.get("email","").strip().lower()
    if not email:
        return jsonify({"found": False})
    lk = LicenseKey.query.filter(LicenseKey.issued_to_email == email, LicenseKey.redeemed_by_user_id == None).order_by(LicenseKey.created_at.desc()).first()
    if not lk:
        return jsonify({"found": False})
    return jsonify({"found": True, "code": lk.code, "plan": lk.plan, "expires": (lk.expires_at.isoformat() if lk.expires_at else None)})

@app.route("/buy/wait")
def buy_wait():
    email = request.args.get("email","").strip().lower()
    plan = request.args.get("plan","").strip().lower()
    return render_template("buy_wait.html", email=email, plan=plan)

@app.route("/buy/success")
def buy_success():
    return render_template("buy_success.html")

@app.route("/api/webhooks/stripe", methods=["POST"])
def api_webhooks_stripe():
    raw = request.get_data(cache=False, as_text=False)
    sig = request.headers.get("Stripe-Signature","")
    secret = _os.environ.get("STRIPE_WEBHOOK_SECRET","")
    valid = False
    try:
        parts = {}
        for p in sig.split(","):
            kv = p.split("=",1)
            if len(kv)==2:
                parts[kv[0].strip()] = kv[1].strip()
        payload = raw or b""
        import hmac, hashlib
        mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        if parts.get("v1") == mac:
            valid = True
    except Exception:
        valid = False
    if not valid:
        return "", 400
    data = request.get_json(force=True, silent=True) or {}
    et = data.get("type") or ""
    obj = (data.get("data") or {}).get("object") or {}
    email = (obj.get("customer_details") or {}).get("email") or obj.get("customer_email") or ""
    amt = obj.get("amount_total") or (obj.get("amount") or 0)
    status = obj.get("payment_status") or obj.get("status") or ""
    if et in ("checkout.session.completed","payment_intent.succeeded") and status in ("paid","succeeded","requires_capture",""):
        plan = "yearly" if (amt or 0) >= 1500 else "monthly"
        if email:
            email = email.strip().lower()
            _issue_paid_key(email, plan, "stripe")
    return "", 200

@app.route("/api/webhooks/mercadopago", methods=["POST"])
def api_webhooks_mercadopago():
    payload = request.get_json(force=True, silent=True) or {}
    notif_type = payload.get("type") or payload.get("action") or ""
    data_id = (payload.get("data") or {}).get("id") or payload.get("id")
    token = _os.environ.get("MERCADOPAGO_ACCESS_TOKEN","")
    if not token or not data_id:
        return "", 400
    import urllib.request, json as _json
    req = urllib.request.Request(
        f"https://api.mercadopago.com/v1/payments/{data_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            info = _json.loads(resp.read().decode("utf-8"))
    except Exception:
        info = {}
    status = info.get("status") or ""
    email = ((info.get("payer") or {}).get("email")) or ""
    amt = info.get("transaction_amount") or 0
    if status == "approved" and email:
        plan = "yearly" if (amt or 0) >= 100 else "monthly"
        _issue_paid_key(email.strip().lower(), plan, "mpago")
    return "", 200

@app.route("/products")
@require_login
@require_paid
def products_list():
    q = request.args.get("q", "").strip()
    uid = session.get("uid")
    if q:
        like = f"%{q.lower()}%"
        products = Product.query.filter(Product.user_id == uid).filter(
            or_(
                func.lower(Product.name).like(like),
                func.lower(Product.sku).like(like),
                func.lower(Product.category).like(like),
            )
        ).order_by(Product.name.asc()).all()
        groups = [("Search Results", products)]
        return render_template("products_list.html", groups=groups, q=q, search_mode=True)
    else:
        groups = []
        cats = Category.query.filter(Category.user_id == uid).order_by(Category.name.asc()).all()
        for c in cats:
            items = Product.query.filter(Product.user_id == uid, Product.category_id == c.id).order_by(Product.name.asc()).all()
            groups.append((c.name, items))
        uncats = Product.query.filter(Product.user_id == uid, Product.category_id == None).order_by(Product.name.asc()).all()
        if uncats:
            groups.insert(0, ("Uncategorized", uncats))
        return render_template("products_list.html", groups=groups, q="", search_mode=False)

@app.route("/products/<int:pid>/stock/increment", methods=["POST"])
@require_login
@require_paid
def product_stock_increment(pid):
    uid = session.get("uid")
    p = Product.query.get_or_404(pid)
    if p.user_id != uid:
        return redirect(url_for("products_list"))
    p.stock += 1
    mv = InventoryMovement(product_id=pid, change=1, reason="adjust", reference="ui", user_id=uid)
    db.session.add(mv)
    db.session.commit()
    return redirect(url_for("products_list"))

@app.route("/products/<int:pid>/stock/decrement", methods=["POST"])
@require_login
@require_paid
def product_stock_decrement(pid):
    uid = session.get("uid")
    p = Product.query.get_or_404(pid)
    if p.user_id != uid:
        return redirect(url_for("products_list"))
    if p.stock > 0:
        p.stock -= 1
        mv = InventoryMovement(product_id=pid, change=-1, reason="adjust", reference="ui", user_id=uid)
        db.session.add(mv)
    db.session.commit()
    return redirect(url_for("products_list"))

@app.route("/orders/<int:oid>/finish", methods=["POST"])
@require_login
@require_paid
def orders_finish(oid):
    uid = session.get("uid")
    o = SalesOrder.query.get_or_404(oid)
    if o.user_id != uid:
        return redirect(url_for("orders_list"))
    o.status = "finished"
    db.session.commit()
    return redirect(url_for("orders_list"))

@app.route("/products/new", methods=["GET", "POST"])
@require_login
@require_paid
def products_new():
    uid = session.get("uid")
    categories = Category.query.filter(Category.user_id == uid).order_by(Category.name.asc()).all()
    if request.method == "POST":
        sku = request.form.get("sku", "").strip()
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id")
        category = ""
        if category_id:
            cat = Category.query.get(int(category_id))
            category = cat.name if cat else ""
        price = float(request.form.get("price", "0") or 0)
        stock = int(request.form.get("stock", "0") or 0)
        try:
            p = Product(sku=sku, name=name, category=category, category_id=int(category_id) if category_id else None, price=price, stock=stock, created_at=datetime.utcnow(), user_id=uid)
            db.session.add(p)
            db.session.commit()
            check_achievements_post_product(uid)
            return redirect(url_for("dashboard"))
        except Exception as e:
            db.session.rollback()
            return render_template("product_form.html", product=None, categories=categories, error="Error creating product. Ensure SKU is unique for your account.")
    return render_template("product_form.html", product=None, categories=categories)

@app.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@require_login
@require_paid
def products_edit(pid):
    p = Product.query.get_or_404(pid)
    uid = session.get("uid")
    if p.user_id != uid:
        return redirect(url_for("products_list"))
    categories = Category.query.filter(Category.user_id == uid).order_by(Category.name.asc()).all()
    if request.method == "POST":
        p.sku = request.form.get("sku", "").strip()
        p.name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id")
        if category_id:
            cat = Category.query.get(int(category_id))
            p.category = cat.name if cat else ""
            p.category_id = int(category_id)
        p.price = float(request.form.get("price", "0") or 0)
        p.stock = int(request.form.get("stock", "0") or 0)
        db.session.commit()
        return redirect(url_for("products_list"))
    return render_template("product_form.html", product=p, categories=categories)

@app.route("/products/export")
@require_login
@require_paid
def products_export():
    uid = session.get("uid")
    rows = Product.query.filter(Product.user_id == uid).order_by(Product.name.asc()).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "sku", "name", "category", "price", "stock"])
    for r in rows:
        w.writerow([r.id, r.sku, r.name, r.category, r.price, r.stock])
    data = buf.getvalue().encode("utf-8")
    return send_file(io.BytesIO(data), mimetype="text/csv", as_attachment=True, download_name="products.csv")
 
@app.route("/categories/new", methods=["GET", "POST"])
@require_login
def categories_new():
    uid = session.get("uid")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name:
            try:
                c = Category(name=name, description=description, user_id=uid)
                db.session.add(c)
                db.session.commit()
                return redirect(url_for("products_new"))
            except Exception as e:
                db.session.rollback()
                return render_template("category_form.html", error="Category name must be unique within your account.")
    return render_template("category_form.html")

@app.route("/customers")
@require_login
@require_paid
def customers_list():
    q = request.args.get("q", "").strip().lower()
    uid = session.get("uid")
    query = Customer.query.filter(Customer.user_id == uid)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(func.lower(Customer.name).like(like), func.lower(Customer.email).like(like), func.lower(Customer.phone).like(like)))
    customers = query.order_by(Customer.name.asc()).all()
    return render_template("customers_list.html", customers=customers, q=q)

@app.route("/customers/bulk", methods=["GET", "POST"])
@require_login
@require_paid
def customers_bulk():
    uid = session.get("uid")
    if request.method == "POST":
        data = request.form.get("lines", "")
        for line in data.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if not parts or not parts[0]:
                continue
            name = parts[0]
            email = parts[1] if len(parts) > 1 else ""
            phone = parts[2] if len(parts) > 2 else ""
            c = Customer(name=name, email=email, phone=phone, user_id=uid)
            db.session.add(c)
        db.session.commit()
        return redirect(url_for("customers_list"))
    return render_template("customers_bulk.html")

@app.route("/suppliers")
@require_login
@require_paid
def suppliers_list():
    q = request.args.get("q", "").strip().lower()
    uid = session.get("uid")
    query = Supplier.query.filter(Supplier.user_id == uid)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(func.lower(Supplier.name).like(like), func.lower(Supplier.email).like(like), func.lower(Supplier.phone).like(like)))
    suppliers = query.order_by(Supplier.name.asc()).all()
    return render_template("suppliers_list.html", suppliers=suppliers, q=q)

@app.route("/suppliers/bulk", methods=["GET", "POST"])
@require_login
@require_paid
def suppliers_bulk():
    uid = session.get("uid")
    if request.method == "POST":
        data = request.form.get("lines", "")
        for line in data.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if not parts or not parts[0]:
                continue
            name = parts[0]
            email = parts[1] if len(parts) > 1 else ""
            phone = parts[2] if len(parts) > 2 else ""
            s = Supplier(name=name, email=email, phone=phone, user_id=uid)
            db.session.add(s)
        db.session.commit()
        return redirect(url_for("suppliers_list"))
    return render_template("suppliers_bulk.html")

@app.route("/orders")
@require_login
@require_paid
def orders_list():
    q = request.args.get("q", "").strip().lower()
    uid = session.get("uid")
    query = SalesOrder.query.filter(SalesOrder.user_id == uid).join(Customer, SalesOrder.customer_id == Customer.id)
    if q:
        like = f"%{q}%"
        query = query.filter(func.lower(Customer.name).like(like))
    orders = query.filter(SalesOrder.status != "finished").order_by(SalesOrder.date.desc()).all()
    return render_template("orders_list.html", orders=orders, q=q)

@app.route("/orders/new", methods=["GET", "POST"])
@require_login
@require_paid
def orders_new():
    uid = session.get("uid")
    customers = Customer.query.filter(Customer.user_id == uid).order_by(Customer.name.asc()).all()
    products = Product.query.filter(Product.user_id == uid).order_by(Product.name.asc()).all()
    if request.method == "POST":
        customer_id = int(request.form.get("customer_id"))
        order = SalesOrder(customer_id=customer_id, status="open", total=0, user_id=uid)
        db.session.add(order)
        db.session.flush()
        pids = request.form.getlist("product_id[]")
        qtys = request.form.getlist("quantity[]")
        for i in range(len(pids)):
            pid = int(pids[i])
            qty = int(qtys[i])
            product = Product.query.get(pid)
            unit_price = product.price
            item = SalesOrderItem(order_id=order.id, product_id=pid, quantity=qty, unit_price=unit_price)
            db.session.add(item)
            product.stock -= qty
            mv = InventoryMovement(product_id=pid, change=-qty, reason="sale", reference=str(order.id), user_id=uid)
            db.session.add(mv)
            order.total += unit_price * qty
        order.status = "closed"
        db.session.commit()
        check_achievements_post_sale(uid)
        return redirect(url_for("dashboard"))
    return render_template("order_form.html", customers=customers, products=products)

@app.route("/purchases")
@require_login
@require_paid
def purchases_list():
    q = request.args.get("q", "").strip().lower()
    uid = session.get("uid")
    query = PurchaseOrder.query.filter(PurchaseOrder.user_id == uid).join(Supplier, PurchaseOrder.supplier_id == Supplier.id)
    if q:
        like = f"%{q}%"
        query = query.filter(func.lower(Supplier.name).like(like))
    purchases = query.filter(PurchaseOrder.status != "finished").order_by(PurchaseOrder.date.desc()).all()
    return render_template("purchases_list.html", purchases=purchases, q=q)

@app.route("/purchases/new", methods=["GET", "POST"])
@require_login
@require_paid
def purchases_new():
    uid = session.get("uid")
    suppliers = Supplier.query.filter(Supplier.user_id == uid).order_by(Supplier.name.asc()).all()
    products = Product.query.filter(Product.user_id == uid).order_by(Product.name.asc()).all()
    if request.method == "POST":
        supplier_id = int(request.form.get("supplier_id"))
        po = PurchaseOrder(supplier_id=supplier_id, status="open", total=0, user_id=uid)
        db.session.add(po)
        db.session.flush()
        pids = request.form.getlist("product_id[]")
        qtys = request.form.getlist("quantity[]")
        costs = request.form.getlist("unit_cost[]")
        for i in range(len(pids)):
            pid = int(pids[i])
            qty = int(qtys[i])
            unit_cost = float(costs[i])
            item = PurchaseOrderItem(purchase_order_id=po.id, product_id=pid, quantity=qty, unit_cost=unit_cost)
            db.session.add(item)
            product = Product.query.get(pid)
            product.stock += qty
            mv = InventoryMovement(product_id=pid, change=qty, reason="purchase", reference=str(po.id), user_id=uid)
            db.session.add(mv)
            po.total += unit_cost * qty
        po.status = "closed"
        db.session.commit()
        check_achievements_post_purchase(uid)
        return redirect(url_for("dashboard"))
    return render_template("purchase_form.html", suppliers=suppliers, products=products)

@app.route("/purchases/<int:poid>/finish", methods=["POST"])
@require_login
def purchases_finish(poid):
    uid = session.get("uid")
    po = PurchaseOrder.query.get_or_404(poid)
    if po.user_id != uid:
        return redirect(url_for("purchases_list"))
    po.status = "finished"
    db.session.commit()
    return redirect(url_for("purchases_list"))

@app.route("/customers/new", methods=["GET", "POST"])
@require_login
def customers_new():
    uid = session.get("uid")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        c = Customer(name=name, email=email, phone=phone, user_id=uid)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("customer_form.html")

@app.route("/suppliers/new", methods=["GET", "POST"])
@require_login
def suppliers_new():
    uid = session.get("uid")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        s = Supplier(name=name, email=email, phone=phone, user_id=uid)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("supplier_form.html")

@app.route("/admin/users")
@require_login
@require_admin
def admin_users():
    q = request.args.get("q","").strip().lower()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(func.lower(User.name).like(like), func.lower(User.email).like(like)))
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=users, q=q)

@app.route("/admin/users/<int:uid>/edit", methods=["GET","POST"])
@require_login
@require_admin
def admin_user_edit(uid):
    u = User.query.get_or_404(uid)
    if request.method == "POST":
        u.name = request.form.get("name","").strip()
        u.email = request.form.get("email","").strip().lower()
        if request.form.get("password"):
            u.password_hash = generate_password_hash(request.form.get("password"))
        u.is_admin = bool(request.form.get("is_admin"))
        db.session.commit()
        return redirect(url_for("admin_users"))
    return render_template("admin_user_form.html", user=u)

@app.route("/admin/users/<int:uid>/delete", methods=["POST"])
@require_login
@require_admin
def admin_user_delete(uid):
    u = User.query.get_or_404(uid)
    InventoryMovement.query.filter(InventoryMovement.user_id == uid).delete()
    # delete order items first
    orders = SalesOrder.query.filter(SalesOrder.user_id == uid).all()
    for o in orders:
        SalesOrderItem.query.filter(SalesOrderItem.order_id == o.id).delete()
    SalesOrder.query.filter(SalesOrder.user_id == uid).delete()
    purchases = PurchaseOrder.query.filter(PurchaseOrder.user_id == uid).all()
    for p in purchases:
        PurchaseOrderItem.query.filter(PurchaseOrderItem.purchase_order_id == p.id).delete()
    PurchaseOrder.query.filter(PurchaseOrder.user_id == uid).delete()
    Product.query.filter(Product.user_id == uid).delete()
    Category.query.filter(Category.user_id == uid).delete()
    Customer.query.filter(Customer.user_id == uid).delete()
    Supplier.query.filter(Supplier.user_id == uid).delete()
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for("admin_users"))

@app.route("/admin/users/<int:uid>/reset_parties", methods=["POST"])
@require_login
@require_admin
def admin_user_reset_parties(uid):
    # reset customers and suppliers for a given user
    Customer.query.filter(Customer.user_id == uid).delete()
    Supplier.query.filter(Supplier.user_id == uid).delete()
    db.session.commit()
    return redirect(url_for("admin_users"))

@app.route("/admin/keys", methods=["GET","POST"])
@require_login
@require_admin
def admin_keys():
    if request.method == "POST":
        plan = request.form.get("plan","monthly")
        if plan not in ("monthly","annual"):
            plan = "monthly"
        lk = _issue_key(plan)
        return redirect(url_for("admin_keys"))
    keys = LicenseKey.query.order_by(LicenseKey.created_at.desc()).limit(50).all()
    return render_template("admin_keys.html", keys=keys)

@app.route("/settings", methods=["GET","POST"])
@require_login
def account_settings():
    uid = session.get("uid")
    u = User.query.get_or_404(uid)
    lk = LicenseKey.query.filter(LicenseKey.redeemed_by_user_id == uid).order_by(LicenseKey.redeemed_at.desc()).first()
    if request.method == "POST":
        code = request.form.get("license_key","").strip().upper()
        if code:
            lkx = LicenseKey.query.filter_by(code=code).first()
            if lkx and lkx.redeemed_by_user_id is None and (not lkx.expires_at or lkx.expires_at > datetime.utcnow()):
                lkx.redeemed_by_user_id = uid
                lkx.redeemed_at = datetime.utcnow()
                lkx.status = "active"
                db.session.commit()
                return redirect(url_for("dashboard"))
            else:
                return render_template("settings.html", license_key=lk, error="Invalid or expired key")
        color = request.form.get("theme_primary_color","#3b82f6")
        u.theme_primary_color = color
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("settings.html", license_key=lk)

@app.route("/account/activate_key", methods=["POST"])
@require_login
def account_activate_key():
    uid = session.get("uid")
    code = request.form.get("license_key","").strip().upper()
    if not code:
        return redirect(url_for("dashboard"))
    lk = LicenseKey.query.filter_by(code=code).first()
    if lk and lk.redeemed_by_user_id is None and (not lk.expires_at or lk.expires_at > datetime.utcnow()):
        lk.redeemed_by_user_id = uid
        lk.redeemed_at = datetime.utcnow()
        lk.status = "active"
        db.session.commit()
        return redirect(url_for("dashboard"))
    return redirect(url_for("dashboard"))

@app.route("/account/reset_parties", methods=["POST"])
@require_login
def account_reset_parties():
    uid = session.get("uid")
    Customer.query.filter(Customer.user_id == uid).delete()
    Supplier.query.filter(Supplier.user_id == uid).delete()
    db.session.commit()
    return redirect(url_for("customers_list"))

if __name__ == "__main__":
    app.run(debug=True)
