from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
import threading
import certifi

app = Flask(__name__)
CORS(app)

MONGO_URI      = os.environ.get('MONGO_URI', '')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'sushil@123')

# MongoDB — background mein connect karo (startup block nahi karega)
db = None
def connect_mongo():
    global db
    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=30000,
            tlsCAFile=certifi.where()   # SSL fix
        )
        db = client['sushil_cafe']
        db.list_collection_names()
        print("✅ MongoDB connected!")
    except Exception as e:
        print(f"❌ MongoDB error: {e}")

threading.Thread(target=connect_mongo, daemon=True).start()

def get_col(name):
    if db is None:
        raise Exception("Database not connected yet. Try again in a moment.")
    return db[name]

def fix_id(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def fix_ids(docs):
    return [fix_id(d) for d in docs]

# ── Health ──
@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    status = 'connected' if db is not None else 'connecting...'
    return jsonify({'success': True, 'status': 'online', 'mongodb': status})

# ── Auth ──
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# ── Menu ──
@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        return jsonify({'success': True, 'data': fix_ids(list(get_col('menu').find()))})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/menu', methods=['POST'])
def add_menu():
    try:
        data = request.json or {}
        item = {
            'name': data['name'], 'price': int(data['price']),
            'category': data.get('category', 'Starter'),
            'img': data.get('img', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'),
            'createdAt': datetime.now().isoformat()
        }
        result = get_col('menu').insert_one(item)
        item['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': item}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/menu/<item_id>', methods=['DELETE'])
def delete_menu(item_id):
    try:
        get_col('menu').delete_one({'_id': ObjectId(item_id)})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── Reservations ──
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        return jsonify({'success': True, 'data': fix_ids(list(get_col('reservations').find().sort('createdAt', -1)))})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    try:
        data = request.json or {}
        res = {
            'name': data.get('name',''), 'phone': data.get('phone',''),
            'date': data.get('date',''), 'time': data.get('time',''),
            'guests': data.get('guests','2 People'),
            'status': 'Pending', 'createdAt': datetime.now().isoformat()
        }
        result = get_col('reservations').insert_one(res)
        res['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': res}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reservations/<res_id>', methods=['PUT'])
def update_reservation(res_id):
    try:
        data = request.json or {}
        get_col('reservations').update_one({'_id': ObjectId(res_id)}, {'$set': {'status': data.get('status','Pending')}})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── Feedback ──
@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    try:
        return jsonify({'success': True, 'data': fix_ids(list(get_col('feedback').find().sort('createdAt', -1)))})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/feedback', methods=['POST'])
def add_feedback():
    try:
        data = request.json or {}
        fb = {
            'name': data.get('name',''), 'rating': int(data.get('rating', 5)),
            'message': data.get('message',''), 'createdAt': datetime.now().isoformat()
        }
        result = get_col('feedback').insert_one(fb)
        fb['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': fb}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── Orders ──
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        return jsonify({'success': True, 'data': fix_ids(list(get_col('orders').find().sort('createdAt', -1)))})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/orders', methods=['POST'])
def add_order():
    try:
        data = request.json or {}
        order = {
            'orderId': 'ORD-' + str(int(datetime.now().timestamp())),
            'items': data.get('items', []),
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'address': data.get('address', ''),
            'payment': data.get('payment', 'UPI'),
            'subtotal': int(data.get('subtotal', 0)),
            'gst': int(data.get('gst', 0)),
            'total': int(data.get('total', 0)),
            'status': 'Preparing',
            'createdAt': datetime.now().isoformat()
        }
        result = get_col('orders').insert_one(order)
        order['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': order}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json or {}
        get_col('orders').update_one({'_id': ObjectId(order_id)}, {'$set': {'status': data.get('status','Preparing')}})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ── Stats ──
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        orders    = list(get_col('orders').find())
        completed = [o for o in orders if o.get('status') == 'Completed']
        revenue   = sum(o.get('total', 0) for o in completed)
        res_count = get_col('reservations').count_documents({})
        fb_list   = list(get_col('feedback').find())
        avg_rating = round(sum(f.get('rating',5) for f in fb_list) / len(fb_list), 1) if fb_list else 5.0
        return jsonify({'success': True, 'data': {
            'totalRevenue': revenue, 'totalOrders': len(orders),
            'reservations': res_count, 'feedbackCount': len(fb_list), 'avgRating': avg_rating
        }})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
