from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker

# set engine and sessionmakers
sip_engine = create_engine("mysql+mysqldb://root:pass@localhost/sip", echo=False, future=True)
sip_sessionmaker = sessionmaker(sip_engine)

# sessionmakers
sessionmakers = {
    "sip": sip_sessionmaker,
}

# get models base class
mapper_registry = registry()
Base = mapper_registry.generate_base()
