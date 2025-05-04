import discord.utils
from discord import Color, Embed

def ModuleNotFound():
    embed = Embed(
        title="Module Not Found",
        description=f"The module was not found.",
        color=Color.brand_red(),
        timestamp=discord.utils.utcnow()
    ).add_field(
        name="Trouble Shooting",
        value=f"> **1.** Run ``/config``\n> **2.** Find the module in the dropdown\n> **3.** Configure the module\n> **4.** On the dropdown, go to Modules\n> **5.** In the Enabled dropdown, find the Module and make sure it is selected.",
        inline=True
    )

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}

def MissingPermissions():
    embed = discord.Embed(
        title="Missing Permissions",
        description=f"> You are missing the required permissions to run this command.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow())

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}


def ModuleDisabled():
    embed = discord.Embed(
        title="Module Disabled",
        description=f"The module is disabled.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow()
    ).add_field(
        name="Trouble Shooting",
        value=f"> **1.** Run ``/config``\n> **2.** Select Modules\n> **3.** Click the enabled dropdown\n> **4.** Find the module and enable it",
        inline=True
    )

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}

def MissingConfigChannel():
    embed = discord.Embed(
        title="Channel Missing",
        description=f"Please setup the channel for the module.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow()
    ).add_field(
        name="Trouble Shooting",
        value=f"> **1.** Run ``/config``\n> **2.** Select the Module\n> **3.** Find the channel dropdown\n> **4.** Select the channel",
        inline=True
    )

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))

    return {"embed": embed, "view": view}

def ChannelNotFound():
    embed = discord.Embed(
        title="Channel Not Found",
        description=f"I can't find the channel for this command.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow())

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}


def ChannelSendFailure():
    embed = discord.Embed(
        title="Failed to Send",
        description=f"I can't send messages to the channel, please ensure I have the necessary permissions.",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow())

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}

def PermissionError():
    embed = discord.Embed(
        title="Permission Error",
        description=f"Im not able to execute this command (discord permission issue).",
        color=discord.Color.brand_red(),
        timestamp=discord.utils.utcnow())

    view = discord.ui.View(timeout=None)
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Support", url="https://discord.gg/mmVYkZRG8h"))
    view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.url, label="Docs", url="https://docs.atlasmgmt.xyz"))
    return {"embed": embed, "view": view}