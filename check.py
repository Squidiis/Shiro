import discord 
from Import_file import *


def check_exists(guild_id:int, user_id:int = None, channel_id:int = None, category_id:int = None, role_id:int = None):

    guild = bot.get_guild(guild_id)

    if user_id != None:

        if guild.get_member(user_id) is not None:

            return True
        
        else:

            return False
        
    if channel_id != None:

        if guild.get_channel(channel_id) is not None:

            return True
        
        else:

            return False
        
    if role_id != None:

        if guild.get_role(role_id) is not None:

            return True
        
        else:

            return False
        

class ShowBlacklist():

    def _show_blacklist_economy(guild_id):

        blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, table="economy")

        if blacklist:

            all_channels, all_categories, all_roles, all_users = [], [], [], []
            for _, _, blacklist_channel, blacklist_category, blacklist_role, blacklist_user in blacklist:

                None if None == blacklist_channel else all_channels.append(f"{dot_emoji} <#{blacklist_channel}>\n")

                None if None == blacklist_category else all_categories.append(f"{dot_emoji} <#{blacklist_category}>\n")

                None if None == blacklist_role else all_roles.append(f"{dot_emoji} <@&{blacklist_role}>\n")

                None if None == blacklist_user else all_users.append(f"{dot_emoji} <@{blacklist_user}>\n")
                
            if all_channels == []:
                channels_mention = f"{dot_emoji} Es gibt keine channels auf der Blacklist"
            else:
                channels_mention = "".join(all_channels)
                
            if all_categories == []:
                categories_mention = f"{dot_emoji} Es gibt keine categories auf der Blacklist"
            else:
                categories_mention = "".join(all_categories)
                
            if all_roles == []:
                roles_mention = f"{dot_emoji} Es gibt keine roles auf der Blacklist"
            else:
                roles_mention = "".join(all_roles)
                
            if all_users == []:
                users_mention = f"{dot_emoji} Es gibt keine users auf der Blacklist"
            else:
                users_mention = "".join(all_users)
        
        else:

            channels_mention = f"{dot_emoji} Es gibt keine channels auf der Blacklist"
            categories_mention = f"{dot_emoji} Es gibt keine categories auf der Blacklist"
            roles_mention = f"{dot_emoji} Es gibt keine roles auf der Blacklist"
            users_mention = f"{dot_emoji} Es gibt keine users auf der Blacklist"

        return [channels_mention, categories_mention, roles_mention, users_mention]
    

    def _show_blacklist_level(guild_id):

        blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, table="level")
        print(blacklist)
        if blacklist:

            all_channels, all_categories, all_roles, all_users = [], [], [], []
            for _, _, blacklist_channel, blacklist_category, blacklist_role, blacklist_user in blacklist:

                None if None == blacklist_channel else all_channels.append(f"{dot_emoji} <#{blacklist_channel}>\n")

                None if None == blacklist_category else all_categories.append(f"{dot_emoji} <#{blacklist_category}>\n")

                None if None == blacklist_role else all_roles.append(f"{dot_emoji} <@&{blacklist_role}>\n")

                None if None == blacklist_user else all_users.append(f"{dot_emoji} <@{blacklist_user}>\n")
                
            if all_channels == []:
                channels_mention = f"{dot_emoji} Es gibt keine channels auf der Blacklist"
            else:
                channels_mention = "".join(all_channels)
                
            if all_categories == []:
                categories_mention = f"{dot_emoji} Es gibt keine categories auf der Blacklist"
            else:
                categories_mention = "".join(all_categories)
                
            if all_roles == []:
                roles_mention = f"{dot_emoji} Es gibt keine roles auf der Blacklist"
            else:
                roles_mention = "".join(all_roles)
                
            if all_users == []:
                users_mention = f"{dot_emoji} Es gibt keine users auf der Blacklist"
            else:
                users_mention = "".join(all_users)
        
        else:

            channels_mention = f"{dot_emoji} Es gibt keine channels auf der Blacklist"
            categories_mention = f"{dot_emoji} Es gibt keine categories auf der Blacklist"
            roles_mention = f"{dot_emoji} Es gibt keine roles auf der Blacklist"
            users_mention = f"{dot_emoji} Es gibt keine users auf der Blacklist"

        return [channels_mention, categories_mention, roles_mention, users_mention]

async def check_status_level(ctx):

    status = DatabaseCheck.check_bot_settings(guild=ctx.guild.id)

    if "on" == status[2] or "on_text" == status == status[2]:
        return True

    else:
        return False