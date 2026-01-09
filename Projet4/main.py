import sys, os, datetime, random, csv, re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QFont, QPixmap, QIcon, QPainter, QBrush, QPen
import pyqtgraph as pg
import database
import time

# --- Protection brute force en mémoire ---
FAILED_ATTEMPTS = {}  # {username: {"count": int, "last_fail": timestamp}}
MAX_ATTEMPTS = 3
LOCK_TIME = 60  # secondes

class ProductDetailWindow(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Détails : {product['name']}")
        self.setFixedSize(450, 550)
        layout = QVBoxLayout(self)

        title = QLabel(product['name'].upper())
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(15)
        
        sn_display = product.get('sn') if product.get('sn') else product.get('description', 'N/A')
        
        fields = [
            ("Catégorie :", product['category']),
            ("Prix :", f"{product['price']} €"),
            ("Stock disponible :", product['stock']),
            ("ID Produit :", product['id']),
            ("N° Série Unique :", sn_display)
        ]
        for lab, val in fields:
            l = QLabel(val)
            l.setStyleSheet("font-size: 14px; background: #ecf0f1; padding: 5px; border-radius: 3px;")
            form.addRow(QLabel(lab), l)
        
        desc_label = QLabel("Description :")
        desc_area = QTextEdit(product.get('description', 'Aucune description disponible.'))
        desc_area.setReadOnly(True)
        desc_area.setMaximumHeight(100)
        form.addRow(desc_label, desc_area)
        layout.addLayout(form)

        self.btn_buy = QPushButton("🛒 AJOUTER AU PANIER")
        self.btn_buy.setStyleSheet("background: #27ae60; color: white; font-weight: bold; height: 45px;")
        self.btn_buy.clicked.connect(self.accept)
        layout.addWidget(self.btn_buy)

class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accès Système")
        self.setFixedSize(400, 450)

        self.logged_user = None
        self.user_mail = None

        # Champs
        self.u = QLineEdit()
        self.u.setPlaceholderText("Nom d'utilisateur")

        self.e = QLineEdit()
        self.e.setPlaceholderText("Email")

        self.p = QLineEdit()
        self.p.setPlaceholderText("Mot de passe")
        self.p.setEchoMode(QLineEdit.Password)

        self.btn = QPushButton("SE CONNECTER")
        self.toggle_btn = QPushButton("Créer un compte")
        self.toggle_btn.setFlat(True)

        layout = QVBoxLayout()
        title = QLabel("CONNEXION")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        layout.addWidget(self.u)
        layout.addWidget(self.e)
        layout.addWidget(self.p)
        layout.addWidget(self.btn)
        layout.addWidget(self.toggle_btn)
        layout.addStretch()

        self.setLayout(layout)

        # État : par défaut mode connexion -> cacher l'email
        self.e.hide()

        self.btn.clicked.connect(self.handle_auth)
        self.toggle_btn.clicked.connect(self.toggle)

    def toggle(self):
        """Bascule entre connexion et inscription."""
        if self.e.isVisible():
            self.e.hide()
            self.btn.setText("SE CONNECTER")
            self.toggle_btn.setText("Créer un compte")
        else:
            self.e.show()
            self.btn.setText("S'INSCRIRE")
            self.toggle_btn.setText("Déjà inscrit ? Se connecter")

    def handle_auth(self):
        username = self.u.text().strip()
        email = self.e.text().strip()
        password = self.p.text()

        if not re.match(r"^[a-zA-Z0-9]{3,15}$", username):
            QMessageBox.warning(self, "Pseudo Invalide", "Le pseudo doit faire entre 3 et 15 caractères.")
            return

        global FAILED_ATTEMPTS
        now = time.time()
        info = FAILED_ATTEMPTS.get(username)

        if info and info["count"] >= MAX_ATTEMPTS and now - info["last_fail"] < LOCK_TIME:
            remaining = int(LOCK_TIME - (now - info["last_fail"]))
            QMessageBox.warning(self, "Compte bloqué", f"Trop de tentatives. Attendez {remaining}s.")
            return

        if info and now - info["last_fail"] >= LOCK_TIME:
            FAILED_ATTEMPTS.pop(username, None)

        if self.e.isVisible():
            if "@" not in email or "." not in email:
                QMessageBox.warning(self, "Erreur", "Email invalide.")
                return
            if database.check_pwned_password(password):
                QMessageBox.critical(self, "SÉCURITÉ", "Mot de passe compromis !")
                return
            res, msg = database.register_user(username, email, password)
            if res:
                QMessageBox.information(self, "Info", msg)
                database.add_log(username, "AUDIT: Création de compte")
                self.toggle()
            else:
                QMessageBox.warning(self, "Erreur", "Pseudo déjà utilisé.")
            return

        success, mail_from_db = database.login_user(username, password)
        if success:
            FAILED_ATTEMPTS.pop(username, None)
            self.logged_user = username.lower()
            self.user_mail = mail_from_db
            database.add_log(self.logged_user, "AUDIT: Connexion réussie")
            self.accept()
        else:
            info = FAILED_ATTEMPTS.get(username, {"count": 0, "last_fail": 0})
            info["count"] += 1
            info["last_fail"] = now
            FAILED_ATTEMPTS[username] = info
            remaining = max(0, MAX_ATTEMPTS - info["count"])
            database.add_log(username, "AUDIT: Échec de connexion")
            QMessageBox.warning(self, "Erreur", f"Identifiants incorrects. Restant : {remaining}")

class MainWindow(QMainWindow):
    def __init__(self, user, mail):
        super().__init__()
        self.user, self.mail, self.cart = user, mail, []
        self.done_code = 0 
        self.setWindowTitle(f"Enterprise Manager - {self.user}")
        self.resize(1300, 900)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab_admin, self.tab_shop, self.tab_log, self.tab_stat, self.tab_prof = QWidget(), QWidget(), QWidget(), QWidget(), QWidget()
        
        self.tabs.addTab(self.tab_admin, "📦 GESTION")
        self.tabs.addTab(self.tab_shop, "🛒 BOUTIQUE")
        self.tabs.addTab(self.tab_log, "📝 LOGS")
        self.tabs.addTab(self.tab_stat, "📊 STATS")
        self.tabs.addTab(self.tab_prof, "👤 PROFIL")
        
        self.categories = ["Toutes Catégories", "Informatique", "Vêtements", "Sport", "Électronique", "Maison"]
        self.init_admin(); self.init_shop(); self.init_logs(); self.init_stats(); self.init_prof()

    def clean_price(self, val):
        if not val: return 0.0
        cleaned = re.sub(r'[^\d,.]', '', str(val)).replace(',', '.')
        try: return float(cleaned)
        except: return 0.0

    def _create_stat_card_admin(self, title, value, subtitle, color):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: white; border-radius: 12px; border: 1px solid #dee2e6; padding: 15px; }}")
        l = QVBoxLayout(card)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; border: none;")
        tit_lbl = QLabel(title.upper())
        tit_lbl.setStyleSheet("font-size: 11px; color: #64748b; font-weight: bold; border: none;")
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(f"font-size: 10px; color: {color}; background: #f8fafc; padding: 4px; border: none;")
        l.addWidget(val_lbl); l.addWidget(tit_lbl); l.addWidget(sub_lbl)
        return card

    def create_search(self, cb):
        l = QHBoxLayout()
        s = QLineEdit(); s.setPlaceholderText("Rechercher par nom..."); s.textChanged.connect(cb)
        sn_search = QLineEdit(); sn_search.setPlaceholderText("Rechercher par SN..."); sn_search.textChanged.connect(cb)
        c = QComboBox(); c.addItems(self.categories); c.currentTextChanged.connect(cb)
        btn_ref = QPushButton("🔄 Actualiser"); btn_ref.clicked.connect(cb); btn_ref.setFixedWidth(120)
        l.addWidget(s, 2); l.addWidget(sn_search, 2); l.addWidget(c, 1); l.addWidget(btn_ref)
        return l, s, c, sn_search

    def init_admin(self):
        layout = QVBoxLayout(self.tab_admin)
        f_lay, self.asrc, self.acat, self.asn = self.create_search(self.refresh_admin)
        btn = QPushButton("+ AJOUTER PRODUIT"); btn.clicked.connect(lambda: self.product_dialog())
        layout.addLayout(f_lay); layout.addWidget(btn, alignment=Qt.AlignLeft)
        self.table = QTableWidget(); self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID / SN", "Nom", "Prix", "Stock", "Modif", "Suppr"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table); self.refresh_admin()

    def refresh_admin(self):
        self.table.setRowCount(0); data = database.safe_read(database.FILE_PRODS)
        txt, cat, sn_txt = self.asrc.text().lower(), self.acat.currentText(), self.asn.text().lower()
        for d in data:
            if (txt in d['name'].lower()) and (cat == "Toutes Catégories" or cat == d['category']) and (sn_txt in d.get('sn', '').lower()):
                r = self.table.rowCount(); self.table.insertRow(r)
                display_id = f"{d['id']} | {d.get('sn', 'N/A')}"
                for i, v in enumerate([display_id, d['name'], d['price'], d['stock']]):
                    it = QTableWidgetItem(str(v)); it.setFlags(Qt.ItemIsEnabled); self.table.setItem(r, i, it)
                m, s = QPushButton("Modifier"), QPushButton("Supprimer")
                m.clicked.connect(lambda chk, rd=d: self.product_dialog(rd))
                s.clicked.connect(lambda chk, sn=d['id'], name=d['name']: self.del_prod(sn, name))
                self.table.setCellWidget(r, 4, m); self.table.setCellWidget(r, 5, s)

    def product_dialog(self, data=None):
        d = QDialog(self); d.setWindowTitle("Fiche Produit"); f = QFormLayout(d)
        n, p, q = QLineEdit(), QLineEdit(), QLineEdit(); desc = QTextEdit()
        c = QComboBox(); c.addItems(self.categories[1:])
        if data:
            n.setText(data['name']); p.setText(data['price']); q.setText(data['stock'])
            c.setCurrentText(data['category']); desc.setText(data.get('description', ''))
        btn = QPushButton("ENREGISTRER")
        f.addRow("Nom:", n); f.addRow("Prix:", p); f.addRow("Stock:", q); f.addRow("Cat:", c); f.addRow("Description:", desc); f.addRow(btn)
        def save():
            sn_val = data.get('sn') if data and data.get('sn') else f"SN-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            new_v = {'name': n.text(), 'price': p.text(), 'stock': q.text(), 'category': c.currentText(), 'description': desc.toPlainText(), 'sn': sn_val}
            if data: database.dm.update_product(data['id'], new_v)
            else: database.dm.save_product(new_v)
            self.refresh_admin(); self.refresh_shop(); self.init_stats(); self.init_logs(); d.accept()
        btn.clicked.connect(save); d.exec_()

    def del_prod(self, p_id, name):
        if QMessageBox.question(self, "Sûr ?", f"Supprimer {name} ?") == QMessageBox.Yes:
            database.dm.delete_product(p_id)
            self.refresh_admin(); self.refresh_shop(); self.init_stats(); self.init_logs()

    def init_shop(self):
        layout = QVBoxLayout(self.tab_shop)
        f_lay, self.ssrc, self.scat, _ = self.create_search(self.refresh_shop)
        layout.addLayout(f_lay)
        self.shop_table = QTableWidget(); self.shop_table.setColumnCount(4)
        self.shop_table.setHorizontalHeaderLabels(["Produit", "Catégorie", "Prix", "Détails"])
        self.shop_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shop_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.shop_table); self.refresh_shop()

    def refresh_shop(self):
        self.shop_table.setRowCount(0); data = database.safe_read(database.FILE_PRODS)
        txt, cat = self.ssrc.text().lower(), self.scat.currentText()
        for p in data:
            if (txt in p['name'].lower()) and (cat == "Toutes Catégories" or cat == p['category']):
                r = self.shop_table.rowCount(); self.shop_table.insertRow(r)
                self.shop_table.setItem(r, 0, QTableWidgetItem(p['name']))
                self.shop_table.setItem(r, 1, QTableWidgetItem(p['category']))
                self.shop_table.setItem(r, 2, QTableWidgetItem(f"{p['price']} €"))
                btn_view = QPushButton("VOIR")
                btn_view.clicked.connect(lambda chk, item=p: self.open_product_details(item))
                self.shop_table.setCellWidget(r, 3, btn_view)

    def open_product_details(self, product):
        dialog = ProductDetailWindow(product, self)
        if dialog.exec_() == QDialog.Accepted:
            self.cart.append(product)
            self.init_prof() # Met à jour l'affichage du panier
            QMessageBox.information(self, "Panier", "Ajouté !")

    def init_logs(self):
        if not self.tab_log.layout(): layout = QVBoxLayout(self.tab_log)
        else:
            layout = self.tab_log.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
        tool_bar = QHBoxLayout()
        btn_refresh_logs = QPushButton("🔄 Actualiser les Logs")
        btn_refresh_logs.setFixedWidth(200); btn_refresh_logs.clicked.connect(self.init_logs)
        tool_bar.addWidget(btn_refresh_logs); tool_bar.addStretch(); layout.addLayout(tool_bar)
        table = QTableWidget(); table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Date", "Utilisateur", "Action", "N° Série"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for row in reversed(database.safe_read(database.FILE_LOGS)):
            idx = table.rowCount(); table.insertRow(idx)
            action_text = row.get('action', '')
            table.setItem(idx, 0, QTableWidgetItem(row.get('timestamp', '')))
            table.setItem(idx, 1, QTableWidgetItem(row.get('user', '')))
            table.setItem(idx, 2, QTableWidgetItem(action_text))
            sn_match = re.search(r'\((SN-[^)]+)\)', action_text)
            if sn_match:
                sn_found = sn_match.group(1); container = QWidget()
                lay = QHBoxLayout(container); lay.setContentsMargins(5, 2, 5, 2)
                lbl = QLabel(sn_found); btn_cp = QPushButton("Copier")
                btn_cp.setFixedWidth(60); btn_cp.clicked.connect(lambda chk, s=sn_found: QApplication.clipboard().setText(s))
                lay.addWidget(lbl); lay.addWidget(btn_cp); table.setCellWidget(idx, 3, container)
            else: table.setItem(idx, 3, QTableWidgetItem("-"))
        layout.addWidget(table)

    def init_stats(self):
        if self.tab_stat.layout():
            layout = self.tab_stat.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
        else: 
            layout = QVBoxLayout(self.tab_stat)
            layout.setContentsMargins(30, 30, 30, 30)

        orders = database.safe_read("commandes.csv")
        total_ca = sum(self.clean_price(o.get('total', 0)) for o in orders)
        product_counts = {}
        for o in orders:
            name = o.get('nom_prod', 'Inconnu')
            product_counts[name] = product_counts.get(name, 0) + 1
        
        # --- MODIFICATION : Tri par volume de vente décroissant ---
        top_5 = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        header = QLabel("📊 TABLEAU DE BORD DE PERFORMANCE")
        header.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e293b; margin-bottom: 15px;")
        layout.addWidget(header)

        top_grid = QGridLayout()
        top_grid.addWidget(self._create_stat_card_admin("Chiffre d'Affaires", f"{total_ca:,.2f} €", "💰 Cumul total", "#22c55e"), 0, 0)
        top_grid.addWidget(self._create_stat_card_admin("Total Ventes", str(len(orders)), "📦 Unités vendues", "#6366f1"), 0, 1)
        top_grid.addWidget(self._create_stat_card_admin("Produits Uniques", str(len(product_counts)), "🏷️ Références", "#f59e0b"), 0, 2)
        layout.addLayout(top_grid)

        middle_layout = QHBoxLayout()
        chart_card = QFrame()
        chart_card.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px;")
        chart_v = QVBoxLayout(chart_card)
        chart_v.addWidget(QLabel("<b>📈 TENDANCE DES VENTES</b>"))
        graphWidget = pg.PlotWidget(); graphWidget.setBackground('w')
        last_orders = orders[-15:]; montants = [self.clean_price(o.get('total', 0)) for o in last_orders]
        if montants: graphWidget.plot(range(len(montants)), montants, pen=pg.mkPen('#6366f1', width=3), symbol='o', symbolBrush='#10b981')
        chart_v.addWidget(graphWidget); middle_layout.addWidget(chart_card, 2)

        top_card = QFrame()
        top_card.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;")
        top_v = QVBoxLayout(top_card); top_v.addWidget(QLabel("<b>🏆 TOP 5 MEILLEURES VENTES</b>"))
        for i, (name, count) in enumerate(top_5):
            item_widget = QWidget(); item_l = QHBoxLayout(item_widget); item_l.setContentsMargins(0, 5, 0, 5)
            rank = QLabel(f"#{i+1}"); rank.setStyleSheet(f"font-weight: bold; color: {'#f59e0b' if i==0 else '#64748b'}; font-size: 16px;")
            p_name = QLabel(name); p_name.setStyleSheet("font-size: 13px; color: #1e293b;")
            qty = QLabel(f"{count} ventes"); qty.setStyleSheet("background: #f1f5f9; padding: 2px 8px; border-radius: 10px; font-size: 11px;")
            item_l.addWidget(rank); item_l.addWidget(p_name, 1); item_l.addWidget(qty); top_v.addWidget(item_widget)
        top_v.addStretch(); middle_layout.addWidget(top_card, 1); layout.addLayout(middle_layout); layout.addStretch()

    def init_prof(self):
        if self.tab_prof.layout():
            layout = self.tab_prof.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
                elif child.layout(): 
                    self.clear_layout(child.layout())
        else:
            layout = QHBoxLayout(self.tab_prof)
            layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

        sidebar = QFrame(); sidebar.setFixedWidth(350); sidebar.setStyleSheet("background-color: #f8f9fa; border-right: 1px solid #dee2e6;")
        side_lyt = QVBoxLayout(sidebar); side_lyt.setContentsMargins(0, 20, 0, 0)
        self.avatar_label = QLabel(); self.avatar_label.setFixedSize(120, 120); self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("background: #ddd; border-radius: 60px; border: 2px solid #333; color: black;"); self.avatar_label.setText("PHOTO")
        btn_change_photo = QPushButton("Modifier la photo"); btn_change_photo.setFixedWidth(160); btn_change_photo.clicked.connect(self.change_avatar)
        name_label = QLabel(self.user.title()); name_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
        mail_label = QLabel(self.mail); mail_label.setStyleSheet("color: #666; font-size: 14px; margin-bottom: 20px;")
        for w in [self.avatar_label, btn_change_photo, name_label, mail_label]: side_lyt.addWidget(w, 0, Qt.AlignCenter)
        side_lyt.addStretch(); 
        
        # --- MODIFICATION : Le bouton déconnexion utilise self.logout ---
        btn_logout = QPushButton("↪ Me déconnecter")
        btn_logout.setFixedHeight(60); btn_logout.clicked.connect(self.logout)
        btn_logout.setStyleSheet("background: black; color: white; font-weight: bold; border: none;")
        side_lyt.addWidget(btn_logout)

        content = QFrame(); content_lyt = QVBoxLayout(content)
        content_lyt.addWidget(QLabel("<h2>🛒 Mon Panier</h2>"))
        self.pt = QTableWidget(); self.pt.setColumnCount(3); self.pt.setHorizontalHeaderLabels(["Article", "Prix", "Action"])
        self.pt.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.pt.setFixedHeight(180)
        for i, it in enumerate(self.cart):
            r = self.pt.rowCount(); self.pt.insertRow(r)
            self.pt.setItem(r, 0, QTableWidgetItem(it['name'])); self.pt.setItem(r, 1, QTableWidgetItem(f"{it['price']} €"))
            btn_rm = QPushButton("Retirer"); btn_rm.clicked.connect(lambda chk, idx=i: (self.cart.pop(idx), self.init_prof()))
            self.pt.setCellWidget(r, 2, btn_rm)
        content_lyt.addWidget(self.pt)
        total = sum(self.clean_price(it['price']) for it in self.cart)
        btn_pay = QPushButton(f"VALIDER L'ACHAT ({total:.2f} €)"); btn_pay.setStyleSheet("background: #22c55e; color: white; height: 40px; font-weight: bold;")
        btn_pay.clicked.connect(self.pay); content_lyt.addWidget(btn_pay); content_lyt.addSpacing(20)
        content_lyt.addWidget(QLabel("<h2>📦 Historique de mes commandes</h2>"))
        self.order_t = QTableWidget(); self.order_t.setColumnCount(5)
        self.order_t.setHorizontalHeaderLabels(["ID Prod", "Date", "Article", "N° Série", "Total"])
        self.order_t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for o in reversed(database.safe_read("commandes.csv")):
            if o['user'] == self.user:
                r = self.order_t.rowCount(); self.order_t.insertRow(r)
                self.order_t.setItem(r, 0, QTableWidgetItem(o.get('id_prod', 'N/A')))
                self.order_t.setItem(r, 1, QTableWidgetItem(o['date']))
                self.order_t.setItem(r, 2, QTableWidgetItem(o['nom_prod']))
                self.order_t.setItem(r, 3, QTableWidgetItem(o.get('sn', 'N/A')))
                self.order_t.setItem(r, 4, QTableWidgetItem(o['total']))
        content_lyt.addWidget(self.order_t); layout.addWidget(sidebar); layout.addWidget(content, 1)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None: widget.deleteLater()
                else: self.clear_layout(item.layout())

    def change_avatar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir une photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            original = QPixmap(path); size = 120; min_dim = min(original.width(), original.height())
            square_pix = original.copy((original.width()-min_dim)//2, (original.height()-min_dim)//2, min_dim, min_dim)
            out_img = QPixmap(size, size); out_img.fill(Qt.transparent)
            painter = QPainter(out_img); painter.setRenderHint(QPainter.Antialiasing)
            path_circle = QBrush(square_pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            painter.setBrush(path_circle); painter.setPen(Qt.NoPen); painter.drawEllipse(0, 0, size, size); painter.end()
            self.avatar_label.setPixmap(out_img); self.avatar_label.setText("")

    def pay(self):
        if not self.cart: return
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        path_cmd = os.path.join('data', 'commandes.csv')
        if not os.path.exists('data'): os.makedirs('data')
        with open(path_cmd, 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if os.path.getsize(path_cmd) == 0:
                w.writerow(["id_order", "user", "total", "status", "date", "id_prod", "nom_prod", "sn"])
            for it in self.cart:
                sn_val = it.get('sn', 'N/A'); order_id = f"ORD-{random.randint(1000, 9999)}"
                w.writerow([order_id, self.user, f"{it['price']}€", "Payé", now, it['id'], it['name'], sn_val])
                database.add_log(self.user, f"AUDIT: Achat {it['name']} (ID:{it['id']} / SN:{sn_val})")
        self.cart = []; self.init_prof(); self.init_stats(); self.init_logs()
        QMessageBox.information(self, "Succès", "Achat réussi !")

    def logout(self): 
        database.add_log(self.user, "AUDIT: Déconnexion")
        self.done_code = 99; self.close()

if __name__ == "__main__":
    while True: 
        app = QApplication(sys.argv)
        if os.path.exists("style.qss"):
            with open("style.qss", "r", encoding="utf-8") as f: app.setStyleSheet(f.read())
        auth = AuthWindow()
        if auth.exec_() == QDialog.Accepted:
            m = MainWindow(auth.logged_user, auth.user_mail); m.show(); app.exec_() 
            if m.done_code != 99: break
        else: break