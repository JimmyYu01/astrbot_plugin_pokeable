import random

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_pokeable",
    "JimmyYu01",
    "AstrBot 插件，提供在 OneBot v11 消息平台上处理戳一戳消息段的能力。",
    "1.0.5",
)
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        proactive_reply = self.config.get("proactive_reply", {})
        self.proactive_reply_enable = proactive_reply.get("enable", False)
        self.proactive_reply_probability = proactive_reply.get("probability", 0.0)

    @filter.llm_tool()
    async def send_poke(self, event: AstrMessageEvent, user_id: str = ""):
        """戳一戳指定用户。

        Args:
            user_id(string): 指定用户的 ID ，如果留空则指定为当前消息发送者。
        """
        if event.get_platform_name() == "aiocqhttp":
            from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
                AiocqhttpMessageEvent,
            )

            assert isinstance(event, AiocqhttpMessageEvent)
            client = event.bot
            user = str(user_id).strip() or event.get_sender_id()
            if event.is_private_chat():
                await client.call_action("send_poke", user_id=user)
            else:
                await client.call_action(
                    "send_poke",
                    group_id=event.get_group_id(),
                    user_id=user,
                )
            return f"你戳了戳 {user}"
        return "暂未适配当前消息平台"

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def proactive_reply(self, event: AstrMessageEvent):
        """被戳时主动回复。"""
        if event.get_platform_name() == "aiocqhttp":
            if not self.proactive_reply_enable:
                return
            if [
                m
                for m in event.get_messages()
                if isinstance(m, Comp.Poke) and str(m.id) == event.get_self_id()
            ] == []:
                return
            if not random.random() < self.proactive_reply_probability:
                return
            event.message_str = f"{event.get_sender_id()} 戳了戳你"
            event.is_at_or_wake_command = True

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
