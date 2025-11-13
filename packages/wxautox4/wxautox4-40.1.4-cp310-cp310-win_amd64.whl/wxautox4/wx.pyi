import abc
from .utils import GetAllWindows as GetAllWindows, uilock as uilock
from _typeshed import Incomplete
from abc import ABC
from typing import Callable, Literal, Union
from wxautox.msgs.base import Message as Message
from wxautox.ui.sessionbox import SessionElement as SessionElement
from wxautox4.logger import wxlog as wxlog
from wxautox4.param import PROJECT_NAME as PROJECT_NAME, WxParam as WxParam, WxResponse as WxResponse
from wxautox4.ui import WeChatMainWnd as WeChatMainWnd, WeChatSubWnd as WeChatSubWnd
from wxautox4.ui.base import BaseUISubWnd as BaseUISubWnd, BaseUIWnd as BaseUIWnd
from wxautox4.ui.component import NewFriendElement as NewFriendElement
from wxautox4.ui.moment import MomentsWnd as MomentsWnd, PrivacyConfig as PrivacyConfig

class Listener(ABC, metaclass=abc.ABCMeta): ...

class Chat:
    who: Incomplete
    def __init__(self, core: WeChatSubWnd = None) -> None: ...
    def __add__(self, other): ...
    def __radd__(self, other): ...
    def Show(self) -> None: ...
    def ChatInfo(self) -> dict[str, str]: ...
    @uilock
    def AtAll(self, msg: str, who: str = None, exact: bool = False) -> WxResponse: 
        """@所有人
        
        Args:
            msg (str): 发送的消息
            who (str, optional): 发送给谁. Defaults to None.
            exact (bool, optional): 是否精确匹配. Defaults to False.

        Returns:
            WxResponse: 发送结果
        """
    @uilock
    def SendMsg(self, msg: str, who: str = None, clear: bool = True, at: str | list[str] = None, exact: bool = False) -> WxResponse: 
        """发送消息

        Args:
            msg (str): 消息内容
            who (str, optional): 发送对象，不指定则发送给当前聊天对象，**当子窗口时，该参数无效**
            clear (bool, optional): 发送后是否清空编辑框.
            at (Union[str, List[str]], optional): @对象，不指定则不@任何人
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False，**当子窗口时，该参数无效**

        Returns:
            WxResponse: 是否发送成功
        """
    @uilock
    def SendFiles(self, filepath, who: Incomplete | None = None, exact: bool = False) -> WxResponse: 
        """向当前聊天窗口发送文件
        
        Args:
            filepath (str|list): 要复制文件的绝对路径  
            who (str): 发送对象，不指定则发送给当前聊天对象，**当子窗口时，该参数无效**
            exact (bool, optional): 搜索who好友时是否精确匹配，默认False，**当子窗口时，该参数无效**
            
        Returns:
            WxResponse: 是否发送成功
        """
    def GetAllMessage(self) -> list['Message']: 
        """获取当前聊天窗口的所有消息
        
        Returns:
            List[Message]: 当前聊天窗口的所有消息
        """
    def GetNewMessage(self) -> list['Message']: 
        """获取当前聊天窗口的新消息

        Returns:
            List[Message]: 当前聊天窗口的新消息
        """
    def Close(self) -> None: """关闭微信窗口"""

class WeChat(Chat, Listener):
    NavigationBox: Incomplete
    SessionBox: Incomplete
    ChatBox: Incomplete
    myinfo: Incomplete
    nickname: Incomplete
    listen: Incomplete
    def __init__(self, nickname: str = None, start_listener: bool = False, debug: bool = False, **kwargs) -> None: ...
    @property
    def path(self): ...
    @property
    def dir(self): ...
    def GetMyInfo(self) -> dict[str, str]: """获取我的信息"""
    def KeepRunning(self) -> None: """保持运行"""
    def IsOnline(self) -> bool: """判断是否在线"""
    def GetSession(self) -> list['SessionElement']: 
        """获取当前会话列表

        Returns:
            List[SessionElement]: 当前会话列表
        """
    @uilock
    def ChatWith(self, who: str, exact: bool = True, force: bool = False, force_wait: float | int = 0.5): 
        """打开聊天窗口
        
        Args:
            who (str): 要聊天的对象
            exact (bool, optional): 搜索who好友时是否精确匹配，默认True
            force (bool, optional): 不论是否匹配到都强制切换，若启用则exact参数无效，默认False
                > 注：force原理为输入搜索关键字后，在等待`force_wait`秒后不判断结果直接回车，谨慎使用
            force_wait (Union[float, int], optional): 强制切换时等待时间，默认0.5秒
            
        """
    def GetSubWindow(self, nickname: str) -> Chat: 
        """获取子窗口实例
        
        Args:
            nickname (str): 要获取的子窗口的昵称
            
        Returns:
            Chat: 子窗口实例
        """
    def GetAllSubWindow(self) -> list['Chat']: 
        """获取所有子窗口实例
        
        Returns:
            List[Chat]: 所有子窗口实例
        """
    @uilock
    def AddListenChat(self, nickname: str, callback: Callable[[Message, Chat], None]) -> WxResponse: 
        """添加监听聊天，将聊天窗口独立出去形成Chat对象子窗口，用于监听
        
        Args:
            nickname (str): 要监听的聊天对象
            callback (Callable[['Message', Chat], None]): 回调函数，参数为(Message对象, Chat对象)，返回值为None
        """
    def StopListening(self, remove: bool = True) -> None: 
        """停止监听
        
        Args:
            remove (bool, optional): 是否移除监听对象. Defaults to True.
        """
    def StartListening(self) -> None: ...
    @uilock
    def RemoveListenChat(self, nickname: str, close_window: bool = True) -> WxResponse: 
        """移除监听聊天

        Args:
            nickname (str): 要移除的监听聊天对象
            close_window (bool, optional): 是否关闭聊天窗口. Defaults to True.

        Returns:
            WxResponse: 执行结果
        """
    def Moments(self, timeout: int = 3) -> MomentsWnd: 
        """进入朋友圈"""
    def PublishMoment(self, text: str = None, media_files: list[str] = None, privacy_config: PrivacyConfig = None): 
        """发布朋友圈

        Args:
            text (str, optional): 文本内容. Defaults to None.
            media_files (List[str], optional): 媒体文件列表. Defaults to None.
            privacy_config (PrivacyConfig, optional): 朋友圈隐私设置. Defaults to None.

        Returns:
            WxResponse: 发布结果

        Example:
            
            text = '今天心情不错'
            media_files = [
                "C:/Users/Xingh/Pictures/1.png",
                "C:/Users/Xingh/Pictures/2.png",
                "C:/Users/Xingh/Pictures/3.png",
            ]
            privacy_config = {
                'privacy': '白名单',    # 设置为黑名单模式
                'tags': ['test1','test3']      # 白名单为仅这些标签能看，黑名单为屏蔽这些标签的人
            }

            wx.PublishMoment(
                text=text,
                media_files=media_files,
                privacy_config=privacy_config
            )
            
        """
    def AddNewFriend(self, keywords: str, addmsg: str = None, remark: str = None, tags: list[str] = None, permission: Literal['朋友圈', '仅聊天'] = '朋友圈') -> WxResponse: 
        """添加新的好友

        Args:
            keywords (str): 搜索关键词，可以是昵称、微信号、手机号等
            addmsg (str, optional): 添加好友时的附加消息，默认为None
            remark (str, optional): 添加好友后的备注，默认为None
            tags (list, optional): 添加好友后的标签，默认为None
            permission (Literal['朋友圈', '仅聊天'], optional): 添加好友后的权限，默认为'朋友圈'
            timeout (int): 搜索微信号超时时间，默认5秒

        Returns:
            WxResponse: 添加好友的结果
        """
    def GetNewFriends(self, acceptable: bool = True) -> list['NewFriendElement']: 
        """获取新的好友申请列表

        Args:
            acceptable (bool, optional): 是否过滤掉已接受的好友申请
        
        Returns:
            List['NewFriendElement']: 新的好友申请列表，元素为NewFriendElement对象，可直接调用Accept方法

        Example:
            >>> wx = WeChat()
            >>> newfriends = wx.GetNewFriends(acceptable=True)
            >>> tags = ['标签1', '标签2']
            >>> for friend in newfriends:
            ...     remark = f'备注{friend.name}'
            ...     friend.Accept(remark=remark, tags=tags)  # 接受好友请求，并设置备注和标签
        """
    def GetNextNewMessage(self, filter_mute=False, callback=None) -> dict[str, list['Message']]:
        """获取下一个新消息
        
        Args:
            filter_mute (bool, optional): 是否过滤掉免打扰消息. Defaults to False.
            callback (Callable[['Message'], None]): 回调函数，参数为(Message对象)，返回值为None

        Returns:
            Dict[str, List['Message']]: 消息列表
        """
    def SendUrlCard(self, url: str, friends: Union[str, list[str]], message: str=None,timeout: int=10) -> WxResponse:
        """发送链接卡片

        Args:
            url (str): 链接地址
            friends (Union[str, List[str]], optional): 发送对象
            message (str): 附加消息，默认无
            timeout (int, optional): 等待时间，默认10秒

        Returns:
            WxResponse: 发送结果
        """
    def GetAllRecentGroups(self,speed: int = 1,interval: float = 0.1):
        """获取所有最近群聊
        
        Args:
            speed (int, optional): 获取速度，默认为1
            interval (float, optional): 获取间隔，默认为0.1秒

        Returns:
            List[Tuple]: 所有最近群聊列表
        """
    def SwitchToChat(self) -> None: """切换到聊天页面"""
    def SwitchToContact(self) -> None: """切换到联系人页面"""
    def ShutDown(self) -> None: """杀掉微信进程"""
