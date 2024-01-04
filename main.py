import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from zxing import BarCodeReader
import sqlite3
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

class AttendanceApp(App):
    def build(self):
        self.conn = sqlite3.connect('attendance.db')
        self.cur = self.conn.cursor()

        self.cur.execute('CREATE TABLE IF NOT EXISTS users (roll_number TEXT PRIMARY KEY, name TEXT, specialization TEXT)')
        self.cur.execute('CREATE TABLE IF NOT EXISTS attendance (roll_number TEXT, entry_time TEXT, exit_time TEXT, date TEXT)')

        layout = BoxLayout(orientation='vertical')

        self.label = Label(text='Scan QR Code for Attendance')
        self.btn_scan = Button(text='Scan QR Code', on_press=self.scan_qr)
        self.btn_register = Button(text='Register User', on_press=self.show_registration_popup)
        self.btn_get_report = Button(text='Get Report', on_press=self.send_report)

        layout.add_widget(self.label)
        layout.add_widget(self.btn_scan)
        layout.add_widget(self.btn_register)
        layout.add_widget(self.btn_entry)
        layout.add_widget(self.btn_exit)

        return layout

    def show_registration_popup(self, instance):
        # Display a popup for user registration
        popup_layout = BoxLayout(orientation='vertical')
        popup_label = Label(text='Enter User Details:')
        self.roll_number_input = TextInput(hint_text='Roll Number')
        self.name_input = TextInput(hint_text='Name')
        self.specialization_input = TextInput(hint_text='Specialization')
        self.phone_number_input = TextInput(hint_text='Parent mobile number')
        popup_register_button = Button(text='Register', on_press=self.register_user)

        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(self.roll_number_input)
        popup_layout.add_widget(self.name_input)
        popup_layout.add_widget(self.specialization_input)
        popup_layout.add_widget(popup_register_button)

        popup = Popup(title='User Registration', content=popup_layout, size_hint=(None, None), size=(300, 200))
        popup.open()

    def register_user(self, instance):
        # Insert new user into the database
        roll_number = self.roll_number_input.text
        name = self.name_input.text
        specialization = self.specialization_input.text
        #parents phone number should be entered
        generate_qr_code(roll_number, name, specialization)

        self.cur.execute('INSERT OR REPLACE INTO users VALUES (?, ?, ?)', (roll_number, name, specialization, phone_number))
        self.conn.commit()


        # Close the popup after registration
        instance.parent.parent.dismiss()

    def generate_qr_code(roll_number, name, specialization):
        data = f"Roll Number: {roll_number}\nName: {name}\nSpecialization: {specialization}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(roll_number-name.png)


    def extract_roll_number(decoded_data):
        # Extract roll number from the decoded data
        roll_number_prefix = "Roll Number: "
        roll_number_start = decoded_data.find(roll_number_prefix)

        if roll_number_start != -1:
            roll_number_end = decoded_data.find("\n", roll_number_start)
            return decoded_data[roll_number_start + len(roll_number_prefix):roll_number_end]
        else:
            return None


    def scan_qr(self, instance):
        # Use ZXing to scan QR code
        with BarCodeReader() as reader:
            result = reader.decode()

            if result:
                decoded_data = result.data
                roll_number = self.extract_roll_number(decoded_data)
                entry_time, exit_time = self.get_last_entry_exit_times(roll_number)

                if entry_time and not exit_time:
                    # Entry time recorded but exit time is not, record exit time
                    self.record_exit_time(roll_number)
                    self.label.text = f'Exit time recorded for {roll_number}'
                    self.send_sms_to_parent(roll_number)
                else:
                    # Entry time not recorded or both entry and exit times are recorded, record entry time
                    self.record_entry_time(roll_number)
                    self.label.text = f'Entry time recorded for {roll_number}'

    def record_entry_time(self, roll_number):
        # Record entry time in SQLite database
        self.cur.execute('CREATE TABLE IF NOT EXISTS attendance (roll_number TEXT, entry_time TEXT, exit_time TEXT, date TEXT)')

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cur.execute('INSERT INTO attendance VALUES (?, ?, ?, ?)', (roll_number, current_datetime, None, current_datetime[:10]))
        self.conn.commit()

    def record_exit_time(self, roll_number):
        # Record exit time in SQLite database
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update the exit_time for the given roll_number and date
        self.cur.execute('UPDATE attendance SET exit_time = ? WHERE roll_number = ? AND date = ? AND exit_time IS NULL',
                         (current_datetime, roll_number, current_datetime[:10]))
        self.conn.commit()

    def get_last_entry_exit_times(self, roll_number):
        # Get the last entry and exit times for a specific roll_number
        self.cur.execute('SELECT entry_time, exit_time FROM attendance WHERE roll_number = ? ORDER BY date DESC LIMIT 1',
                         (roll_number,))
        entry_exit_times = self.cur.fetchone()
        return entry_exit_times if entry_exit_times else (None, None)

    def send_sms_to_parent(self, roll_number): #to be altered (phone number parent's)
        # Use Twilio to send SMS to parent
        account_sid = 'your_account_sid'
        auth_token = 'your_auth_token'
        client = Client(account_sid, auth_token)
        #should get students name and their parent phone number
        # Replace with your Twilio phone number and SMS message
        message = client.messages.create(
            body=f'Attendance recorded for {roll_number}',
            from_='your_twilio_number',
            to='parent_phone_number'
        )

    def send_report(self, instance):
        # Generate an Excel report and send it via email
        report_df = self.generate_report()
        report_filename = 'attendance_report.xlsx'
        report_df.to_excel(report_filename, index=False)
        self.send_email_report(report_filename)

    def generate_report(self):
        # Generate a report using pandas DataFrame
        self.cur.execute('SELECT * FROM attendance') #should be altered for the current date
        attendance_data = self.cur.fetchall()

        columns = ['Roll Number', 'Entry Time', 'Exit Time', 'Date']
        report_df = pd.DataFrame(attendance_data, columns=columns)

        return report_df

    def send_email_report(self, report_filename):
        # Send an email with the Excel report
        email_sender = 'your_email@gmail.com'
        email_receiver = 'owner_email@gmail.com'
        email_password = 'your_email_password'

        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg['Subject'] = 'Attendance Report'

        body = MIMEText('Please find the attached attendance report.')
        msg.attach(body)

        with open(report_filename, 'rb') as report_file:
            attachment = MIMEText(report_file.read(), 'xlsx')
            attachment.add_header('Content-Disposition', f'attachment; filename={report_filename}')
            msg.attach(attachment)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, msg.as_string())

if __name__ == '__main__':
    AttendanceApp().run()
