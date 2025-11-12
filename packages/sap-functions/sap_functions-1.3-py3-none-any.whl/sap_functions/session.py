from typing import Iterator


class SAPGridView:
    toolbarButtonCount: any
    columnOrder: list
    columnCount: int
    rowCount: int
    visibleRowCount: int
    def setCurrentCell(self, row: int, column: str) -> None: """If row and column identify a valid cell, this cell becomes the current cell. Otherwise, an exception is raised."""
    def doubleClickCurrentCell(self) -> None: """This function emulates a mouse double click on the current cell"""
    def clearSelection(self) -> None: """Calling clearSelection removes all row, column and cell selections"""
    def clickCurrentCell(self) -> None: """This function emulates a mouse click on the current cell"""
    def contextMenu(self) -> None: """Calling contextMenu emulates the context menu request"""
    def selectAll(self) -> None: """This function selects the whole grid content (i.e. all rows and all columns)."""
    def selectContextMenuItem(self, item: str) -> None: """Select an item from the control’s context menu"""
    def selectColumn(self, column: str) -> None: """This function adds the specified column to the collection of the selected columns"""
    def getCellValue(self, row: int, column: str) -> str: """Returns the value of the cell as a string"""


class SAPGuiInfo:
    user: str
    transaction: str
    program: str
    systemName: str
    client: str
    language: str
    guiCodepage: float
    group: str
    isLowSpeedConnection: bool
    messageServer: str
    responseTime: str
    sessionNumber: float
    systemName: str
    systemSessionId: str


class SAPGuiFrameWindow:
    name: str
    text: str
    type: str
    def close(self) -> None: """The function attempts to close the window. Trying to close the last main window of a session will not succeed immediately; the dialog ‘Do you really want to log off?’ will be displayed first"""


class SAPGuiScrollbar:
    position: int
    minimum: int
    maximum: int
    pageSize: int
    range: int


class GuiComponent:
    id: str
    name: str
    type: str
    text: str
    parent: "GuiComponent"
    count: int
    charLeft: str
    children: "GuiComponent"
    horizontalScrollbar: SAPGuiScrollbar
    verticalScrollbar: SAPGuiScrollbar

    def clickCurrentCell(self): ...
    def Select(self) -> None: ...
    def sendVKey(self, key: int) -> None: ...
    def setFocus(self) -> None: ...
    def visualize(self) -> None: ...
    def containerType(self) -> str: ...
    def change(self) -> None: ...
    def press(self) -> None: ...
    def __getitem__(self, index: int) -> "GuiComponent": ...
    def __iter__(self) -> Iterator["GuiComponent"]: ...


class SAPGuiSession:
    info: SAPGuiInfo
    activeWindow: SAPGuiFrameWindow
    isActive: bool

    def CreateSession(self) -> None: ...
    def EndTransaction(self) -> None: ...
    def findById(self, identifier: str) -> GuiComponent: ...
    def startTransaction(self, transaction: str) -> None: ...
