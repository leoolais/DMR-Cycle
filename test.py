from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Operator, DMR, ServiceHealthcare # Import the models
import hashlib


def generate_hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


if __name__ == '__main__':
    # Database Setup
    engine = create_engine('sqlite:///sterilization_tracker.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # Create Test Operators
    test_operators = [
        {
            'username': 'user1',
            'password': 'password1',
            'first_name': 'Test',
            'last_name': 'User1',
            'service_assignment': 'Sterilization'
        },
         {
            'username': 'user2',
            'password': 'password2',
            'first_name': 'Test',
            'last_name': 'User2',
            'service_assignment': 'Surgical'
        }
    ]

    for operator_data in test_operators:
        hashed_password = generate_hash_password(operator_data['password'])
        new_operator = Operator(
            username=operator_data['username'],
            password=hashed_password,
            first_name=operator_data['first_name'],
            last_name=operator_data['last_name'],
            service_assignment=operator_data['service_assignment']
        )
        session.add(new_operator)
    # Create test Services
    test_services = [
        {
            'service_name': 'Sterilization',
            'healthcare_professionals': 'Sterilization Team',
            'storage_location': 'Storage A'
        },
        {
            'service_name': 'Surgical',
            'healthcare_professionals': 'Surgical Team',
            'storage_location': 'Storage B'
        }
    ]
    for service_data in test_services:
        new_service = ServiceHealthcare(
           service_name=service_data['service_name'],
           healthcare_professionals=service_data['healthcare_professionals'],
           storage_location=service_data['storage_location']
        )
        session.add(new_service)

    # Create test DMRs
    test_dmrs = [
         {
             'unique_id': 'DMR001',
             'description': 'Forceps',
            'brand_model': 'ABC',
            'service_id':1
        },
        {
            'unique_id': 'DMR002',
            'description': 'Scalpel Handle',
            'brand_model': 'XYZ',
            'service_id':2
        },
    ]

    for dmr_data in test_dmrs:
        new_dmr = DMR(
            unique_id=dmr_data['unique_id'],
            description=dmr_data['description'],
            brand_model=dmr_data['brand_model'],
            service_id=dmr_data['service_id']
        )
        session.add(new_dmr)

    session.commit()
    session.close()

    print("Test data populated successfully!")
