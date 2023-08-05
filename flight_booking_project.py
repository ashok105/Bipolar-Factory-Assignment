from flask import Flask, render_template, request, redirect, jsonify, url_for, flash,session as session_dict
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base,User,Flight,BookedTickets,engine

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('authentication/index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session_dict:
        if session_dict['isAdmin']:
            return redirect(url_for('showFlights'))
        else:
            return redirect(url_for('getAllFlight'))
    else:
        return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = session.query(User).filter_by(username=username, password=password).first()
        if user:
            session_dict['user'] = user.id
            session_dict['isAdmin']=user.is_admin
            print(user.is_admin)
            flash("you signed in successfully.")
            session.commit()
            return redirect(url_for('dashboard'))
    elif 'user' in session_dict:
        return  redirect(url_for('dashboard'))
    return render_template('authentication/signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different username.", "error")
            return redirect(url_for('signup'))
        password = request.form['password']
        email = request.form['email']
        existing_email = session.query(User).filter_by(email=email).first()
        if existing_email:
            flash("email already exists. Please choose a different email.", "error")
            return redirect(url_for('signup'))
        is_admin = True if request.form.get('is_admin') else False
        new_user = User(username=username, password=password, email=email, is_admin=is_admin)
        session.add(new_user)
        session.commit()
        flash("account created succesfully.")
        return redirect(url_for('signin'))

    return render_template('authentication/signup.html')

@app.route('/sign-out')
def sign_out():
    session_dict.pop('user', None)
    flash('You are Signed Out successfully')
    return redirect(url_for('dashboard'))

@app.route('/admin/flights/')
def showFlights():
    if session_dict.get('isAdmin') is True:
        flights = session.query(Flight).order_by(asc(Flight.departure_date),asc(Flight.arrival_time))
        return render_template('admin/flight.html', flights=flights,isAdmin=session_dict.get('isAdmin'))
    else:
        flash('access denied')
        return redirect(url_for('dashboard'))

@app.route('/admin/flight/new/', methods=['GET', 'POST'])
def newFlight():
    if session_dict.get('isAdmin') is True:
        if request.method == 'POST':
            newFlight = Flight(flight_number=request.form['flight_no'],departure=request.form['departure'],destination=request.form['destination'],departure_date=request.form['departure_date'],departure_time=request.form['departure_time'],arrival_time=request.form['arrival_time'],price=request.form['price'])
            session.add(newFlight)
            flash('New flight Successfully Created')
            session.commit()
            return redirect(url_for('showFlights'))
        else:
            return render_template('admin/newFlight.html')
    else:
        flash('access denied')
        return redirect(url_for('dashboard'))
    
@app.route('/admin/flight/<int:flight_id>/delete/', methods=['GET', 'POST'])
def deleteFlight(flight_id):
    if session_dict.get('isAdmin') is True:
        flightToDelete = session.query(
            Flight).filter_by(id=flight_id).one()
        if request.method == 'POST':
            session.query(BookedTickets).filter_by(flight_id=flight_id).delete()
            session.commit()
            session.delete(flightToDelete)
            flash('Successfully Deleted')
            session.commit()
            return redirect(url_for('showFlights', flight_id=flight_id))
        else:
            return render_template('admin/deleteFlight.html', flight=flightToDelete)
    else:
        flash('access denied')
        return redirect(url_for('dashboard'))
    
@app.route('/admin/Bookings',methods=["POST","GET"])
def getAllBooking():
    if session_dict.get('isAdmin') is True:
        if request.method== "POST":
            query = session.query(Flight, BookedTickets).filter(Flight.id == BookedTickets.flight_id,Flight.flight_number==request.form['flight_number'],Flight.departure_date==request.form['departure_date'],Flight.departure_time==request.form['departure_time']).order_by(BookedTickets.seat_number.asc())
            bookings = query.all()
            flights=session.query(Flight.flight_number).distinct().all()
            return render_template('admin/bookings.html',booked_tickets=bookings,flights=flights,isAdmin=session_dict.get('isAdmin'))
        else:
            flights=session.query(Flight.flight_number).distinct().all()
            return render_template('admin/bookings.html',flights=flights,isAdmin=session_dict.get('isAdmin')) 
    else:
        flash('access denied')
        return redirect(url_for('dashboard'))
    
@app.route('/user/flights', methods=["POST","GET"])
def getAllFlight():
    if 'user' in session_dict:
        if request.method== "POST":
            flights = session.query(Flight).filter(Flight.departure == request.form['departure'],Flight.destination == request.form['destination'],Flight.departure_date >=request.form['departure_date']).order_by(Flight.departure_date, Flight.departure_time).all()
            departures=session.query(Flight.departure).distinct().all()
            destinations=session.query(Flight.destination).distinct().all()
            return render_template('user/flight.html',flights=flights,departures=departures,destinations=destinations)
        else:
            departures=session.query(Flight.departure).distinct().all()
            destinations=session.query(Flight.destination).distinct().all()
            return render_template('user/flight.html',flights=[],departures=departures,destinations=destinations) 
    else:
        return redirect(url_for('signin'))   
    
@app.route('/user/flight/<int:flight_id>/book',methods=["POST","GET"])
def bookFlight(flight_id):
    if 'user' in session_dict:
        if request.method== "POST":
            flight = session.query(Flight).get(flight_id)
            def is_seat_booked(flight_id, seat_number):
                try:
                    booked_ticket = session.query(BookedTickets).filter_by(flight_id=flight_id, seat_number=seat_number).one()
                    return True 
                except NoResultFound:
                    return False  
            if is_seat_booked(flight_id,request.form['seat_number']):
                flash('seat num is already taken')
                return render_template('user/bookFlight.html')
            ticket_number=flight.flight_number+'-'+str(flight.departure_time)+'-'+"S"+str(request.form['seat_number'])
            newBooking = BookedTickets(user_id=session_dict.get('user'),flight_id=flight_id,ticket_number=ticket_number,passenger_name=request.form['passenger_name'],seat_number=request.form['seat_number'])
            session.add(newBooking)
            flash('flight booking is successfull')
            session.commit()
            return redirect(url_for('getAllFlight'))    
        else:
            return render_template('user/bookFlight.html')
    else:
        return redirect(url_for('signin'))
    
@app.route('/user/myBookings',methods=["GET"])
def myBookings():
    if 'user' in session_dict:
        query = session.query(BookedTickets,Flight).filter(BookedTickets.flight_id==Flight.id,BookedTickets.user_id==session_dict.get('user'))
        bookings = query.all()
        print(bookings)
        return render_template('user/myBookings.html',booked_tickets=bookings)
    else:
        return redirect(url_for('signin'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
