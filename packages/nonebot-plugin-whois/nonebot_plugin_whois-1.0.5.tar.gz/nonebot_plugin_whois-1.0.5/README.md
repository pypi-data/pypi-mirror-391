
<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# nonebot-plugin-whois

_✨ 一个Nonebot2插件用于查询域名的whois信息✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-whois.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-whois">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-whois.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>



</details>

## 📖 介绍

一个Nonebot2插件用于查询域名的whois信息

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-whois

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-whois
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-whois
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-whois
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-whois
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_whois"]

</details>

## ⚙️ 配置

本插件无需配置


## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| whois example.com | 群员 | 是 | 全局 | 查询whois |
| whois example.com -all | 群员 | 是 | 全局 | 查询原始whois |
