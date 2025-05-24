from supabase import create_client

class User:
    def __init__(self):
        self.base_url = "https://cgogqyorfzpxaiotscfp.supabase.co"
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnb2dxeW9yZnpweGFpb3RzY2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5ODMyMzcsImV4cCI6MjA2MzU1OTIzN30.enehR9wGHJf1xKO7d4XBbmjfdm80EvBKzaaPO3NPVAM'
        self.supabase = create_client(self.base_url, self.token)

    def get_all_users(self):
        res = self.supabase.table("data_user").select("*").execute()
        return res.data if res.data else []

    def get_user_by_username(self, username):
        res = self.supabase.table("data_user").select("*").eq("username", username).execute()
        if res.data and len(res.data) > 0:
            user = res.data[0]
            # Đảm bảo có balance và purchases
            if 'balance' not in user or user['balance'] is None:
                user['balance'] = 0
            if 'purchases' not in user or user['purchases'] is None:
                user['purchases'] = []
            return user
        return None

    def register_user(self, username, password, email):
        # Kiểm tra tồn tại
        if self.get_user_by_username(username):
            return False
        try:
            self.supabase.table("data_user").insert({
                "username": username,
                "password": password,
                "email": email,
                "balance": 0,
                "purchases": []
            }).execute()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def update_purchase_version_client(self, username, purchase_id, new_version_client):
        user = self.get_user_by_username(username)
        if not user:
            return False
        purchases = user.get('purchases', [])
        updated = False
        for p in purchases:
            if p['id'] == purchase_id:
                p['version_client'] = new_version_client
                updated = True
                break
        if not updated:
            return False
        try:
            self.supabase.table("data_user").update({"purchases": purchases}).eq("username", username).execute()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    def login_user(self, username, password):
        user = self.get_user_by_username(username)
        return user and user['password'] == password

    def get_user_purchases(self, username):
        user = self.get_user_by_username(username)
        return user['purchases'] if user and 'purchases' in user else []

    def update_purchases(self, username, purchases):
        try:
            self.supabase.table("data_user").update({"purchases": purchases}).eq("username", username).execute()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def add_balance(self, username, amount):
        user = self.get_user_by_username(username)
        if not user:
            return False
        new_balance = user.get('balance', 0) + amount
        try:
            self.supabase.table("data_user").update({"balance": new_balance}).eq("username", username).execute()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    
    def get_transactions(self):
        try:
            res = self.supabase.table("transactions").select("*").execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def check_user_has_product(self, username, product_id):
        purchases = self.get_user_purchases(username)
        return any(p['product_id'] == product_id for p in purchases)

    def purchase_product(self, username, product_id, key, price, version_client, date_key_part):
        user = self.get_user_by_username(username)
        if not user:
            return False
        # Trừ tiền
        if int(user['balance'])< int(price):
            return False
        
        new_balance = int(user['balance']) - int(price)
        purchases = user.get('purchases', [])
        purchase = {
            'id': len(purchases) + 1,
            'product_id': product_id,
            'download_count': 0,
            'purchase_date': 'Hôm nay',
            'key': key,
            'version_client': version_client,
            'date_key_part': date_key_part,
        }
        purchases.append(purchase)
        try:
            self.supabase.table("data_user").update({
                "balance": new_balance,
                "purchases": purchases
            }).eq("username", username).execute()
            # Ghi log giao dịch nếu muốn
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def get_purchase_by_id(self, purchase_id, username):
        purchases = self.get_user_purchases(username)
        for p in purchases:
            if p['id'] == purchase_id:
                return p
        return None

    def increment_download_count(self, purchase_id, username, version_client):
        user = self.get_user_by_username(username)
        if not user:
            return False
        purchases = user.get('purchases', [])
        for p in purchases:
            if p['id'] == purchase_id:
                p['download_count'] = p.get('download_count', 0) + 1
        try:
            self.supabase.table("data_user").update({"purchases": purchases,"version_client":version_client}).eq("username", username).execute()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False