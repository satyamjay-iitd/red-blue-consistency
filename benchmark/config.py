import os
from dotenv import load_dotenv

load_dotenv('../.env')

RDS_MASTER_PORT = os.environ['RDS_MASTER_PORT']
RDS_REPLICA1_PORT = os.environ['RDS_REPLICA1_PORT']
RDS_REPLICA2_PORT = os.environ['RDS_REPLICA2_PORT']
RDS_REP_IN_SYNC = True
