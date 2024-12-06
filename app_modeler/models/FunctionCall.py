import logging
import re
from typing import Optional

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
            out += (arg.strip().strip('"'),)
        return out

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
    nf = FunctionCall(view='view', function_name="click_tab1",
                      args='"arg1", "arg2"', kwargs='key1="value1", key2="value2", "key3"="value3"')
    nf.test()
    print(str(nf))
    print(nf.get_args())
    print(nf.get_kwargs())

    dump = nf.model_dump()
    print(dump)
    nf2 = NextFunction(**dump)

    class View:
        def click_tab1(self, *args, **kwargs):
            print("click_tab1", args, kwargs)
            return "click_tab1"
    view = View()
    nf.call(view)
    print(dump)
