from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)

class Flight(Base):
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_number = Column(String(10), nullable=False)
    departure = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_date = Column(Date, nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    price = Column(Integer, nullable=False)

class BookedTickets(Base):
    __tablename__ = 'booked_tickets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    ticket_number = Column(String(100), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    seat_number = Column(String(10), nullable=False)
    
username = 'root'
password = 'ashok_105'
host = 'localhost' 
port = '3306'
database_name = 'flight_booking'

db_uri = f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database_name}'

engine = create_engine(db_uri)

Base.metadata.create_all(engine)