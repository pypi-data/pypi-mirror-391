from typing import Optional, Tuple

import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-whois",
    description="一个Nonebot2插件用于查询域名的whois信息",
    usage="/whois [域名] [-all]",
    type="application",
    homepage="https://github.com/Maizi-G/nonebot-plugin-whois",
    supported_adapters={"~onebot.v11"},
)


whois_search = on_command('whois', aliases={'whois查询'}, priority=5)

async def get_whois_info(domain: str) -> Optional[dict]:
    url = f"https://whois.4.cn/api/main?domain={domain}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            if response.status_code != 200:
                return None
            data = response.json()
            if data.get("retcode") != 0:
                return None
            return data.get("data")
    except Exception:
        return None

def parse_domain(input: str) -> Tuple[str, bool]:
    parts = input.split()
    if not parts:
        return "", False
    if parts[-1].lower() == "-all":
        return " ".join(parts[:-1]), True
    return " ".join(parts), False

def format_whois_result(data: dict) -> str:
    def get_field(field, default="暂无信息"):
        return data.get(field) or default

    domain_name = get_field("domain_name")
    registrars = get_field("registrars")
    expire_date = get_field("expire_date")
    create_date = get_field("create_date")
    update_date = get_field("update_date")

    status_list = data.get("status", [])
    status = "\n".join([f"• {s}" for s in status_list]) if status_list else "• 暂无状态信息"

    nameserver_list = data.get("nameserver", [])
    nameserver = "\n".join([f"• {ns}" for ns in nameserver_list]) if nameserver_list else "• 暂无DNS信息"

    owner_info = [
        f"├ 姓名：{get_field('owner_name')}",
        f"├ 机构：{get_field('owner_org')}",
        f"├ 邮箱：{get_field('owner_email')}",
        f"└ 电话：{get_field('owner_phone')}"
    ]
    # ✅ 先拼接好字符串
    owner_info_str = "\n".join(owner_info)

    # ✅ 在 f-string 里直接使用变量
    return f"""
🌐 域名信息：
├ 域名：{domain_name}
├ 注册商：{registrars}
├ 创建时间：{create_date}
├ 到期时间：{expire_date}
└ 更新时间：{update_date}

📄 状态信息：
{status}

🧭 DNS 服务器：
{nameserver}

👤 持有人信息：
{owner_info_str}
──────────────────────────────
💡 提示：添加 [-all] 参数查看完整信息
""".strip()


@whois_search.handle()
async def handle_whois_search(bot: Bot, event: Event, args: Message = CommandArg()):
    input_str = args.extract_plain_text().strip()
    if not input_str:
        await whois_search.finish("请输入要查询的域名，例如：/whois example.com")
    
    domain, show_all = parse_domain(input_str)
    if not domain:
        await whois_search.finish("域名不能为空！")
    
    data = await get_whois_info(domain)
    if not data:
        await whois_search.finish("Whois查询失败，请检查域名格式或稍后再试")
    
    if show_all:
        raw_data = data.get("meta_data", "暂无原始信息")
        await whois_search.finish(f"原始Whois信息：\n{raw_data}")
    else:
        result = format_whois_result(data)
        await whois_search.finish(result)