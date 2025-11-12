# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 20:07:00 2019
Created on Python3.6.8
@author:liwancai
    QQ:248411282
    Tel:13199701121
"""
import os,logbook,sys
from datetime       import datetime
from logbook.more   import ColorizedStderrHandler
from logbook        import Logger, TimedRotatingFileHandler

################################################################################
def FormatLogInfo(record, handler):
    color_code = {
        'INFO': '\033[92m',   
        'DEBUG':'\033[36m',
        'ERROR': '\033[31m',   
        'CRITICAL': '\033[35m', 
        'NOTICE': '\033[38;5;208m',  
        'WARNING': '\033[33m',  
    }
    log = "\033[0m[{dt}]{bold}{color}[{level}][{filename}][{func_name}][{lineno}]↓↓↓\n{msg}\033[0m\n{rn}".format(
        rn="-"*64,
        dt=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 时间
        filename=os.path.split(record.filename)[-1],  # 文件名
        func_name=record.func_name,  # 函数名
        level=record.level_name,  # 日志等级
        lineno=record.lineno,  # 行号
        bold='\033[1m',  # 设置为粗体
        color=color_code.get(record.level_name, ''),  # 颜色代码
        msg=record.message,  # 内容
    )
    return log

################################################################################
class _Log(object):
    logpath = os.path.join("./logs/")
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    handler = ColorizedStderrHandler(bubble=True)
    handler.formatter = FormatLogInfo
    logitems = {
        "Info": Logger('INFO', level=logbook.INFO),
        "Trace": Logger('TRACE', level=logbook.TRACE),
        "Debug": Logger('DEBUG', level=logbook.DEBUG),
        "Error": Logger('ERROR', level=logbook.ERROR),
        "Notice": Logger('NOTICE', level=logbook.NOTICE),
        "Warning": Logger('WARNING', level=logbook.WARNING),
        "Critical": Logger('CRITICAL', level=logbook.CRITICAL)
    }
    for level, _ in logitems.items():#
        file_handler = TimedRotatingFileHandler( date_format='%Y%m%d',  bubble=True,
        filename =os.path.join( logpath,f"{os.path.splitext(os.path.basename(sys.argv[0]))[0]}_{level}.log"))
        file_handler.formatter = FormatLogInfo
        logitems[level].handlers.append(handler)
        logitems[level].handlers.append(file_handler)

    Info = logitems["Info"].info
    Trace = logitems["Trace"].trace
    Debug = logitems["Debug"].debug
    Error = logitems["Error"].error
    Notice = logitems["Notice"].notice
    Warn = logitems["Warning"].warning
    Critical = logitems["Critical"].critical
    
log = _Log()
 
if __name__ == '__main__':
    def run():
        log.Info("This is an info message")
        log.Trace("This is a trace message")
        log.Debug("This is a debug message")
        log.Error("This is an error message")
        log.Notice("This is a notice message")
        log.Warn("This is a warning message")
        log.Critical("This is a critical message")
    run()