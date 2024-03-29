# Attendance Application

## Introduction

### Project Overview
The Attendance App is designed to automate the process of recording student attendance using QR codes. The app simplifies attendance tracking, provides a user-friendly interface, and allows for efficient reporting.

### Objectives
- Automate attendance recording.
- Provide a user-friendly interface for both students and administrators.
- Generate attendance reports for specific dates.

## Features

### QR Code Scanning
- Students can scan QR codes to record attendance.

### User Registration
- Administrators can register new users with their details.

### Entry and Exit Recording
- The app records entry and exit times for each student.

### Report Generation
- Administrators can generate attendance reports for specific dates which would be sent to the administrator via an e-mail. 

### SMS integration
- The app itself sends SMS regarding the student's attendance to their parents. 

## Technologies Used

### Programming Languages
- Python

### Frameworks and Libraries
- Kivy: For building the cross-platform user interface.
- SQLite: For the database to store user and attendance information.
- ZXing: For QR code scanning.

## Implementation Details

### User Interface
- Developed using the KivyMD framework.
- Simple layout with buttons for scanning, registration, entry, exit, and report generation.

### Database Schema
- SQLite database with tables for users and attendance.
- For convinience the attendance recorded will get stored in the local secondary memory of the machine that this attendance app is installed. 

### QR Code Generation
- QR codes are generated for each registered user using ZXing framework. 

### Attendance Logic
- Entry and exit times are recorded in the database.

## Usage Instructions
- Administrator is required to login or create an account and update the student details which would appropriately create QR codes for each students. 
- For recording the attendance the administrator should use the scanning option provided in the app itself. 
- To record the entry time student should scan his/her QR code once and for recording the exit time the student should scan the QR code once again. 
- To send SMS to the parents regarding attendance, administrator should stop the scanning process once the class gets completed. 
- To get a report, administrator should select the Generate Report option from the menu. 
- To get a report of a particular date, navigate to the menu and select get report and specify the date to which the report is to be generated. 

## Future Enhancements
- Since the application itself stores the data in the secondary memory of a device that the application has been installed, it occupies a considerable amount of memory for an academy with large set of students. This issue could be solved by implementing the application in a cloud environment. 

## Conclusion
- This is an application for automating the process of marking attendance and generating a daily report, which is achieved with the help of QR codes and Python programming language's simplicity. 

## References
- To know more about python https://docs.python.org/3/
- To know more about kivy and kivyMD https://kivy.org/doc/stable/
- To know more about SQLite https://www.sqlite.org/docs.html