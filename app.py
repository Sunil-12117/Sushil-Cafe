from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# ── CORS — sabhi domains allow ──
CORS(app)

# ── Environment Variables ──
MONGO_URI      = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'sushil@123')

# ── MongoDB — Lazy connection ──
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
db = client['sushil_cafe']

menu_col         = db['menu']
reservations_col = db['reservations']
feedback_col     = db['feedback']
orders_col       = db['orders']

def fix_id(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

def fix_ids(docs):
    return [fix_id(d) for d in docs]


# ── Health Check ──
@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    try:
        client.admin.command('ping')
        mongo_status = 'connected'
    except Exception as e:
        mongo_status = f'error: {str(e)}'
    return jsonify({'success': True, 'status': 'online', 'mongodb': mongo_status})


# ── Auth ──
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json or {}
        if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
            return jsonify({'success': True, 'message': 'Login successful'})
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Menu ──
@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        items = fix_ids(list(menu_col.find()))
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    try:
        data = request.json or {}
        if not data.get('name') or not data.get('price'):
            return jsonify({'success': False, 'message': 'Name aur price required hai'}), 400
        item = {
            'name': data['name'],
            'price': int(data['price']),
            'category': data.get('category', 'Starter'),
            'img': data.get('img', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'),
            'createdAt': datetime.now().isoformat()
        }
        result = menu_col.insert_one(item)
        item['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': item}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/menu/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    try:
        result = menu_col.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Item nahi mila'}), 404
        return jsonify({'success': True, 'message': 'Item delete ho gaya'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Reservations ──
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        items = fix_ids(list(reservations_col.find().sort('createdAt', -1)))
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    try:
        data = request.json or {}
        if not data.get('name') or not data.get('phone'):
            return jsonify({'success': False, 'message': 'Name aur phone required hai'}), 400
        reservation = {
            'name': data['name'],
            'phone': data['phone'],
            'date': data.get('date', ''),
            'time': data.get('time', ''),
            'guests': data.get('guests', '2 People'),
            'status': 'Pending',
            'createdAt': datetime.now().isoformat()
        }
        result = reservations_col.insert_one(reservation)
        reservation['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': reservation}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reservations/<res_id>', methods=['PUT'])
def update_reservation(res_id):
    try:
        data = request.json or {}
        reservations_col.update_one(
            {'_id': ObjectId(res_id)},
            {'$set': {'status': data.get('status', 'Pending')}}
        )
        return jsonify({'success': True, 'message': 'Status update ho gaya'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Feedback ──
@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    try:
        items = fix_ids(list(feedback_col.find().sort('createdAt', -1)))
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/feedback', methods=['POST'])
def add_feedback():
    try:
        data = request.json or {}
        if not data.get('name') or not data.get('message'):
            return jsonify({'success': False, 'message': 'Name aur message required hai'}), 400
        feedback = {
            'name': data['name'],
            'rating': int(data.get('rating', 5)),
            'message': data['message'],
            'createdAt': datetime.now().isoformat()
        }
        result = feedback_col.insert_one(feedback)
        feedback['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': feedback}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Orders ──
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        items = fix_ids(list(orders_col.find().sort('createdAt', -1)))
        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500

@app.route('/api/orders', methods=['POST'])
def add_order():
    try:
        data = request.json or {}
        order = {
            'orderId': f"ORD-{int(datetime.now().timestamp())}",
            'items': data.get('items', []),
            'address': data.get('address', ''),
            'phone': data.get('phone', ''),
            'payment': data.get('payment', 'UPI'),
            'total': int(data.get('total', 0)),
            'status': 'Preparing',
            'createdAt': datetime.now().isoformat()
        }
        result = orders_col.insert_one(order)
        order['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'data': order}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json or {}
        orders_col.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': data.get('status', 'Preparing')}}
        )
        return jsonify({'success': True, 'message': 'Order status update ho gaya'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ── Stats ──
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_orders   = orders_col.count_documents({})
        completed      = list(orders_col.find({'status': 'Completed'}))
        total_revenue  = sum(o.get('total', 0) for o in completed)
        reservations   = reservations_col.count_documents({})
        pending_res    = reservations_col.count_documents({'status': 'Pending'})
        feedback_count = feedback_col.count_documents({})
        feedbacks      = list(feedback_col.find())
        avg_rating     = round(sum(f.get('rating', 5) for f in feedbacks) / len(feedbacks), 1) if feedbacks else 5.0
        return jsonify({
            'success': True,
            'data': {
                'totalRevenue': total_revenue,
                'totalOrders': total_orders,
                'reservations': reservations,
                'pendingReservations': pending_res,
                'feedbackCount': feedback_count,
                'avgRating': avg_rating
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
