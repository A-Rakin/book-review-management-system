import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, db

with app.app_context():
    db.create_all()
    from app import seed_database
    seed_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)