from flask import *
from flask_mail import *
from itsdangerous import *
from flask_mongoengine import MongoEngine
import hashlib, json

#----------
#	INIT
#----------
app = Flask(__name__, template_folder="template")
app.secret_key = "Essay";

#CONFIGURE MAIL INFO
app.config.from_pyfile('config.cfg')
mailConfig = Mail(app)
SecretKey = URLSafeTimedSerializer("SecretKey")
sender = "vinhkhang1969@gmail.com";

#---------------
#	DATABASE
#---------------
app.config['MONGODB_SETTINGS'] = {
    'db': 'iBanking',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

# User collection
class User(db.Document):
    username = db.StringField()
    password = db.StringField()
    fullname = db.StringField()
    email = db.StringField()
    phone = db.StringField()
    availableBalances = db.FloatField()
    transactionHistory = db.ListField()
	
# Student tuition fee collection
class StudentTuitionFee(db.Document):
	studentId = db.StringField()
	studentName = db.StringField()
	tuitionFee = db.FloatField()
	status = db.StringField()
	payHistory = db.DictField()

#---------
#	API
#---------
# INDEX
@app.route('/')
def index():
	return render_template('index.html')
	
# LOG IN
@app.route('/login',methods=["GET","POST"])
def LogIn():
	if "user" in session and "fullname" in session:
		g.fullname = session["fullname"];
		g.email = session["email"];
		g.phone = session["phone"];
		user = User.objects(email = g.email).first()
		return render_template('payment.html', availableBalances = user.availableBalances)
	if(request.method=="POST"):
		Username 	= request.form['name'];
		Password 	= request.form['pass'];
		Hash512 	= hashlib.sha512(Password.encode());
		PasswordHashed = Hash512.hexdigest();

		# GET USER INFO FROM DB 
		user = User.objects(username = Username, password = PasswordHashed).first()
		if user:			
			session["user"] = user.username;
			session["fullname"] = user.fullname;
			session["email"] = user.email;
			session["phone"] = user.phone;
			session["availableBalances"] = user.availableBalances;

			g.fullname = session["fullname"];
			g.email = session["email"];
			g.phone = session["phone"];
			return render_template('payment.html', availableBalances = user.availableBalances)
		return render_template('index.html', errorMessage = 'Wrong email or password')
	if request.method == "GET":
		return render_template('index.html')

# OTP EMAIL
@app.route('/otp',methods=["GET","POST"])
def otp():
	if(request.method=="POST"):
		Title 		= "iBanking";
		recipients 	= request.form['email'];
		OTP 		= SecretKey.dumps(recipients, salt="email-confirm")
		mess 		= Message(Title, sender=sender, recipients=[recipients])
		mess.body 	= "Hi {}! \nYour OTP: {}".format(recipients.split("@gmail.com")[0], OTP)
		mailConfig.send(mess)

		# Receive transaction data from the form
		payerName = request.form['payerName']
		payerPhone = request.form['payerPhone']
		payerEmail = request.form['email']
		studentId = request.form['stdID']
		studentName = request.form['stdName']
		tuitionFee = request.form['tuitionFee']
		avaiBalance = request.form['avaiBalance']
		paidAmountBill = request.form['paidAmountBill']
		timeInput = request.form['timeInput']

		transactionData = {
			"payerName": payerName,
			"payerPhone": payerPhone,
			"payerEmail": payerEmail,
			"studentId": studentId,
			"studentName": studentName,
			"tuitionFee": tuitionFee,
			"avaiBalance": avaiBalance,
			"paidAmountBill": paidAmountBill,
			"timeInput": timeInput
		}
		session['transactionData'] = transactionData
		return render_template('paymentConfirm.html')
	else:
		return render_template('payment.html')

# CONFIRM TOKEN AND STORE TO DB
@app.route('/confirm',methods=["POST"])
def confirm():
	OTP = request.form['otp'];
	# CHECK OTP EXPIRED
	try:
		Email = SecretKey.loads(OTP, salt="email-confirm", max_age=300) #SET TIME TO USE: 300 SECS (5 MINS)
	except SignatureExpired:
		g.messExpiredPayment = "YOUR PAYMENT CONFIRMATION SESSION HAS EXPIRED! PLEASE TRY AGAIN!";
		return render_template('messages.html')

	# IF NOT EXPIRED => CONFIRM OTP SUCCESS AND STORE TO DB
	# Get transaction data from session
	payerName = session['transactionData']['payerName']
	payerEmail = session['transactionData']['payerEmail']
	studentId = session['transactionData']['studentId']	
	avaiBalance = session['transactionData']['avaiBalance']
	paidAmountBill = session['transactionData']['paidAmountBill']
	timeInput = session['transactionData']['timeInput']

	# Update new balance and new transaction history for payer
	payer = User.objects(email = payerEmail).first()
	avaiBalance = float("".join(avaiBalance.split(",")))
	paidAmountBill = float("".join(paidAmountBill.split(",")))
	newPayerBalance = avaiBalance - paidAmountBill
	newTransactionHistory = payer.transactionHistory
	newTransactionHistory.append({ "studentId": studentId, "paidAmount": paidAmountBill, "date": timeInput })
	payer.update(availableBalances = newPayerBalance, transactionHistory = newTransactionHistory)

	# Update pay history for student tuition fee
	studentTF = StudentTuitionFee.objects(studentId = studentId, status = "Debt").first()
	studentTF.update(status = "Accomplished", payHistory = { "payer": payerName, "date": timeInput })

	# Send mail to announce payer of successful payment
	Title 		= "iBanking"
	recipients 	= payerEmail
	mess 		= Message(Title, sender = sender, recipients = [recipients])
	successfulMessage = "\nYour payment has been successful.\n\nTransaction detail:\nPayer name: {}\nAvailable balance after paying: {:,.2f}\nPaid for student with the id: {}\nTuition fee has paid: {:,.2f}\nDate: {}".format(payerName, newPayerBalance, studentId, paidAmountBill, timeInput)
	mess.body 	= "Hi {}! \n{}".format(recipients.split("@gmail.com")[0], successfulMessage)
	mailConfig.send(mess)
	return redirect(url_for('Announce'))

# ANNOUNCE PAYER TO CHECK THEIR MAIL
@app.route('/announce')
def Announce():
	if "user" in session and "fullname" in session:
		payerEmail = session['transactionData']['payerEmail']
		return render_template("announce.html", payerEmail = payerEmail)
	else:
		return render_template('index.html')

# GET STUDENT DATA OF WHICH TUITION FEE HAS NOT BEEN DONE FOR FRONTEND
@app.route("/student/<id>", methods=['GET'])
def getStudentData(id):
	if request.method == "GET":
		studentTF = StudentTuitionFee.objects(studentId = id, status = "Debt").first()
		return jsonify(studentTF)

# LOG OUT
@app.route('/logout')
def LogOut():
	session.pop('user', None)
	session.pop('fullname', None)
	session.pop('email', None)
	session.pop('phone', None)
	session.pop('availableBalances', None)
	return redirect(url_for('index'))

# 404 NOT FOUND
@app.errorhandler(404) 
def HandleNotFound(e):
	g.mess404NotFound = "404 NOT FOUND";
	return render_template('messages.html')

# 400 BAD REQUEST
@app.errorhandler(400) 
def HandleBadRequest(e):
	g.mess400BadRequest = "400 BAD REQUEST";
	return render_template('messages.html')

#-----------
#	MAIN
#-----------
if(__name__ == "__main__"):
	app.run()

#----------
#	END
#----------