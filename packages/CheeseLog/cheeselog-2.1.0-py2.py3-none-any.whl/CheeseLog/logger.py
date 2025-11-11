import sys, datetime, re, time, os, threading, queue, atexit, io

from CheeseLog import style
from CheeseLog.message import Message
from CheeseLog.filter import Filter

TAG_PATTERN = re.compile(r'<.+?>')
TAG_PATTERN_REPL = lambda m: f'\033[{getattr(style, (m.group()[2:] if "/" in m.group() else m.group()[1:])[:-1].upper())[1 if "/" in m.group() else 0]}m'

class CheeseLogger:
    __slots__ = ('key', 'file_path', 'messages', 'message_template', 'timer_template', 'message_template_styled', '_is_running', '_has_console', 'filter', '_queue', '_thread_handler')

    instances: dict[str, CheeseLogger] = {}
    ''' 所有CheeseLogger实例 '''

    def __init__(self, key: str | None = None, file_path: str | None = None, *, messages: dict[str, Message] = {}, message_template: str = '(%k) %t > %c', timer_template: str = '%Y-%m-%d %H:%M:%S.%f', message_template_styled: str = '(<black>%k</black>) <black>%t</black> > %c', filter: Filter = {}):
        '''
        - Static
            - instances: 所有CheeseLogger实例

        - Args
            - file_path: 日志文件路径，若不设置则不会写入文件
            - messages: 消息类型
            - message_template: 消息模版；支持的占位符有：
                - %k: key
                - %t: 时间模版
                - %c: 内容
            - timer_template: 时间模版
            - message_template_styled: 带样式的消息模版；支持的占位符有：
                - %k: key
                - %t: 时间模版
                - %c: 内容
                支持的样式标签有：
                - faint: 弱化
                - intalic: 斜体
                - underline: 下划线
                - reverse_color: 反色
                - hidden: 隐藏
                - strikethough: 删除线
                - double_underscore: 双下划线
                - black
                - red
                - green
                - yellow
                - blue
                - nagenta
                - cyan
                - white
                - bg_black
                - bg_red
                - bg_green
                - bg_yellow
                - bg_blue
                - bg_magenta
                - bg_cyan
                - bg_white
                - overline: 上划线
                - light_black
                - light_red
                - light_green
                - light_yellow
                - light_blue
                - light_magenta
                - light_cyan
                - light_white
                - bg_light_black
                - bg_light_red
                - bg_light_green
                - bg_light_yellow
                - bg_light_blue
                - bg_light_magenta
                - bg_light_cyan
                - bg_light_white
            - filter: 过滤器

        - Examples:
```python
""" 带有日志文件输出的简易应用 """
from CheeseLog import CheeseLogger, Message

logger = CheeseLogger(key = 'myLogger', file_path = 'logs/%Y-%m-%d.log')

logger.debug('This is a debug message.')
logger.info('This is an info message.')
logger.warning('This is a warning message.')
logger.danger('This is a danger message.')
logger.error('This is an error message.')

logger.add_message(Message('CUSTOM', 30, message_template_styled = '(<blue>%k</blue>) <black>%t</black> > %c'))
logger.print('CUSTOM', 'This is a custom message.')


""" 简单的消息过滤 """
from CheeseLog import CheeseLogger, Message

logger = CheeseLogger(key = 'myLogger')
logger.set_filter({
    'weight': 20,
    'message_keys': [ 'FILTERED' ]
})

low_weight_message = Message('LOW_WEIGHT', 10)
logger.add_message(low_weight_message)
high_weight_message = Message('HIGH_WEIGHT', 50)
logger.add_message(high_weight_message)
filtered_message = Message('FILTERED', 100)
logger.add_message(filtered_message)

logger.print('LOW_WEIGHT', 'This is a low weight message.') # 不会输出
logger.print('HIGH_WEIGHT', 'This is a high weight message.')
logger.print('FILTERED', 'This is a filtered message.') # 不会输出


""" 如何使用进度条实现一个loading效果 """
import time, random

from CheeseLog import CheeseLogger, Message, ProgressBar

logger = CheeseLogger(key = 'myLogger', file_path = 'logs/%Y-%m-%d.log')

loadingMessage = Message('LOADING')
logger.add_message(loadingMessage)
loadedMessage = Message('LOADED', 20, message_template_styled = '(<green>%k</green>) <black>%t</black> > %c')
logger.add_message(loadedMessage)

progress_bar = ProgressBar()
i = 0
while i < 100:
    bar, bar_styled = progress_bar(i / 100)
    logger.print('LOADING', bar, bar_styled, refresh = i != 0)
    time.sleep(random.uniform(0.05, 0.15))
    i += random.uniform(0.5, 1)
logger.print('LOADED', 'Loading complete!', refresh = True)
```
        '''

        self._key: str = key
        self.file_path: str | None = file_path
        ''' 日志文件路径 '''
        self.messages: dict[str, Message] = {
            'DEBUG': Message('DEBUG', 10),
            'INFO': Message('INFO', 20, message_template_styled = '(<green>%k</green>) <black>%t</black> > %c'),
            'WARNING': Message('WARNING', 30, message_template_styled = '(<yellow>%k</yellow>) <black>%t</black> > %c'),
            'DANGER': Message('DANGER', 40, message_template_styled = '(<red>%k</red>) <black>%t</black> > %c'),
            'ERROR': Message('ERROR', 50, message_template_styled = '(<magenta>%k</magenta>) <black>%t</black> > %c')
        } | messages
        ''' 消息类型 '''
        self.message_template: str = message_template
        ''' 消息模版 '''
        self.timer_template: str = timer_template
        ''' 时间模版 '''
        self.message_template_styled: str = message_template_styled
        ''' 带样式的消息模版 '''
        self.filter: Filter = filter
        ''' 过滤器 '''

        self._is_running: bool = True
        ''' 是否正在运行 '''
        self._has_console: bool = sys.stdout.isatty()
        ''' 是否有控制台输出 '''
        self._queue: queue.Queue = queue.Queue()
        ''' 消息队列 '''
        self._thread_handler: threading.Thread | None = threading.Thread(target = self._thread_handle, daemon = True)
        ''' 专用线程池 '''

        ''' 初始化 '''
        self.filter.setdefault('weight', -1)
        self.filter.setdefault('message_keys', set([]))
        self.filter['message_keys'] = set(self.filter['message_keys'])

        self._thread_handler.start()
        atexit.register(self.stop)

        if key in CheeseLogger.instances:
            raise KeyError(f'CheeseLogger "{key}" already exists')
        CheeseLogger.instances[key] = self

    def add_message(self, message: Message):
        ''' 添加消息类型 '''

        self.messages[message.key] = message

    def delete_message(self, key: str):
        ''' 删除消息类型 '''

        if key in self.messages:
            del self.messages[key]

    def start(self):
        ''' 启动日志记录 '''

        if self._is_running is True:
            return

        self._is_running = True
        self._thread_handler = threading.Thread(target = self._thread_handle, daemon = True)
        self._thread_handler.start()

    def stop(self):
        ''' 停止日志记录 '''

        if self._is_running is False:
            return

        self._queue.put(None)
        try:
            self._thread_handler.join()
        except KeyboardInterrupt:
            ...
        self._thread_handler = None
        self._is_running = False

    def set_filter(self, filter: Filter):
        ''' 设置过滤器 '''

        self.filter |= filter
        self.filter['message_keys'] = set(self.filter['message_keys'])

    def _thread_handle(self):
        while True:
            messages = [self._queue.get()]
            while not self._queue.empty():
                messages.append(self._queue.get())

            _log_content: str = ''
            last_file_path: str | None = None
            f: io.TextIOWrapper | None = None

            for _message in messages:
                if _message is None:
                    if f:
                        if _log_content:
                            f.write(_log_content)
                        f.close()
                    return

                message: Message = _message[0]
                content = _message[1]
                content_styled = _message[2]
                message_key = _message[3]
                end = _message[4]
                refresh = _message[5]
                now: datetime.datetime = _message[6]

                if message_key in self.filter['message_keys'] or message.weight <= self.filter['weight']:
                    continue

                if self._has_console:
                    content_styled = TAG_PATTERN.sub(TAG_PATTERN_REPL, (message.message_template_styled or self.message_template_styled).replace('%t', now.strftime(self.timer_template)).replace('%k', message_key).replace('%c', f'{content_styled or content}'))

                    if refresh:
                        content_styled = f'\033[F\033[K{content_styled}'

                    sys.stdout.write(f'{content_styled.replace("%lt;", "<").replace("%gt;", ">")}{end}')
                    sys.stdout.flush()

                if self.file_path:
                    try:
                        file_path = now.strftime(self.file_path)
                    except:
                        file_path = self.file_path
                    if file_path != last_file_path:
                        if f:
                            f.close()
                        os.makedirs(os.path.dirname(file_path), exist_ok = True)
                        f = open(file_path, 'a', encoding = 'utf-8')
                        last_file_path = file_path

                    _log_content += f'{(message.message_template or self.message_template).replace("%t", now.strftime(self.timer_template)).replace("%k", message_key).replace("%c", content).replace("%lt;", "<").replace("%gt;", ">")}\n'
                else:
                    if f:
                        f.close()
                        f = None
                    last_file_path = None

            if f and _log_content:
                f.write(_log_content)
                f.flush()

    def print(self, message_key: str, content: str, content_styled: str | None = None, *, end: str = '\n', refresh: bool = False):
        '''
        打印日志

        - Args
            - content: 消息内容
            - key: 消息类型
            - content_styled: 带样式的消息内容
            - end: 结尾符
            - refresh: 是否刷新终端输出
        '''

        if not self._is_running:
            return

        message = self.messages.get(message_key)
        if message is None:
            raise KeyError(f'Message "{message_key}" does not exist')

        self._queue.put((message, content, content_styled, message_key, end, refresh, datetime.datetime.now()))

    def debug(self, content: str, content_styled: str | None = None, *, end: str = '\n', refresh: bool = False):
        '''
        打印DEBUG日志

        - Args
            - content: 消息内容
            - content_styled: 带样式的消息内容
            - end: 结尾符
            - refresh: 是否刷新终端输出
        '''

        self.print('DEBUG', content, content_styled, end = end, refresh = refresh)

    def info(self, content: str, content_styled: str | None = None, *, end: str = '\n', refresh: bool = False):
        '''
        打印INFO日志

        - Args
            - content: 消息内容
            - content_styled: 带样式的消息内容
            - end: 结尾符
            - refresh: 是否刷新终端输出
        '''

        self.print('INFO', content, content_styled, end = end, refresh = refresh)

    def warning(self, content: str, content_styled: str | None = None, *, end: str = '\n', refresh: bool = False):
        '''
        打印WARNING日志

        - Args
            - content: 消息内容
            - content_styled: 带样式的消息内容
            - end: 结尾符
            - refresh: 是否刷新终端输出
        '''

        self.print('WARNING', content, content_styled, end = end, refresh = refresh)

    def danger(self, content: str, content_styled: str | None = None, *, end: str = '\n', refresh: bool = False):
        '''
        打印DANGER日志

        - Args
            - content: 消息内容
            - content_styled: 带样式的消息内容
            - end: 结尾符
            - refresh: 是否刷新终端输出
        '''

        self.print('DANGER', content, content_styled, end = end, refresh = refresh)

    def error(self, content: str, content_styled: str | None = None, *, end: str = '\n', refresh: bool = False):
        '''
        打印ERROR日志

        - Args
            - content: 消息内容
            - content_styled: 带样式的消息内容
            - end: 结尾符
            - refresh: 是否刷新终端输出
        '''

        self.print('ERROR', content, content_styled, end = end, refresh = refresh)

    def encode(self, content: str) -> str:
        ''' 当内容中有`'<'`和`'>'`字符时，进行转义 '''

        return content.replace('<', '%lt;').replace('>', '%gt;')

    @property
    def is_running(self) -> bool:
        ''' 是否正在运行 '''

        return self._is_running

    @property
    def has_console(self) -> bool:
        ''' 是否有控制台输出 '''

        return self._has_console

    @property
    def key(self) -> str:
        return self._key
