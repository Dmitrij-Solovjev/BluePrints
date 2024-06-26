from PySide6 import QtWidgets
from node_editor.gui.attributes import Node


class Timer_Event_Node(Node):
    timers_id = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.combo_box = QtWidgets.QComboBox()

        self.title_text = "Timer Event"
        self.type_text = "Timer Nodes"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(pin_text="::Ex Out", is_output=True, execution=True, visible=False)

    def combo_box_user_input(self, index):
        self.metadata["index"] = index
        self.title_text = f"Timer Event {index + 1}"
        self.build()

    def init_widget(self):

        # Combo Box
        index = self.metadata.get("index", 0)
        self.combo_box_user_input(index)
        self.combo_box.addItems(self.timers_id)
        self.combo_box.setCurrentIndex(index)
        self.combo_box.currentIndexChanged.connect(self.combo_box_user_input)
        self.combo_box.setFixedWidth(100)
        self.layout.addWidget(self.combo_box)

        super().init_widget()
