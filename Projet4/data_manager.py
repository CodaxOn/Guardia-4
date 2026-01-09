import csv, os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.path = "data"
        if not os.path.exists(self.path): os.makedirs(self.path)
        self.files = {
            'users': ('users.csv', ["id", "username", "mail", "password_hash", "salt", "role"]),
            # AJOUT DE "sn" à la fin de la liste ci-dessous
            'products': ('produit.csv', ["id", "name", "price", "stock", "description", "category", "sn"]),
            'logs': ('logs.csv', ["timestamp", "user", "action"])
        }
        for f, h in self.files.values():
            if not os.path.exists(os.path.join(self.path, f)):
                with open(os.path.join(self.path, f), 'w', newline='', encoding='utf-8') as file:
                    csv.DictWriter(file, fieldnames=h).writeheader()

    def get_data(self, key):
        with open(os.path.join(self.path, self.files[key][0]), 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def save_product(self, p):
        prods = self.get_data('products')
        p['id'] = str(max([int(x['id']) for x in prods] + [0]) + 1)
        with open(os.path.join(self.path, self.files['products'][0]), 'a', newline='', encoding='utf-8') as f:
            csv.DictWriter(f, fieldnames=self.files['products'][1]).writerow(p)

    def update_product(self, p_id, data):
        prods = self.get_data('products')
        for p in prods:
            if p['id'] == p_id: p.update(data)
        self._rewrite('products', prods)

    def delete_product(self, p_id):
        prods = [p for p in self.get_data('products') if p['id'] != p_id]
        self._rewrite('products', prods)

    def _rewrite(self, key, data):
        with open(os.path.join(self.path, self.files[key][0]), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=self.files[key][1])
            w.writeheader()
            w.writerows(data)

    def log(self, user, action):
        with open(os.path.join(self.path, self.files['logs'][0]), 'a', newline='', encoding='utf-8') as f:
            csv.DictWriter(f, fieldnames=self.files['logs'][1]).writerow({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": user, "action": action
            })