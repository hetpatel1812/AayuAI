import sys
import os
from app import app
from database_models import db, User

# Create a test PDF
with open("test.pdf", "wb") as f:
    f.write(b"fake pdf content")

with app.test_client() as client:
    with app.app_context():
        # Login as a user
        user = User.query.first()
        if not user:
            print("No users in db")
            sys.exit()
            
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        data = {
            'mode': 'pdf',
            'lang': 'en',
            'file': (open('test.pdf', 'rb'), 'test.pdf')
        }
        try:
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            print(f"Status: {response.status_code}")
            if response.status_code == 500:
                print(response.get_data(as_text=True))
        except Exception as e:
            import traceback
            traceback.print_exc()

os.remove("test.pdf")
