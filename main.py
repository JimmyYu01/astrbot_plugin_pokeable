import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_pokeable",
    "JimmyYu01",
    "让AstrBot能够主动处理戳一戳消息段。",
    "1.0.1",
)
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.llm_tool()
    async def send_poke(self, event: AstrMessageEvent, user_id: str = ""):
        """戳一戳指定用户。

        Args:
            user_id(string): 指定用户的QQ号。如果留空则指定为当前消息发送者。
        """
        if event.get_platform_name() == "aiocqhttp":
            from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
                AiocqhttpMessageEvent,
            )

            assert isinstance(event, AiocqhttpMessageEvent)
            client = event.bot
            user_poked = str(user_id).strip() or event.get_sender_id()
            if event.is_private_chat():
                await client.call_action("send_poke", user_id=user_poked)
            else:
                await client.call_action(
                    "send_poke",
                    group_id=event.get_group_id(),
                    user_id=user_poked,
                )
            return f"戳了一下{user_poked}"
        return "当前消息平台不支持戳一戳"

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def reply_poke(self, event: AstrMessageEvent):
        """主动回复戳一戳。"""
        if not self.config.get("reply", False):
            return
        for message in event.get_messages():
            if (
                not isinstance(message, Comp.Poke)
                or str(message.id) != event.get_self_id()
            ):
                break
            event.message_str = f"你被{event.get_sender_id()}戳了一下"
            event.is_at_or_wake_command = True

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
