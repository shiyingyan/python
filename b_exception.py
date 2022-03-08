# -*- coding:UTF-8 -*-

class MJException(Exception):
    pass

class ApiError(Exception):
    def __init__(self, provider, err_code, msg):
        super().__init__(f'{{"{provider}{err_code}":"{msg}"}}')
        self.provider = provider
        self.err_code = err_code
        self.msg = msg