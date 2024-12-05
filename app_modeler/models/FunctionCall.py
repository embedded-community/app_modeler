import logging
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class NextFunction(BaseModel):
    view: str
    function_name: str
    args: str
    kwargs: str

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
                out[key.strip()] = value.strip().strip('"')
            else:
                logger.warning(f"Invalid key-value pair: {arg}")
        return out

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
                      args='"arg1", "arg2"', kwargs='key1="value1", key2="value2"')
    print(nf)
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
