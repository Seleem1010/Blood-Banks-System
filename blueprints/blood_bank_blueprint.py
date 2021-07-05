from utils.blood import expiration_date
from db.blood_case_insertion import insert_blood_case
from db.refused_requests import blood_reauest_refused, update_user
from flask import Blueprint, request, render_template, redirect, session
from db.init import execute
from db.blood_bank import get_bloodbanks_by_email
from db.bank_storage import get_bank_Storage
import datetime
from utils.alert import alert
from utils.security import encrypt_password, check_encrypted_password
from db.donation_request import get_donation_request, get_donation_details, accept_blood_request


bank = Blueprint('bank', __name__)


@bank.route('/login', methods=['POST', 'GET'])
def login():
    if(request.method == 'GET'):
        return render_template('bb_login.html')

    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']

        banks = execute(get_bloodbanks_by_email(email))
        if len(banks) == 0:
            return alert('no blood bank matches this email')
        bank = banks[0]
        print(bank)
        passwordVerified = check_encrypted_password(password, bank['password'])
        if not passwordVerified:
            return alert('incorrect password')
        session['bank'] = {"id": bank['id'], "email": bank['email']}
        return redirect('/bank/home')


@bank.route('/home', methods=['GET'])
def home():
    bloodcases = execute(get_bank_Storage(session.get("bank")["id"]))
    return render_template('Bank_home.html', bloodcases=bloodcases)


@bank.route('/donation-request', methods=['GET'])
def show_donate_requests():
    history = execute(get_donation_request(session.get("bank")["id"]))
    return render_template('donate_Requests.html', history=history)


@bank.route('/donation-request/<int:rid>', methods=['GET'])
def show_manage(rid):
    donationRequest = execute(get_donation_details(rid))[0]
    return render_template('Manage.html', donation=donationRequest)


@bank.route('/donation-request/<int:rid>/refuse', methods=['POST'])
def refuse_request(rid):
    execute(update_user(
        request.form['userId'], request.form['weight'], request.form['hasDiseases']))
    execute(blood_reauest_refused(rid))
    return redirect('/bank/donation-request')


@bank.route('/donation-request/<int:rid>/accept', methods=['POST'])
def accept_request(rid):
    execute(accept_blood_request(rid))
    execute(insert_blood_case(rid, session.get("bank")["id"], request.form['bloodType'],
                              request.form['bloodClass'], datetime.datetime.now(),
                              datetime.datetime.now() + datetime.timedelta(expiration_date(request.form['bloodType']))))
    return redirect('/bank/donation-request')
