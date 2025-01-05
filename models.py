from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from datetime import datetime

Base = declarative_base()

class DMR(Base):
    __tablename__ = 'dmrs'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String, unique=True, nullable=False)
    description = Column(String)
    brand_model = Column(String)
    storage_location = Column(String)
    status = Column(String, default="Usable")  # Usable, Non-Usable

    # Relationships
    cycles = relationship("CycleOperation", back_populates="dmr")
    utilizations = relationship("Utilization", back_populates="dmr")

    def __repr__(self):
        return f"<DMR(unique_id='{self.unique_id}', description='{self.description}')>"

class Operator(Base):
    __tablename__ = 'operators'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  #  Store hashes in a real app!
    first_name = Column(String)
    last_name = Column(String)
    service_assignment = Column(String)

    # Relationships
    cycles = relationship("CycleOperation", back_populates="operator")
    utilizations = relationship("Utilization", back_populates="operator")

    def __repr__(self):
        return f"<Operator(username='{self.username}', first_name='{self.first_name}')>"


class CycleOperation(Base):
    __tablename__ = 'cycle_operations'
    id = Column(Integer, primary_key=True)
    dmr_id = Column(Integer, ForeignKey('dmrs.id'), nullable=False)
    operation_type = Column(String, nullable=False)  # Cleaning, Drying, Sterilization, Packaging, Storage
    timestamp = Column(DateTime, default=datetime.utcnow)
    operator_id = Column(Integer, ForeignKey('operators.id'), nullable=False)
    location = Column(String) # Updated DMR storage location
    equipment_used = Column(String) # E.g., Autoclave #1

    #Relationships
    dmr = relationship("DMR", back_populates="cycles")
    operator = relationship("Operator", back_populates="cycles")

    def __repr__(self):
        return f"<CycleOperation(operation_type='{self.operation_type}', dmr_id='{self.dmr_id}')>"


class Utilization(Base):
    __tablename__ = 'utilizations'
    id = Column(Integer, primary_key=True)
    dmr_id = Column(Integer, ForeignKey('dmrs.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    operator_id = Column(Integer, ForeignKey('operators.id'), nullable=False)
    intervention_number = Column(String)
    healthcare_professional = Column(String)

    # Relationships
    dmr = relationship("DMR", back_populates="utilizations")
    operator = relationship("Operator", back_populates="utilizations")

    def __repr__(self):
        return f"<Utilization(dmr_id='{self.dmr_id}', intervention_number='{self.intervention_number}')>"

# Initialize the database
engine = create_engine('sqlite:///sterilization_tracker.db')
Base.metadata.create_all(engine)

# Add an event listener to the CycleOperation model to handle DMR status and storage location updates upon creation
@event.listens_for(CycleOperation, 'after_insert')
def after_cycle_operation_insert(mapper, connection, target):
    session = Session(bind=connection)
    dmr = session.query(DMR).filter(DMR.id == target.dmr_id).first()
    if target.operation_type in ['Sterilization', 'Storage']:
        dmr.status = "Usable"
    else:
        dmr.status = "Non-Usable"
    dmr.storage_location = target.location
    session.commit()
    session.close()

# Create a session factory for managing db transactions
Session = sessionmaker(bind=engine)