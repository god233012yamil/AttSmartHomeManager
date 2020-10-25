#
import os
import sys
import time
#
from PyQt5.QtGui import QGuiApplication, QBrush, QColor, QIcon, QPixmap, QMovie
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QPoint
# to import Qt Namespace
from PyQt5.QtCore import Qt
# Import the Selenium WebDriver. The selenium package is used to automate web browser interaction from Python.
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Beautiful Soup is a Python library for pulling data out of
# HTML and XML files. It works with your favorite parser to provide
# idiomatic ways of navigating, searching, and modifying the parse tree.
# It commonly saves programmers hours or days of work.
from bs4 import BeautifulSoup

# Global variables section
app = QApplication(sys.argv)
list_device_names = []
list_device_types = []
list_connection_type = []

# Define the options to use with chromedriver.
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
# options.addArguments("start-maximized");
# options.add_argument('--incognito')
# options.add_argument('--headless')
options.add_argument("--test-type")
# mWebDriver = webdriver.Chrome('/path/to/chromedriver')  # Optional argument, if not specified will search path.

# https://sites.google.com/a/chromium.org/chromedriver/home
# The WebDriver is an open source tool for automated testing of webapps across many browsers.
# It provides capabilities for navigating to web pages, user input, JavaScript execution, and more.
# ChromeDriver is a standalone server that implements the W3C WebDriver standard.
# ChromeDriver is available for Chrome on Android and Chrome on Desktop (Mac, Linux, Windows and ChromeOS).
try:
    # Get current working directory
    chrome_driver_path = os.path.dirname(os.path.realpath(__file__))
    # Set the complete path to chromedriver.
    chrome_driver_path += "\\chromedriver_win32\\ChromeDriver 83.0.4103.39.exe"
    # Pass the options to chromedriver.
    mWebDriver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
except SessionNotCreatedException as error:
    print("Chrome Web Driver Error: {0}".format(error))
    sys.exit(-1)


class MainWindowGui(QMainWindow):
    def __init__(self):
        super(MainWindowGui, self).__init__()

        # Fields variables for this class
        self.password = ""
        self.user_id = ""
        self.att_url = "https://myhomenetwork.att.com/#/login"

        # Create widget instances.
        self.UserLineEdit = QLineEdit(self)
        self.PasswordLineEdit = QLineEdit(self)
        self.LoginPushButton = QPushButton('Login', self)
        self.DevicesQTableWidget = QTableWidget()
        self.DevicesQTableWidget.cellDoubleClicked.connect(self.table_cell_doubled_clicked)
        # self.DevicesQTableWidget.cellClicked.connect(self.table_cell_click)
        # Create a QLabel to be used as a loading or waiting indicator.
        self.gif_label_loading_indicator = None
        # Create a QMovie to be used as a loading or waiting indicator.
        self.gif_label_loading_indicator = None
        self.gif_movie_loading_indicator = None

        # Create an instance of class LoginToAttSmartHomeManager.
        self.mLoginToAttSmartHomeManager = LoginToAttSmartHomeManager()
        self.mLoginToAttSmartHomeManager.LoginToAttSmartHomeManagerFillTable.connect(self.fill_table)
        self.mLoginToAttSmartHomeManager.LoginToAttSmartHomeManagerUpdateStatus.connect(self.update_status_bar)
        self.mLoginToAttSmartHomeManager.LoginToAttSmartHomeManagerFailLogin.connect(self.login_failure)

        # Create a instance of the class BlockDevice
        self.mBlockDevice = BlockDevice()
        self.mBlockDevice.BlockDeviceUpdateStatus.connect(self.update_status_bar)
        self.mBlockDevice.BlockDeviceUpdateTableStatusColumn.connect(self.update_table_connection_type_column)
        self.mBlockDevice.BlockDeviceDisableWidgets.connect(self.block_device_disable_widgets)

        # Call InitUI method to Initialized the UI.
        self.InitUI()

    def InitUI(self):
        # user_label widget properties
        user_label = QLabel("User ID", self)

        # UserLineEdit widget properties
        self.UserLineEdit.textChanged.connect(self.update_widgets_when_typing_in_line_edit)
        # Install the event filter for this object to be watch.
        self.UserLineEdit.installEventFilter(self)
        self.UserLineEdit.setFixedWidth(258)
        self.UserLineEdit.setFocus()
        # QLineEdit::Normal 0 Display characters as they are entered. This is the default.
        self.UserLineEdit.setEchoMode(0)
        UserHBoxLayout = QHBoxLayout()
        UserHBoxLayout.addWidget(user_label)
        UserHBoxLayout.addSpacing(10)
        UserHBoxLayout.addWidget(self.UserLineEdit)
        UserHBoxLayout.addStretch()

        # password_label widget properties
        password_label = QLabel("Password", self)

        # PasswordLineEdit widget properties
        self.PasswordLineEdit.textChanged.connect(self.update_widgets_when_typing_in_line_edit)
        # Install the event filter for this object to be watch.
        self.PasswordLineEdit.installEventFilter(self)
        self.PasswordLineEdit.setFixedWidth(258)
        self.PasswordLineEdit.setFocus()
        # QLineEdit::Password 2 Display platform-dependent password mask characters
        # instead of the characters actually entered.
        self.PasswordLineEdit.setEchoMode(2)

        # LoginPushButton widget properties
        self.LoginPushButton.setFixedWidth(70)
        # self.LoginPushButton.setStyleSheet("background-color:rgb(19,145,196); color:white")
        self.LoginPushButton.setEnabled(False)
        self.LoginPushButton.clicked.connect(self.start_login_thread)

        PasswordHBoxLayout = QHBoxLayout()
        PasswordHBoxLayout.addWidget(password_label)
        PasswordHBoxLayout.addWidget(self.PasswordLineEdit)
        PasswordHBoxLayout.addSpacing(155)
        PasswordHBoxLayout.addWidget(self.LoginPushButton)
        PasswordHBoxLayout.addStretch()

        #
        font = self.DevicesQTableWidget.horizontalHeader().font()
        # set QTableWidget1 font to bold. QFont::Bold = 75
        font.setWeight(75)
        self.DevicesQTableWidget.setEnabled(False)
        self.DevicesQTableWidget.setFixedWidth(541)
        self.DevicesQTableWidget.setFixedHeight(175)
        # self.DevicesQTableWidget.horizontalHeader().setFont(font)
        self.DevicesQTableWidget.setRowCount(5)
        self.DevicesQTableWidget.setColumnCount(4)
        self.DevicesQTableWidget.verticalHeader().setVisible(False)
        self.DevicesQTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Item"))
        TableWidgetItem_1 = QTableWidgetItem()
        TableWidgetItem_1.setTextAlignment(Qt.AlignLeft)
        TableWidgetItem_1.setText("Device Name")
        self.DevicesQTableWidget.setHorizontalHeaderItem(1, TableWidgetItem_1)
        TableWidgetItem_2 = QTableWidgetItem()
        TableWidgetItem_2.setTextAlignment(Qt.AlignLeft)
        TableWidgetItem_2.setText("Device Type")
        self.DevicesQTableWidget.setHorizontalHeaderItem(2, TableWidgetItem_2)
        TableWidgetItem_3 = QTableWidgetItem()
        TableWidgetItem_3.setTextAlignment(Qt.AlignLeft)
        TableWidgetItem_3.setText("Connection type")
        self.DevicesQTableWidget.setHorizontalHeaderItem(3, TableWidgetItem_3)
        # self.DevicesQTableWidget.setStyleSheet("QHeaderView::section { background-color:rgb(0,99,177); color:white }")
        self.DevicesQTableWidget.setStyleSheet(
            "QHeaderView::section { background-color:rgb(204,204,204); color:rgb(134,134,134) }")
        self.DevicesQTableWidget.setColumnWidth(0, 10)
        self.DevicesQTableWidget.setColumnWidth(1, 280)
        self.DevicesQTableWidget.setColumnWidth(2, 110)
        self.DevicesQTableWidget.setColumnWidth(3, 110)
        self.DevicesQTableWidget.setVisible(True)
        DevicesQTableWidgetHBoxLayout = QHBoxLayout()
        DevicesQTableWidgetHBoxLayout.addWidget(self.DevicesQTableWidget)
        DevicesQTableWidgetHBoxLayout.addStretch()

        # Setup the main vertical layout.
        MainVBoxLayout = QVBoxLayout()
        MainVBoxLayout.addLayout(UserHBoxLayout)
        MainVBoxLayout.addLayout(PasswordHBoxLayout)
        MainVBoxLayout.addLayout(DevicesQTableWidgetHBoxLayout)
        MainVBoxLayout.addStretch()

        # You can't set a QLayout directly on the QMainWindow.
        # You need to create a QWidget and set it as the central
        # widget on the QMainWindow and assign the QLayout to that.
        widget = QWidget(self)
        widget.setLayout(MainVBoxLayout)

        #
        self.gif_label_loading_indicator = QLabel(self)
        self.gif_label_loading_indicator.setAlignment(Qt.AlignCenter)
        self.gif_label_loading_indicator.move((560 / 2) - (self.gif_label_loading_indicator.width() / 2),
                                              (280 / 2) - (self.gif_label_loading_indicator.height() / 2))
        # Get current working directory
        path = os.path.dirname(os.path.realpath(__file__))
        # This gif was created using: http://www.ajaxload.info/#preview
        self.gif_movie_loading_indicator = QMovie(path + "\\circle_loader_blue_big.gif")
        self.gif_label_loading_indicator.setMovie(self.gif_movie_loading_indicator)

        # Sets the given widget to be the main window's central widget.
        self.setCentralWidget(widget)
        self.setWindowTitle("ATT Smart Home Manager")
        # Find the screen width and height
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        height = screen_geometry.height()
        width = screen_geometry.width()
        self.setFixedSize(560, 280)  # 600, 350
        self.setGeometry((width / 2) - (self.width() / 2), (height / 2) - (self.height() / 2),
                         self.width(), self.height())

        # Set the icon for the application.
        pixmap = QPixmap("AT&T Smart Home Manager Icon.png")
        self.setWindowIcon(QIcon(pixmap))
        self.statusBar().showMessage("Status: Logout")

    # Reimplementing the keyPressEvent method for QMainWindow.
    def keyPressEvent(self, event):
        #
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.PasswordLineEdit.text() != "" and self.UserLineEdit.text() != "":
                self.start_login_thread()
        else:
            QMainWindow.keyPressEvent(self, event)

    # Reimplementing the closeEvent method for QMainWindow.
    def closeEvent(self, *args, **kwargs):
        print("Status: Windows was closed")
        #
        self.gif_movie_loading_indicator.stop()
        # Closes the browser and shuts down the ChromeDriver.
        mWebDriver.quit()

    #
    def update_widgets_when_typing_in_line_edit(self):
        # if QLineEdit1 is not empty
        if self.UserLineEdit.text() != "" and self.PasswordLineEdit.text() != "":
            self.LoginPushButton.setEnabled(True)
        else:
            self.LoginPushButton.setEnabled(False)
        # self.statusBar().showMessage("")

    def start_login_thread(self):
        # Disable the UI.
        self.UserLineEdit.setEnabled(False)
        self.PasswordLineEdit.setEnabled(False)
        self.LoginPushButton.setEnabled(False)
        self.DevicesQTableWidget.setEnabled(False)
        self.DevicesQTableWidget.setStyleSheet(
            "QHeaderView::section { background-color:rgb(204,204,204); color:rgb(134,134,134) }")
        # Clear the table.
        for i in range(self.DevicesQTableWidget.rowCount()):
            # Clear cells at column 1.
            self.DevicesQTableWidget.setItem(i, 1, QTableWidgetItem(""))
            # Clear cells at column 2.
            self.DevicesQTableWidget.setItem(i, 2, QTableWidgetItem(""))
            # Clear cells at column 3.
            self.DevicesQTableWidget.setItem(i, 3, QTableWidgetItem(""))
        # Start the loading indicator.
        self.start_loading_indicator()
        # Pass the url, user id and password to mLoginToAttSmartHomeManager class and
        # start the thread to login into ATT Smart Manager.
        self.mLoginToAttSmartHomeManager.att_url = self.att_url
        self.mLoginToAttSmartHomeManager.password = self.PasswordLineEdit.text()
        self.mLoginToAttSmartHomeManager.user_id = self.UserLineEdit.text()
        self.mLoginToAttSmartHomeManager.start()

    def update_status_bar(self, status):
        self.statusBar().showMessage(status)
        print(status)
        # # If received status contains Error, then enable the widgets.
        if status.find("Error") != -1:
            # Enable the widgets.
            self.UserLineEdit.setEnabled(True)
            self.UserLineEdit.clear()
            self.UserLineEdit.setFocus()
            self.PasswordLineEdit.setEnabled(True)
            self.PasswordLineEdit.clear()
            self.LoginPushButton.setEnabled(True)
            self.DevicesQTableWidget.setEnabled(False)
            self.DevicesQTableWidget.setStyleSheet(
                "QHeaderView::section { background-color:rgb(204,204,204); color:rgb(134,134,134) }")
            # Clear the table
            for i in range(self.DevicesQTableWidget.rowCount()):
                # Clear cells at column 0.
                self.DevicesQTableWidget.setItem(i, 0, QTableWidgetItem(""))
                # Clear cells at column 1.
                self.DevicesQTableWidget.setItem(i, 1, QTableWidgetItem(""))
                # Clear cells at column 2.
                self.DevicesQTableWidget.setItem(i, 2, QTableWidgetItem(""))
                # Clear cells at column 3.
                self.DevicesQTableWidget.setItem(i, 3, QTableWidgetItem(""))
            # Stop indicator.
            self.stop_loading_indicator()

    def update_num_of_connected_devices_widgets(self, num_of_connected_devices):
        self.DevicesQTableWidget.setVisible(True)

    def start_loading_indicator(self):
        self.gif_label_loading_indicator.show()
        self.gif_movie_loading_indicator.start()

    def stop_loading_indicator(self):
        self.gif_label_loading_indicator.hide()
        self.gif_movie_loading_indicator.stop()

    def login_failure(self):
        # Enable the UI.
        self.UserLineEdit.setEnabled(True)
        self.UserLineEdit.clear()
        self.UserLineEdit.setFocus()
        self.PasswordLineEdit.setEnabled(True)
        self.PasswordLineEdit.clear()
        self.LoginPushButton.setEnabled(True)
        self.DevicesQTableWidget.setEnabled(False)
        self.DevicesQTableWidget.setStyleSheet(
            "QHeaderView::section { background-color:rgb(204,204,204); color:rgb(134,134,134) }")
        #
        self.stop_loading_indicator()

    def block_device_disable_widgets(self):
        self.UserLineEdit.setEnabled(False)
        self.PasswordLineEdit.setEnabled(False)
        self.LoginPushButton.setEnabled(False)
        self.DevicesQTableWidget.setEnabled(False)
        self.DevicesQTableWidget.setStyleSheet(
            "QHeaderView::section { background-color:rgb(204,204,204); color:rgb(134,134,134) }")
        self.start_loading_indicator()

    def table_cell_click(self):
        msgBox = QMessageBox()
        msgBox.setText("Double click on any cell of the row to block / unblock the device.")
        msgBox.setWindowTitle("Message")
        pixmap = QPixmap("AT&T Smart Home Manager Icon.png")
        msgBox.setWindowIcon(QIcon(pixmap))
        # msgBox.move((560 / 2) - (msgBox.width() / 2),
        #             (280 / 2) - (msgBox.height() / 2))
        msgBox.exec()

    def fill_table(self):
        # print("Method fill_table was called")
        # Set the Table row count
        row_count = list_device_names.__len__()
        #
        if row_count > 0:
            self.DevicesQTableWidget.setEnabled(True)
            self.DevicesQTableWidget.setRowCount(row_count)
            #
            for i in range(row_count):
                # Add the row number to column 0.
                TableWidgetItem = QTableWidgetItem(str(i))
                TableWidgetItem.setTextAlignment(Qt.AlignCenter)
                self.DevicesQTableWidget.setItem(i, 0, TableWidgetItem)
                # Add the list of device names to column 1.
                self.DevicesQTableWidget.setItem(i, 1, QTableWidgetItem(list_device_names[i]))
                # Add the list of device types to column 2.
                self.DevicesQTableWidget.setItem(i, 2, QTableWidgetItem(list_device_types[i]))
                # Add the list of connection types to column 3.
                TableWidgetItem = QTableWidgetItem(list_connection_type[i])
                if list_connection_type[i] == "Blocked":
                    # set text color to red
                    TableWidgetItem.setForeground(QBrush(QColor(255, 0, 0)))
                    # set background color to red
                    # TableWidgetItem.setBackground(QBrush(QColor(255, 0, 0)))
                else:
                    # set text color to black
                    TableWidgetItem.setForeground(QBrush(QColor(0, 0, 0)))
                    # set background color to white
                    # TableWidgetItem.setBackground(QBrush(QColor(255, 255, 255)))
                self.DevicesQTableWidget.setItem(i, 3, QTableWidgetItem(TableWidgetItem))
            # Enable the UI.
            self.UserLineEdit.setEnabled(True)
            self.PasswordLineEdit.setEnabled(True)
            self.LoginPushButton.setEnabled(True)
            self.DevicesQTableWidget.setEnabled(True)
            self.DevicesQTableWidget.setStyleSheet(
                "QHeaderView::section { background-color:rgb(0,99,177); color:white }")
            #
            self.stop_loading_indicator()
            #
            self.DevicesQTableWidget.repaint()
        else:
            return

    #
    def update_table_connection_type_column(self):
        # Set the Table row count
        row_count = list_connection_type.__len__()
        #
        if row_count > 0:
            for i in range(row_count):
                # Add the list of connection types to column 3.
                TableWidgetItem = QTableWidgetItem(list_connection_type[i])
                if list_connection_type[i] == "Blocked":
                    # set text color to red
                    TableWidgetItem.setForeground(QBrush(QColor(255, 0, 0)))
                    # set background color to red
                    # TableWidgetItem.setBackground(QBrush(QColor(255, 0, 0)))
                else:
                    # set text color to black
                    TableWidgetItem.setForeground(QBrush(QColor(0, 0, 0)))
                    # set background color to white
                    # TableWidgetItem.setBackground(QBrush(QColor(255, 255, 255)))
                self.DevicesQTableWidget.setItem(i, 3, QTableWidgetItem(TableWidgetItem))
            # Enable the UI.
            self.UserLineEdit.setEnabled(True)
            self.PasswordLineEdit.setEnabled(True)
            self.LoginPushButton.setEnabled(True)
            self.DevicesQTableWidget.setEnabled(True)
            self.DevicesQTableWidget.setStyleSheet(
                "QHeaderView::section { background-color:rgb(0,99,177); color:white }")
            #
            self.stop_loading_indicator()
            #
            self.DevicesQTableWidget.repaint()
        else:
            return

    def table_cell_doubled_clicked(self, row, column):
        # print("row: " + str(row) + ", column:" + str(column))
        self.DevicesQTableWidget.setStyleSheet(
            "QHeaderView::section { background-color:rgb(0,99,177); color:white }")
        self.DevicesQTableWidget.repaint()
        # Find the device name we want to block. Device name is in column 1.
        device_name = self.DevicesQTableWidget.item(row, 1).text()
        device_current_status = self.DevicesQTableWidget.item(row, 3).text()
        # If device_name and device_current_status are not empty.
        if device_name != "" and device_current_status != "":
            self.start_loading_indicator()
            self.update_status_bar("Status: Blocking device " + device_name + ", please wait.")
            self.mBlockDevice.device_name = device_name
            self.mBlockDevice.device_current_status = device_current_status
            self.mBlockDevice.start()

    def enable_disable_table(self, action):
        if action.find('enable table') != -1:
            self.DevicesQTableWidget.setEnabled(True)
        elif action.find('disable table') != -1:
            self.DevicesQTableWidget.setEnabled(False)
        else:
            self.DevicesQTableWidget.setEnabled(False)


# This class is used to login to the ATT site. It is a thread
# because this process takes too long to run it in the UI thread.
# https://myhomenetwork.att.com/#/login
# https://myhomenetwork.att.com/#/authenticate
# https://myhomenetwork.att.com/#/home
# https://myhomenetwork.att.com/#/network
# https://myhomenetwork.att.com/#/devices
# https://myhomenetwork.att.com/#/login?loggedOut=true
class LoginToAttSmartHomeManager(QThread):
    # Create Qt signals for this class.
    LoginToAttSmartHomeManagerHasFinished = pyqtSignal()
    LoginToAttSmartHomeManagerUpdateStatus = pyqtSignal(str)
    LoginToAttSmartHomeManagerFillTable = pyqtSignal()
    LoginToAttSmartHomeManagerFailLogin = pyqtSignal()

    def __init__(self):
        super(LoginToAttSmartHomeManager, self).__init__()
        # Fields for this class.
        self.att_url = ""
        self.password = ""
        self.user_id = ""

    def run(self):
        try:
            # Print out the passed url.
            print("passed url: " + self.att_url)

            # Load the page self.att_url.
            mWebDriver.get(self.att_url)

            # print the whole html page.
            # html = mWebDriver.page_source
            # print(html)

            # Get current url.
            current_url = str(mWebDriver.current_url)
            # Print out the current url.
            print("page 1: " + mWebDriver.current_url)
            # If current url is https://myhomenetwork.att.com/#/login
            if current_url == "https://myhomenetwork.att.com/#/login":
                # Explicitly wait up to 60 seconds to find the html input tag whose attribute name is "userid".
                try:
                    input_user_id = WebDriverWait(mWebDriver, 60).until(
                        EC.presence_of_element_located((By.NAME, "userid")))
                except TimeoutException:
                    # Report the error through the status bar and the console and
                    # closes the browser and shuts down the ChromeDriver.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit("Error: Loading page took too much time!")
                    mWebDriver.quit()
                    return
                else:
                    # Clear the input tag.
                    input_user_id.clear()
                    # Write the value in it.
                    input_user_id.send_keys(self.user_id)

                # Find the html input tag whose attribute name is "password" in the page.
                try:
                    input_password = mWebDriver.find_element_by_name('password')
                except NoSuchElementException:
                    # Report the error through the status bar and the console and
                    # closes the browser and shuts down the ChromeDriver.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Error: The element password was not found!")
                    mWebDriver.quit()
                    return
                else:
                    # Clear the input tag.
                    input_password.clear()
                    # Write the value in it.
                    input_password.send_keys(self.password)

                # Find the html button tag whose class name is "sign-in-button" in the page.
                try:
                    sign_in_button = mWebDriver.find_element_by_class_name("sign-in-button")
                except NoSuchElementException:
                    # Report the error through the status bar and the console and return.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Error: The element sign in button was not found!")
                    mWebDriver.quit()
                    return
                else:
                    # Submit the user and password. In other words, press the button sign-in.
                    sign_in_button.submit()
                    # Report the status through the status bar and console.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Status: Your credentials has been submit, please wait")

            # Get current url.
            current_url = str(mWebDriver.current_url)
            # Print out the current url.
            print("page 2: " + mWebDriver.current_url)
            # If current url is https://myhomenetwork.att.com/#/authenticate
            if current_url == "https://myhomenetwork.att.com/#/authenticate":
                # After submit the "user id" and "password" check if the login into the ATT Smart Home Manager succeed.
                second_counter_int = 0
                while second_counter_int < 60:
                    # Wait for a second to give time to web browser to load page.
                    time.sleep(1)
                    # Increment seconds counter.
                    second_counter_int += 1
                    #
                    try:
                        # Find the html ul tag whose class name is "navbar-nav".
                        # If this element is found is because we successfully login into the ATT Smart Home Manager.
                        mWebDriver.find_element_by_class_name("navbar-nav")
                        # Report status through the status bar and console and break the while loop.
                        self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                            "Status: You have successfully login into the ATT Smart Home Manager.")
                        break
                    except NoSuchElementException:
                        #
                        try:
                            # Find the html div tag whose class name is "invalid-feedback".
                            # If we find it is because we didn't succeed login into ATT Smart Home Manager.
                            mWebDriver.find_element_by_class_name("invalid-feedback")
                            # Report error to the status bar and the console and return.
                            self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                                "Error: The User ID and password combination you entered doesn't "
                                "match any entries in our files.")
                            self.LoginToAttSmartHomeManagerFailLogin.emit()
                            return
                        except NoSuchElementException:
                            pass
                    else:
                        pass

                # Explicitly wait up to 60 seconds to find the html div tag whose class name is "info-container".
                # This is done as a safety to make sure that the page is completely loaded.
                try:
                    WebDriverWait(mWebDriver, 60).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "info-container")))
                except TimeoutException:
                    # Report error through the status bar and the console and
                    # closes the browser and shuts down the ChromeDriver.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Error: The html element info-container was not found!")
                    mWebDriver.quit()
                    return

            # Get current url.
            current_url = str(mWebDriver.current_url)
            # Print out the current url.
            print("page 3: " + mWebDriver.current_url)
            # If current url is https://myhomenetwork.att.com/#/home
            if current_url == "https://myhomenetwork.att.com/#/home":
                # Explicitly wait up to 60 seconds to find the html li tag whose xpath is:
                # /html/body/app-root/div/app-navigation/div/div/nav[2]/div/ul/li[2]
                # In here we are looking for the network tab element.
                try:
                    network_tab = WebDriverWait(mWebDriver, 60).until(
                        EC.presence_of_element_located((
                            By.XPATH, "/html/body/app-root/div/app-navigation/div/div/nav[2]/div/ul/li[2]"))
                    )
                except TimeoutException:
                    # Report error through the status bar and the console and
                    # closes the browser and shuts down the ChromeDriver.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Error: The html tag li Network was not found!")
                    mWebDriver.quit()
                    return
                else:
                    # If the network tab is found, then perform a click to go to the next page.
                    network_tab.click()

                # Find the html span tag whose class name is "count".
                connected_devices_int = 0
                second_counter_int = 0
                while connected_devices_int == 0 and second_counter_int < 60:
                    # Wait for a second to give time to web browser to load page.
                    time.sleep(1)
                    # Increment seconds counter.
                    second_counter_int += 1
                    #
                    try:
                        # Find the html span tag whose class name is "count".
                        connected_devices_span = mWebDriver.find_element_by_class_name("count")
                    except NoSuchElementException:
                        pass
                    else:
                        try:
                            # Convert connected devices text into integer.
                            # connected_devices_span.text contains the number of connected devices in string format.
                            connected_devices_int = int(connected_devices_span.text, base=10)
                        except ValueError as v_error:
                            # Report error through the status bar and the console and
                            # closes the browser and shuts down the ChromeDriver.
                            self.LoginToAttSmartHomeManagerUpdateStatus.emit("Error: %s" % v_error)
                            mWebDriver.quit()
                            return
                        else:
                            # If there is at least 1 device connected.
                            # It might happens that the element is found but the count is not loaded.
                            if connected_devices_int > 0:
                                # Report the status through the status bar and the console.
                                self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                                    "Status: Number of connected devices is %d" % connected_devices_int)
                                # Perform a click on this element to show the list of connected devices
                                connected_devices_span.click()
                                break
                # If we wait more than 60 seconds, is because an error took place, so report it and quit.
                if second_counter_int >= 60:
                    # Report error through the status bar and the console and
                    # closes the browser and shuts down the ChromeDriver.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Error: We couldn't find any connected devices. Please restart the application!")
                    mWebDriver.quit()
                    return

            # Get current url.
            current_url = str(mWebDriver.current_url)
            # Print out the current url.
            print("page 4: " + mWebDriver.current_url)
            # If current url is https://myhomenetwork.att.com/#/network
            if current_url == "https://myhomenetwork.att.com/#/network":
                # Find the html ul tag whose class name is "items-list".
                # This is a safety measure to assure that the list of devices exist before we
                # start using soup to scraping the list.
                try:
                    WebDriverWait(mWebDriver, 60).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "items-list")))
                except TimeoutException:
                    # Report error through the status bar and the console and
                    # closes the browser and shuts down the ChromeDriver.
                    self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                        "Error: The html unordered list items-list was not found!")
                    mWebDriver.quit()
                    return

            # Get current url.
            current_url = str(mWebDriver.current_url)
            # Print out the current url.
            print("page 5: " + mWebDriver.current_url)
            # If current url is https://myhomenetwork.att.com/#/devices
            if current_url == "https://myhomenetwork.att.com/#/devices":
                # Clear the list of device names and types.
                list_device_names.clear()
                list_device_types.clear()
                list_connection_type.clear()

                # Parse the html page to scrape for the list of device names, types and connections.
                soup = BeautifulSoup(mWebDriver.page_source, 'html.parser')

                # Find all the html ul tag whose class name is "items-list" using soup.
                items_list = soup.find_all("ul", class_="items-list")
                # Iterate between all the list items from items_list[0].
                for li in items_list[0].find_all("li", class_="item clickable"):
                    #
                    for div in li.find_all("div", class_="content-wrapper"):
                        for div1 in div.find_all("div", class_="name-wrapper"):
                            for span in div1.find_all("span", class_="name"):
                                list_device_names.append(span.text)
                    #
                    for div in li.find_all("div", class_="device-type-icon"):
                        for span in div.find_all("span"):
                            # Convert a soup object into a string using direct type casting.
                            device_type = str(span)
                            # Using python slicing to extract the device type from the span element.
                            slice_start = device_type.find("class") + 7
                            slice_end = device_type.find("-icon")
                            device_type = device_type[slice_start:slice_end]
                            # Add to the list.
                            list_device_types.append(device_type)
                    #
                    for span in li.find_all("span", class_="icons-container"):
                        for span1 in span.find_all("span", class_="connection-type-icon"):
                            for span2 in span1.find_all("span"):
                                # Convert a soup object into a string using direct type casting.
                                connection_type = str(span2)
                                # Using python slicing to extract the device type from the span element.
                                slice_start = connection_type.find("aria-label=") + 12
                                slice_end = connection_type.find("icon", slice_start) - 1
                                # Extract substring using slice.
                                connection_type = connection_type[slice_start:slice_end]
                                # Add to the list.
                                list_connection_type.append(connection_type)
                        for span3 in span.find_all("span", class_="device-state"):
                            connection_type = str(span3.text).strip()
                            # Add to the list.
                            list_connection_type.append(connection_type)
                #
                for li in items_list[0].find_all("li", class_="item clickable last-item"):
                    #
                    for div in li.find_all("div", class_="content-wrapper"):
                        for div1 in div.find_all("div", class_="name-wrapper"):
                            for span in div1.find_all("span", class_="name"):
                                list_device_names.append(span.text)
                    #
                    for div in li.find_all("div", class_="device-type-icon"):
                        for span in div.find_all("span"):
                            # Convert a soup object into a string using direct type casting.
                            device_type = str(span)
                            # Using python slicing to extract the device type from the span element.
                            slice_start = device_type.find("class") + 7
                            slice_end = device_type.find("-icon")
                            device_type = device_type[slice_start:slice_end]
                            # Add to the list.
                            list_device_types.append(device_type)
                    #
                    for span in li.find_all("span", class_="icons-container"):
                        for span1 in span.find_all("span", class_="connection-type-icon"):
                            for span2 in span1.find_all("span"):
                                # Convert a soup object into a string using direct type casting.
                                connection_type = str(span2)
                                # Using python slicing to extract the device type from the span element.
                                slice_start = connection_type.find("aria-label=") + 12
                                slice_end = connection_type.find("icon", slice_start) - 1
                                # Extract substring using slice.
                                connection_type = connection_type[slice_start:slice_end]
                                # Add to the list.
                                list_connection_type.append(connection_type)
                        for span3 in span.find_all("span", class_="device-state"):
                            connection_type = str(span3.text).strip()
                            # Add to the list.
                            list_connection_type.append(connection_type)

                print("list of device names: ")
                print(list_device_names)
                print("list of device types: ")
                print(list_device_types)
                print("list of connection types: ")
                print(list_connection_type)
                # Emit this signal to fill the table with the data stored in the global lists.
                self.LoginToAttSmartHomeManagerFillTable.emit()

        except WebDriverException as e:
            # Report error through the status bar and the console and
            # closes the browser and shuts down the ChromeDriver.
            self.LoginToAttSmartHomeManagerUpdateStatus.emit(
                "Error: WebDriverException error %s" % e)
            mWebDriver.quit()
            return
        else:
            pass


#
class BlockDevice(QThread):
    # Qt signals emit by this class
    BlockDeviceUpdateStatus = pyqtSignal(str)
    BlockDeviceUpdateTableStatusColumn = pyqtSignal()
    BlockDeviceDisableWidgets = pyqtSignal()

    def __init__(self):
        super(BlockDevice, self).__init__()
        self.device_name = ""
        self.device_current_status = ""

    def run(self):
        print("Blocking device " + self.device_name)

        # If we are not in the page "https://myhomenetwork.att.com/#/devices" we can't
        # block a device, so return and do nothing more than report the error.
        current_url = str(mWebDriver.current_url)
        print(current_url)
        if current_url.find("https://myhomenetwork.att.com/#/devices") == -1:
            # Report error through the status bar and the console.
            self.BlockDeviceUpdateStatus.emit(
                "Error: The current page is not \"https://myhomenetwork.att.com/#/devices\"")
            return

        # Find the html ul tag whose class name is "items-list".
        # If this element exist is because we are in the proper html page.
        try:
            WebDriverWait(mWebDriver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "items-list")))
        except TimeoutException:
            # Report error through the status bar and the console and
            # closes the browser and shuts down the ChromeDriver.
            self.BlockDeviceUpdateStatus.emit(
                "Error: We can't block any device because we couldn't find the list of items!")
            mWebDriver.quit()
            return

        # Find the html tag by xpath which contains as text the value of self.device_name.
        # Wait up to a time in case the html element require time to be loaded.
        # driver.find_element_by_xpath("//*[contains(text(),'text to be found')]")
        element_xpath = "//*[contains(text(), '" + self.device_name + "')]"
        try:
            device = WebDriverWait(mWebDriver, 60).until(
                EC.presence_of_element_located((
                    By.XPATH, element_xpath))
            )
        except TimeoutException:
            self.BlockDeviceUpdateStatus.emit(
                "Error: We can't block the device because we couldn't find it!")
            return
        else:
            # Perform a click on the html tag which which contains "self.device_name" as text.
            # This action will load a new page with the details for the device and the button to block it.
            device.click()

        # Block / Unblock the device.
        second_counter_int = 0
        while second_counter_int < 60:
            # Wait for a second to give time to web browser to load page.
            time.sleep(1)
            # Increment seconds counter.
            second_counter_int += 1
            try:
                # Find the html element or tag (in this case is a div) by xpath
                # containing as text the value of "Block Device".
                element_xpath = "//*[contains(text(), 'Block Device')]"
                html_div_block_device = mWebDriver.find_element_by_xpath(element_xpath)
            except NoSuchElementException:
                try:
                    # Find the html element or tag (in this case is a div) by xpath
                    # containing as text the value of "Unblock Device".
                    element_xpath = "//*[contains(text(), 'Unblock Device')]"
                    html_div_unblock_device = mWebDriver.find_element_by_xpath(element_xpath)
                except NoSuchElementException:
                    pass
                else:
                    # Perform a click to unblock the device.
                    html_div_unblock_device.click()
                    # Report the status through the status bar and the console.
                    self.BlockDeviceUpdateStatus.emit("Status: Device was unblocked.")
                    # Break the while loop.
                    break
            else:
                # Perform a click to block the device.
                html_div_block_device.click()
                # Report the status through the status bar and the console.
                self.BlockDeviceUpdateStatus.emit("Status: Device was blocked.")
                # Break the while loop.
                break

        #
        self.BlockDeviceDisableWidgets.emit()

        # This code will wait until
        if element_xpath.find("Block Device") != -1:
            element_xpath_1 = "//*[contains(text(), 'Unblock Device')]"
        else:
            element_xpath_1 = "//*[contains(text(), 'Block Device')]"
        element_is_found = False
        while not element_is_found:
            time.sleep(1)
            try:
                # Find the html element or tag by xpath containing as text the value of
                # "Block Device" or "Unblock Device".
                mWebDriver.find_element_by_xpath(element_xpath_1)
            except NoSuchElementException:
                pass
            else:
                element_is_found = True
                # break

        # Move backward in your browser’s history
        # Go back to the html page where the list of devices is shown
        # in case we want to click on another device to be blocked.
        mWebDriver.back()
        # Find the html ul tag whose class name is "items-list".
        # If this element exist is because we are in the proper html page.
        # The html page with the list of devices.
        try:
            WebDriverWait(mWebDriver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "items-list")))
        except TimeoutException:
            # Report error through the status bar and the console and
            # closes the browser and shuts down the ChromeDriver.
            self.BlockDeviceUpdateStatus.emit(
                "Error: We couldn't find the html page with the list of devices!")
            mWebDriver.quit()
            return

        # Clear the list of types.
        list_connection_type.clear()

        # Parse the html page to scrape for the list of device names, types and connections.
        soup = BeautifulSoup(mWebDriver.page_source, 'html.parser')

        # Find all the html ul tag whose class name is "items-list" using soup.
        items_list = soup.find_all("ul", class_="items-list")
        # Iterate between all the list items from items_list[0].
        for li in items_list[0].find_all("li", class_="item clickable"):
            #
            for span in li.find_all("span", class_="icons-container"):
                for span1 in span.find_all("span", class_="connection-type-icon"):
                    for span2 in span1.find_all("span"):
                        # Convert a soup object into a string using direct type casting.
                        connection_type = str(span2)
                        # Using python slicing to extract the device type from the span element.
                        slice_start = connection_type.find("aria-label=") + 12
                        slice_end = connection_type.find("icon", slice_start) - 1
                        # Extract substring using slice.
                        connection_type = connection_type[slice_start:slice_end]
                        # Add to the list.
                        list_connection_type.append(connection_type)
                for span3 in span.find_all("span", class_="device-state"):
                    connection_type = str(span3.text).strip()
                    # Add to the list.
                    list_connection_type.append(connection_type)
        #
        for li in items_list[0].find_all("li", class_="item clickable last-item"):
            #
            for span in li.find_all("span", class_="icons-container"):
                for span1 in span.find_all("span", class_="connection-type-icon"):
                    for span2 in span1.find_all("span"):
                        # Convert a soup object into a string using direct type casting.
                        connection_type = str(span2)
                        # Using python slicing to extract the device type from the span element.
                        slice_start = connection_type.find("aria-label=") + 12
                        slice_end = connection_type.find("icon", slice_start) - 1
                        # Extract substring using slice.
                        connection_type = connection_type[slice_start:slice_end]
                        # Add to the list.
                        list_connection_type.append(connection_type)
                for span3 in span.find_all("span", class_="device-state"):
                    connection_type = str(span3.text).strip()
                    # Add to the list.
                    list_connection_type.append(connection_type)
        #
        # print(list_connection_type)
        #
        self.BlockDeviceUpdateTableStatusColumn.emit()


if __name__ == '__main__':
    mainWindow = MainWindowGui()
    mainWindow.show()
    sys.exit(app.exec_())