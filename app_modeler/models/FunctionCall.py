import logging
import re
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QMetaObject, Qt, Q_ARG, Q_RETURN_ARG
from PySide6.QtWidgets import QInputDialog
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class NextFunction(BaseModel):
    view: str
    function_name: str
    args: str
    kwargs: str

    def __post_init_post_parse__(self):
        # cleanup if the function name has parenthesis
        self.function_name = self.function_name.rstrip('()')

class NextFunctionList(BaseModel):
    candidates: list[NextFunction]

class FunctionCall(NextFunction):
    return_value: Optional[str] = None
    error: Optional[object] = None

    def get_args(self) -> tuple:
        out = ()
        for arg in self.args.split(','):
            item = (arg.strip().strip('"'),)
            if re.match(r'^{([^}]*)}$', item[0]):
                value = self.get_input_from_user(item[0])
                logger.debug(f'User input: {value}')
                item = (f'"{value}"',)
                self.args = self.args.replace(arg, item[0])
            out += item
        return out

    @staticmethod
    def get_input_from_user(arg: str) -> str:
        # make this call using main thread
        logger.debug(f"Requesting input from user for {arg}")
        result: str = QMetaObject.invokeMethod(
            QApplication.instance().widget,
            "get_text_from_user",
            Qt.BlockingQueuedConnection,
            Q_RETURN_ARG(str),
            Q_ARG(str, arg))
        if not result:
            raise StopIteration('User cancelled input')
        return result

    def get_kwargs(self) -> dict:
        out = {}
        for arg in self.kwargs.split(','):
            key_value = arg.split('=')
            if len(key_value) == 2:
                key, value = key_value
                out[key.strip().strip('"')] = value.strip().strip('"')
            else:
                logger.warning(f"Invalid key-value pair: {arg}")
        return out

    def test(self):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.view):
            raise ValueError(f"Invalid view name: {self.view}")
        # function name can be a regex
        if not(self.function_name.startswith('/') and self.function_name.endswith('/')):
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.function_name):
                raise ValueError(f"Invalid function name: {self.function_name}")
        if self.args != '' and not re.match(r'^"([^"]*)"(?:,\s*"([^"]*)")*$', self.args):
            raise ValueError(f"Invalid args: {self.args}")
        if self.kwargs != '' and not re.match(r'^(?:"\w+"|\w+)=(?:"[^"]+"|\d+)(?:,\s*(?:"\w+"|\w+)=(?:"[^"]+"|\d+))*$', self.kwargs):
            raise ValueError(f"Invalid kwargs: {self.kwargs}")

    def __str__(self):
        args = f"{self.args}"
        if self.kwargs:
            args += f", {self.kwargs}"
        return f"{self.function_name}({args})"

    def call(self, view: object):
        """ Call the next function in the view."""
        func_name = self.function_name
        next_func = getattr(view, func_name)
        if next_func is None:
            logger.info("No next step available")
            raise StopIteration('No next step available')
        # select the right call
        try:
            if self.args and self.kwargs:
                return_value = next_func(*self.get_args(), **self.get_kwargs())
            elif self.args:
                return_value = next_func(*self.get_args())
            elif self.kwargs:
                return_value = next_func(**self.get_kwargs())
            else:
                return_value = next_func()
            self.return_value = return_value
            return return_value
        except Exception as error:
            self.error = error
            raise error


if __name__ == "__main__":
    import threading
    from PySide6.QtWidgets import QWidget, QPushButton
    from PySide6.QtCore import Slot
    import sys
    class View:
        def click_tab1(self, *args, **kwargs):
            print("click_tab1", args, kwargs)
    class MainApp(QApplication):
        def __init__(self, *args):
            super().__init__(*args)
            self.widget = QPushButton()
            self.widget.show()
            self.widget.clicked.connect(self.on_start_thread)

        @Slot(str, result=str)
        def get_text_from_user(self, arg: str) -> str:
            text, ok = QInputDialog.getText(self.widget, "Input", f"Enter input for {arg}:")
            if ok:
                return text
            return ""

        def on_start_thread(self):
            view = View()
            nf = FunctionCall(view='view', function_name="click_tab1",
                              args='"{arg1}", "arg2"', kwargs="")
            thread = threading.Thread(target=nf.call, args=(view,))
            thread.start()
            #thread.join()

    app = MainApp()
    sys.exit(app.exec())
    #value = FunctionCall.get_input_from_user("arg1")
    #print(value)
    #sys.exit(0)

    nf = FunctionCall(view='view', function_name="click_tab1",
                      args='"{arg1}", "arg2"', kwargs='key1="value1", key2="value2", "key3"="value3"')
    nf.test()
    print(str(nf))
    print(nf.get_args())
    print(nf.get_kwargs())

    dump = nf.model_dump()
    print(dump)
    nf2 = NextFunction(**dump)


    view = View()

    nf.call(view)

    #thread = threading.Thread(target=nf.call, args=(view,))
    #thread.start()
    #thread.join()
    print(dump)
