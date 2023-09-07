

CREATE DATABASE IF NOT EXISTS `DiscordBot` ;

USE DiscordBot;


------------  Tables for the Level System -------------

DROP TABLE IF EXISTS `LevelSystemStats`;

CREATE TABLE `LevelSystemStats` (
    guildId BIGINT UNSIGNED NOT NULL, 
    userId BIGINT UNSIGNED NOT NULL,
    userLevel BIGINT UNSIGNED NOT NULL,
    userXp BIGINT UNSIGNED NOT NULL,
    userName VARCHAR(255) NOT NULL,
	voiceTime TIMESTAMP(6) NULL,
    wholeXp BIGINT UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LevelSystemBlacklist`;

CREATE TABLE LevelSystemBlacklist (
    guildId BIGINT UNSIGNED NOT NULL,
    channelId BIGINT UNSIGNED NULL,
    categoryId BIGINT UNSIGNED NULL,
    roleId BIGINT UNSIGNED NULL,
    userId BIGINT UNSIGNED NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LevelSystemRoles`;

CREATE TABLE LevelSystemRoles (
    guildId BIGINT UNSIGNED NOT NULL,
    roleId BIGINT UNSIGNED NOT NULL,
    roleLevel INT UNSIGNED NOT NULL,
    guildName VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LevelSystemSettings`;

CREATE TABLE LevelSystemSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    xpRate INT UNSIGNED DEFAULT 20,
    levelStatus VARCHAR(50) DEFAULT 'on',
    levelUpChannel BIGINT UNSIGNED NULL,
    levelUpMessage VARCHAR(500) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}'
    bonusXpPercentage INT UNSIGNED DEFAULT 10
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LevelRankCardSettingsGuild`;

CREATE TABLE LevelRankCardSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    cardColor VARCHAR(20) DEFAULT '8, 120, 151',
    cardImage BLOB NULL,
    cardLayout INT UNSIGNED DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `BonusXpList`;

CREATE TABLE BonusXpList (
    guildId BIGINT UNSIGNED NOT NULL,
    channelId BIGINT UNSIGNED NULL,
    categoryId BIGINT UNSIGNED NULL,
    roleId BIGINT UNSIGNED NULL,
    userId BIGINT UNSIGNED NULL,
    PercentBonusXp INT UNSIGNED DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `ManageBlacklistTemp`;

CREATE TABLE ManageBlacklistTemp (
    guildId BIGINT UNSIGNED NOT NULL,
    channelId VARCHAR(500) NULL,
    categoryId VARCHAR(500) NULL,
    roleId VARCHAR(500) NULL,
    userId VARCHAR(500) NULL,
    operation VARCHAR(100) NOT NULL,
    systemStatus VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


------------- Table for the Marry system --------------

DROP TABLE IF EXISTS `MarryStats`;

CREATE TABLE MarryStats (
    guildId BIGINT UNSIGNED NOT NULL,
    userOneId BIGINT UNSIGNED NOT NULL,
    userOneName VARCHAR(255) NOT NULL,
    userTwoId BIGINT UNSIGNED NOT NULL,
    userTwoName VARCHAR(255) NOT NULL,
    WeddingDate DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


------------- Table for the Bot settigs -----------------

DROP TABLE IF EXISTS `BotSettings`;

CREATE TABLE BotSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    prefix VARCHAR(20) DEFAULT '?',
    botColour VARCHAR(20) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-------------- Table for the Autoreaction ---------------

DROP TABLE IF EXISTS `AutoReactionSetup`;

CREATE TABLE AutoReactionSetup (
    guildId BIGINT UNSIGNED NOT NULL, 
    channelId BIGINT UNSIGNED NOT NULL,
    categoryId BIGINT UNSIGNED NOT NULL,
    emojiOne VARCHAR(255) NULL,
    emojiTwo VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `AutoReactionSettings`;

CREATE TABLE AutoReactionSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    teServerReaction INT NULL,
    reactionParameter VARCHAR(255) NULL,
    mainReactionEmoji VARCHAR(255) NOT NULL,
    reactionKeyWords VARCHAR(4000) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


--------------- Table for Econemy System ------------

DROP TABLE IF EXISTS `EconomySystemStats`;

CREATE TABLE EconomySystemStats (
    guildId BIGINT UNSIGNED NOT NULL,
    userId BIGINT UNSIGNED NOT NULL,
    moneyCount BIGINT UNSIGNED DEFAULT 0,
    userName VARCHAR(255) NOT NULL,
    voiceTime TIMESTAMP(6) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `EconomySystemBlacklist`;

CREATE TABLE EconomySystemBlacklist (
    guildId BIGINT UNSIGNED NOT NULL,
    guildName VARCHAR(255) NOT NULL,
    channelId BIGINT UNSIGNED NULL,
    categoryId BIGINT UNSIGNED NULL,
    roleId BIGINT UNSIGNED NULL,
    userId BIGINT UNSIGNED NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `EconomySystemShop`;

CREATE TABLE EconomySystemShopRolles (
    guildId BIGINT UNSIGNED NOT NULL,
    guildName VARCHAR(255) NOT NULL,
    rolesId BIGINT UNSIGNED NULL,
    itemPrice INT UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `EconomySystemSettings`;

CREATE TABLE EconomySystemSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    econemyStatus VARCHAR(50) DEFAULT 'on_all'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




