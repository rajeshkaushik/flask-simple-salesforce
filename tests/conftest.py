from flask import Flask
from flask_testing import TestCase


class AppTestCase(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SF_USERNAME'] = 'rajesh.kaushik15@gmail.com'
        app.config['SF_PASSWORD'] = 'flaskssf@123'
        app.config['SF_SECURITY_TOKEN'] = 'zH6DkZkeVPMAmwUs04cpU2wMb'
        app.config['SF_DOMAIN'] = 'rajeshkaushik15-dev-ed.my.salesforce.com'
        return app
