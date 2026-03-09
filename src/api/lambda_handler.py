import sys
import os
sys.path.insert(0, '/var/task')

from src.api.main import app
from mangum import Mangum

handler = Mangum(app)