#Foreign imports
import sys
import PyQt6.QtWidgets as qtw

#Local imports
import card_selector as cs
import game

#Creates the Main Window
def initUI(window):
    #Set widgets to be displayed (central widget necessary)
    centralWidget = qtw.QWidget()
    window.setCentralWidget(centralWidget)
    window.layout = qtw.QVBoxLayout(centralWidget)

    #Add the play game button to window
    play_game = qtw.QPushButton("Play Game")
    play_game.clicked.connect(lambda x: window.select_game(4))
    window.layout.addWidget(play_game)

    #Add the play mega hand game button to window
    # play_game = qtw.QPushButton("Play Mega Hand Game")
    # play_game.clicked.connect(lambda x: window.select_game(8))
    # window.layout.addWidget(play_game)

    #Add the counter button to window
    card_counter = qtw.QPushButton("Card Counter")
    card_counter.clicked.connect(window.card_counter)
    window.layout.addWidget(card_counter)

#Class that adapts QMainWindow to fit our needs
class Main_Window(qtw.QMainWindow):
    #Initializes the class as a QMainWindow and calls initUI
    def __init__(self):
        super().__init__()
        initUI(self)

    def select_game(self, num_cards):
        game.initUI(self, num_cards)
    
    def card_counter(self):
        cs.initUI(self)

#Run window
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    window = Main_Window()
    window.setWindowTitle('Cribbage')
    window.setGeometry(100,100,400,510)
    window.show()
    sys.exit(app.exec())