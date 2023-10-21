import os
from dotenv import load_dotenv

load_dotenv('../.env')

RDS_MASTER_PORT = os.environ['RDS_MASTER_PORT']
RDS_REPLICA1_PORT = os.environ['RDS_REPLICA1_PORT']
RDS_REPLICA2_PORT = os.environ['RDS_REPLICA2_PORT']
RDS_REP_IN_SYNC = bool(os.environ['RDS_REP_IN_SYNC'])

BANK_INTEREST = 0.01
