from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend connection

# ----------------- DATABASE SETUP -----------------
def create_database():
    conn = sqlite3.connect('tanglecoind.db')
    cursor = conn.cursor()

    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')

    # Create wallets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL UNIQUE,
            balance REAL DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# ----------------- FRONTEND ROUTES -----------------
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/wallet.html')
def wallet():
    return send_from_directory('../frontend', 'wallet.html')

@app.route('/transaction.html')
def transaction():
    return send_from_directory('../frontend', 'transaction.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/dag.html')
def dag():
    return send_from_directory('../frontend', 'dag.html')

# ----------------- WALLET ENDPOINTS -----------------
# Create a new wallet with balance
@app.route('/create_wallet', methods=['POST'])
def create_wallet():
    try:
        data = request.get_json()
        owner = data.get('owner')
        balance = float(data.get('balance', 0))

        if not owner:
            return jsonify({'error': 'Owner name is required'}), 400
        
        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO wallets (owner, balance) VALUES (?, ?)', (owner, balance))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Wallet already exists'}), 400
        
        conn.close()
        return jsonify({'message': 'Wallet created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

# ----------------- TRANSACTION ENDPOINTS -----------------
# Add a new transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        data = request.get_json()
        sender = data.get('sender')
        receiver = data.get('receiver')
        amount = float(data.get('amount'))

        if not sender or not receiver or amount <= 0:
            return jsonify({'error': 'Invalid transaction data'}), 400
        
        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()

        # Check if sender wallet exists and has enough funds
        cursor.execute('SELECT balance FROM wallets WHERE owner = ?', (sender,))
        sender_wallet = cursor.fetchone()

        if not sender_wallet:
            conn.close()
            return jsonify({'error': 'Sender wallet does not exist'}), 404
        
        if sender_wallet[0] < amount:
            conn.close()
            return jsonify({'error': 'Insufficient funds'}), 400

        # Check if receiver wallet exists
        cursor.execute('SELECT balance FROM wallets WHERE owner = ?', (receiver,))
        receiver_wallet = cursor.fetchone()

        if not receiver_wallet:
            conn.close()
            return jsonify({'error': 'Receiver wallet does not exist'}), 404

        # Record transaction
        cursor.execute(
            'INSERT INTO transactions (sender, receiver, amount) VALUES (?, ?, ?)',
            (sender, receiver, amount)
        )

        # Update sender and receiver balances
        cursor.execute('UPDATE wallets SET balance = balance - ? WHERE owner = ?', (amount, sender))
        cursor.execute('UPDATE wallets SET balance = balance + ? WHERE owner = ?', (amount, receiver))

        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Transaction added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all transactions
@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    try:
        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()
        cursor.execute('SELECT sender, receiver, amount FROM transactions')
        transactions = cursor.fetchall()
        conn.close()

        transaction_data = [
            {'sender': tx[0], 'receiver': tx[1], 'amount': tx[2]}
            for tx in transactions
        ]
        return jsonify(transaction_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Get all wallets
@app.route('/get_all_wallets', methods=['GET'])
def get_all_wallets():
    try:
        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()
        cursor.execute('SELECT owner, balance FROM wallets')
        wallets = cursor.fetchall()
        conn.close()

        wallet_data = [
            {'owner': wallet[0], 'balance': wallet[1]}
            for wallet in wallets
        ]
        return jsonify(wallet_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Get Wallet Balance
@app.route('/get_wallet_balance', methods=['GET'])
def get_wallet_balance():
    try:
        owner = request.args.get('owner')
        if not owner:
            return jsonify({'error': 'Owner name is required'}), 400

        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM wallets WHERE owner = ?', (owner,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return jsonify({'owner': owner, 'balance': result[0]}), 200
        else:
            return jsonify({'error': 'Wallet not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- DAG ENDPOINT -----------------
@app.route('/get_dag', methods=['GET'])
def get_dag():
    try:
        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()
        cursor.execute('SELECT sender, receiver, amount FROM transactions')
        transactions = cursor.fetchall()
        conn.close()

        dag_data = [{
            'sender': tx[0],
            'receiver': tx[1],
            'amount': tx[2]
        } for tx in transactions]

        return jsonify(dag_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ----------------- DELETE WALLET -----------------
@app.route('/delete_wallet/<owner>', methods=['DELETE'])
def delete_wallet(owner):
    try:
        conn = sqlite3.connect('tanglecoind.db')
        cursor = conn.cursor()

        # Check if wallet exists
        cursor.execute('SELECT * FROM wallets WHERE owner = ?', (owner,))
        wallet = cursor.fetchone()

        if not wallet:
            conn.close()
            return jsonify({'error': 'Wallet not found'}), 404

        # Delete wallet
        cursor.execute('DELETE FROM wallets WHERE owner = ?', (owner,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Wallet deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- INITIALIZE DATABASE -----------------
if __name__ == '__main__':
    create_database()
    app.run(debug=True)
