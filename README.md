----------
 iBanking
----------
iBanking based on the Flask platform using MongoDB to store data.

------------------------------
• MAIN LIBRARIES:
------------------------------
	+ flask
	+ flask_mail
	+ itsdangerous
	+ flask_mongoengine

------------------------------
• ACTIVITY:
------------------------------
	0/ Start.
	1/ User login to the system, the system will retrieve user information and available balance in the account.
	2/ User enter student ID, the system will retrieve information about the full name and the corresponding amount of tuition to pay.
	3/ When the user click "Confirm", an OTP will be sent to the user's email (Set the validity time of OTP to 5 minutes).
	4/ The system also navigate to the OTP authentication page.
	5/ User enter OTP, and click "Confirm" again.
	6/ System proceed to deduct and update account balance when OTP is not expired.
	7/ Send mail to announce payer of successful payment.
	8/ Finish the transaction, return to the payment page.
	9/ End.

------------------------------
• URI:
------------------------------
127.0.0.1:5000
	/
	/login
	/logout
	/otp
	/confirm
	/announce
	/student/<id>

------------------------------
• RUN PROJECT - STEP BY STEP:
------------------------------
	1/ Open "config.cfg" file and enter your email and password	
	2/ Setup MongoDB:
		>> Install mongodb shell
		>> Install Robo3T
		>> Open Robot3T and create a database named as iBanking
		>> In the iBanking database, create 2 collections named as user and student_tuition_fee
		>> Right click on each collection and choose Insert Document
		>> In the Insert Document section, make sure you have remove the curly brackets before the next step 
		>> Open the db collections folder and copy each content of those files into the Insert Document section of each collection
		>> Refesh the database and check if all data have been imported
	3/ Enter these command lines to run the app:
		>> cd flask
		>> source venv/bin/activate
		>> export FLASK_APP=index.py
		>> export FLASK_DEBUG=1
		>> python3 -m flask run

------------------------------
• ACCOUNTS GIVEN:
------------------------------
	username: khang
	password: 123456KKLteam

