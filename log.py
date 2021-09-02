import datetime
import os


class Log():

    def __init__(self):
        self.directory_path = os.getcwd() + "\\logs"
        self.file_path = self.directory_path + "\\" + str(datetime.date.today()) + ".txt"
        self.current_day = self.get_current_date()


    def directory_create(self):
        try:
            if not os.path.exists(self.directory_path):
                os.mkdir(self.directory_path)
        except Exception as e:
            print(e)


    def file_create(self):
        try:
            if not os.path.exists(self.file_path):
                file = open(self.file_path, "w+") # create the file
                file.close()
            
            # If its out first time opening the file since we started up,
            # write a new line to make it a little neater
            with open(self.file_path, 'a') as file:
                file.write("\n=========================================================================================\n")
        except Exception as e:
            print(e)


    def write(self, text):
        """Writes to the end of the log file"""
        try:
            with open(self.file_path, 'a') as file:
                file.write(f"{text}\n")
        except Exception as e:
            print(e)


    def check_date(self, current_day):
        if current_day != self.get_current_date():
            # create new log file with new date
            self.file_path = self.directory_path + "\\" + str(self.get_current_date()) + ".txt"
            self.file_create()
            self.current_day = self.get_current_date()


    def get_current_date(self):
        return datetime.date.today()


    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")