import discord 
from Import_file import *

        

class ShowBlacklist():

    def _show_blacklist_economy(guild_id):

        blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, table="economy")

        if blacklist:

            all_channels, all_categories, all_roles, all_users = [], [], [], []
            for _, _, blacklist_channel, blacklist_category, blacklist_role, blacklist_user in blacklist:

                None if None == blacklist_channel else all_channels.append(f"{Emojis.dot_emoji} <#{blacklist_channel}>\n")

                None if None == blacklist_category else all_categories.append(f"{Emojis.dot_emoji} <#{blacklist_category}>\n")

                None if None == blacklist_role else all_roles.append(f"{Emojis.dot_emoji} <@&{blacklist_role}>\n")

                None if None == blacklist_user else all_users.append(f"{Emojis.dot_emoji} <@{blacklist_user}>\n")
                
            if all_channels == []:
                channels_mention = f"{Emojis.dot_emoji} Es gibt keine channels auf der Blacklist"
            else:
                channels_mention = "".join(all_channels)
                
            if all_categories == []:
                categories_mention = f"{Emojis.dot_emoji} Es gibt keine categories auf der Blacklist"
            else:
                categories_mention = "".join(all_categories)
                
            if all_roles == []:
                roles_mention = f"{Emojis.dot_emoji} Es gibt keine roles auf der Blacklist"
            else:
                roles_mention = "".join(all_roles)
                
            if all_users == []:
                users_mention = f"{Emojis.dot_emoji} Es gibt keine users auf der Blacklist"
            else:
                users_mention = "".join(all_users)
        
        else:

            channels_mention = f"{Emojis.dot_emoji} Es gibt keine channels auf der Blacklist"
            categories_mention = f"{Emojis.dot_emoji} Es gibt keine categories auf der Blacklist"
            roles_mention = f"{Emojis.dot_emoji} Es gibt keine roles auf der Blacklist"
            users_mention = f"{Emojis.dot_emoji} Es gibt keine users auf der Blacklist"

        return [channels_mention, categories_mention, roles_mention, users_mention]

