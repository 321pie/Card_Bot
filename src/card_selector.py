#Foreign imports
import PyQt6.QtWidgets as qtw

#Local imports
import calculate_points
import home
import deck


flipped = None
hand = []
cards = 0

#Creates new rank and suit boxes adds it to layout then increments how many cards you have
def add_new_card(window):
    global flipped
    global hand
    global cards

    window.card_layout.addWidget(make_rank_box(), cards, 1)
    cards += 1
    window.layout.itemAt(4).widget().setText(f"Personal Hand ({cards})")

#Removes last card in the list
def remove_card(window):
    global flipped
    global hand
    global cards

    if cards != 1:
        rank = window.card_layout.itemAtPosition(cards-1,1).widget()
        window.card_layout.removeWidget(rank)
        cards -= 1
        window.layout.itemAt(4).widget().setText(f"Personal Hand ({cards})")

#Creates the GUI
def initUI(window, num_cards=4):
    global flipped
    global hand
    global cards

    flipped = None
    hand = []
    cards = 0

    #Set widgets to be displayed (central widget necessary)
    centralWidget = qtw.QWidget()
    window.setCentralWidget(centralWidget)
    window.layout = qtw.QVBoxLayout(centralWidget)

    #Add the back to home button
    window.home = qtw.QPushButton("Back to Home")
    window.home.clicked.connect(lambda x: home.initUI(window))
    window.layout.addWidget(window.home)
    window.layout.addWidget(qtw.QLabel(""))

    #Add the Add Card button to top of window
    add_card = qtw.QPushButton("Add Card")
    add_card.clicked.connect(lambda x: add_new_card(window))
    window.layout.addWidget(add_card)

    #Add the Remove Card button to top of window
    remove_card_button = qtw.QPushButton("Remove Card")
    remove_card_button.clicked.connect(lambda x: remove_card(window))
    window.layout.addWidget(remove_card_button)

    #Flipped Card
    window.layout.addWidget(qtw.QLabel("Flipped Card"))
    window.flipped_layout = qtw.QGridLayout()
    window.layout.addLayout(window.flipped_layout)
    window.flipped_layout.addWidget(make_suit_box(), 0, 0)
    window.flipped_layout.addWidget(make_rank_box(), 0, 1)

    #Set up the new card layout
    window.layout.addWidget(qtw.QLabel("Personal Hand (4)"))
    scroll = qtw.QScrollArea()
    window.card_layout = qtw.QGridLayout()
    wrapper_widget = qtw.QWidget()
    wrapper_widget.setLayout(window.card_layout)
    scroll.setWidget(wrapper_widget)
    scroll.setWidgetResizable(True)
    window.layout.addWidget(scroll)

    #Add a checkbox for flush
    window.flush_layout = qtw.QGridLayout()
    window.flush_layout.addWidget(make_suit_box(), 0, 0)
    window.flush_layout.addWidget(qtw.QCheckBox(), 0, 1)
    window.layout.addWidget(qtw.QLabel("Flush?"))
    window.layout.addLayout(window.flush_layout)

    #Add a checkbox for nobs
    window.nobs_layout = qtw.QGridLayout()
    window.nobs_layout.addWidget(qtw.QCheckBox())
    window.layout.addWidget(qtw.QLabel("Nobs?"))
    window.layout.addLayout(window.nobs_layout)

    #Add a checkbox for crib
    window.crib_layout = qtw.QGridLayout()
    window.crib_layout.addWidget(qtw.QCheckBox())
    window.layout.addWidget(qtw.QLabel("Crib?"))
    window.layout.addLayout(window.crib_layout)

    #Add the done button to bottom of window
    window.layout.addWidget(qtw.QLabel(""))
    window.done = qtw.QPushButton("Done")
    window.done.clicked.connect(lambda x: make_cards(window))
    window.layout.addWidget(window.done)

    #Have 4 cards already in window
    for i in range(num_cards):
        add_new_card(window)
        i += 1

#Does calculation once "Done" is clicked
def make_cards(window):
    global flipped
    global hand
    global cards

    suits = [deck.HEART, deck.DIAMOND, deck.CLUB, deck.SPADE]
    suit = window.flipped_layout.itemAtPosition(0,0).widget()
    rank = window.flipped_layout.itemAtPosition(0,1).widget()
    if isinstance(suit, qtw.QComboBox) and isinstance(rank, qtw.QComboBox):
        suit = suit.currentText()
        rank = rank.currentText()
        suits.remove(suit)
    flipped = deck.Card(rank, suit)

    #Make a card for every entry in form and add it to Card Array
    did_nobs = False
    for i in range(cards):
        
        suit = suits[i % 3]
        rank = window.card_layout.itemAtPosition(i,1).widget()
        if isinstance(rank, qtw.QComboBox):
            rank = rank.currentText()
            if(window.flush_layout.itemAtPosition(0,1).widget().isChecked()): #Check for flush
                suit = window.flush_layout.itemAtPosition(0,0).widget().currentText()
            elif(window.nobs_layout.itemAtPosition(0,0).widget().isChecked() and rank == 'J' and did_nobs == False):
                suit = flipped.suit
                did_nobs = True

            hand.append(deck.Card(rank, suit))

    points = 0
    output = ''
    #Get score to display until clicked
    if(window.crib_layout.itemAtPosition(0,0).widget().isChecked()):
        [points, output] = calculate_points.calculate_crib(hand, flipped)
    else:
        [points, output] = calculate_points.calculate_hand(hand, flipped)

    #Initiate layout
    centralWidget = qtw.QWidget()
    window.setCentralWidget(centralWidget)
    window.layout = qtw.QVBoxLayout(centralWidget)

    #Add the points button to return to the game
    button = qtw.QPushButton(f'{points} points\n\n(Click here for next hand)', window)
    button.clicked.connect(lambda: initUI(window, len(hand)))
    window.layout.addWidget(button)

    #Add the scroll box for the score output
    scroll = qtw.QScrollArea()
    output_widget = qtw.QLabel(f"{output}")
    scroll.setWidget(output_widget)
    scroll.setWidgetResizable(True)
    window.layout.addWidget(scroll)

#Add suits to combo box same way calculator takes them
def make_suit_box():
    suit_box = qtw.QComboBox()

    for suit in deck.SUITS:
        suit_box.addItem(suit)
    
    return suit_box

#Add cards to combo box same way that calculator takes them
def make_rank_box():
    rank_box = qtw.QComboBox()
    for value in deck.VALUES:
        rank_box.addItem(value)
    return rank_box