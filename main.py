import sys
from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow

if __name__ == '__main__':

    firebase = None
    try:
        from Database.Cloud import FirebaseThread
        from Database.users_db import FirebaseUser
        firebase = FirebaseUser()
        firebaseThread = FirebaseThread(firebase)
        firebaseThread.start()
    except Exception as e:
        print(f"[INFO] Firebase not available, continuing without it: {e}")

    app = QApplication(sys.argv)
    window = MainWindow(firebase)
    window.show()
    sys.exit(app.exec())
