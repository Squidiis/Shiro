

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
    roleLevel INT UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LevelSystemSettings`;

CREATE TABLE LevelSystemSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    xpRate INT UNSIGNED DEFAULT 20,
    levelStatus VARCHAR(50) DEFAULT 'on',
    levelUpChannel BIGINT UNSIGNED NULL,
    levelUpMessage VARCHAR(500) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}',
    bonusXpPercentage INT UNSIGNED DEFAULT 10
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


DROP TABLE IF EXISTS `AntiLinkWhiteList`;

CREATE TABLE AntiLinkWhiteList (
    guildId BIGINT UNSIGNED NOT NULL,
    channelId BIGINT UNSIGNED NULL,
    categoryId BIGINT UNSIGNED NULL,
    roleId BIGINT UNSIGNED NULL,
    userId BIGINT UNSIGNED NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


---------------- leaderboard Settings ---------------------

DROP TABLE IF EXISTS `LeaderboardSettingsMessage`

CREATE TABLE LeaderboardSettingsMessage (
    guildId BIGINT UNSIGNED NOT NULL,
    statusMessage INT UNSIGNED NOT NULL DEFAULT 0,
    bourdMessageIdDay BIGINT UNSIGNED NULL,
    bourdMessageIdWeek BIGINT UNSIGNED NULL,
    bourdMessageIdMonth  BIGINT UNSIGNED NULL,
    bourdMessageIdWhole BIGINT UNSIGNED NULL,
    leaderboardChannel BIGINT UNSIGNED NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LeaderboardSettingsInvite`

CREATE TABLE LeaderboardSettingsInvite (
    guildId BIGINT UNSIGNED NOT NULL,
    statusInvite INT UNSIGNED NOT NULL DEFAULT 0,
    invitebourdMessageIdWeek BIGINT UNSIGNED NULL,
    invitebourdMessageIdMonth BIGINT UNSIGNED NULL,
    invitebourdMessageIdQuarter BIGINT UNSIGNED NULL,
    invitebourdMessageIdWhole BIGINT UNSIGNED NULL,
    leaderboardChannel BIGINT UNSIGNED NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LeaderboardTacking`;

CREATE TABLE LeaderboardTacking (
    guildId BIGINT UNSIGNED NOT NULL,
    userId BIGINT UNSIGNED NOT NULL,
    dailyCountMessage INT UNSIGNED DEFAULT 0,
    weeklyCountMessage INT UNSIGNED DEFAULT 0,
    monthlyCountMessage INT UNSIGNED DEFAULT 0,
    wholeCountMessage INT UNSIGNED DEFAULT 0,
    weeklyCountInvite INT UNSIGNED DEFAULT 0,
    monthlyCountInvite INT UNSIGNED DEFAULT 0,
    quarterlyCountInvite INT UNSIGNED DEFAULT 0,
    wholeCountInvite INT UNSIGNED DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LeaderboardRoles`;

CREATE TABLE LeaderboardRoles (
    guildId BIGINT UNSIGNED NOT NULL,
    roleId BIGINT UNSIGNED NOT NULL,
    rankingPosition INT UNSIGNED NOT NULL,
    status VARCHAR(20) NOT NULL,
    roleInterval VARCHAR(10) NOT NUll
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LeaderboardGivenRoles`;

CREATE TABLE LeaderboardGivenRoles (
    guildId BIGINT UNSIGNED NOT NULL,
    roleId BIGINT UNSIGNED NOT NULL,
    userId BIGINT UNSIGNED NOT NULL,
    roleInterval VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `LeaderboardInviteTracking`;

CREATE TABLE LeaderboardInviteTracking (
    guildId BIGINT UNSIGNED NOT NULL,
    userId BIGINT UNSIGNED NOT NULL,
    inviteCode VARCHAR(20) NOT NULL,
    usesCount INT NOT NULL,
    UNIQUE KEY unique_invite (guildId, inviteCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


------------- Table for the Bot settigs -----------------

DROP TABLE IF EXISTS `BotSettings`;

CREATE TABLE BotSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    botColour VARCHAR(20) NULL,
    ghostPing BIT DEFAULT 0,
    antiLink BIT(4) DEFAULT 3,
    antiLinkTimeout INT DEFAULT 0,
    autoReaction BIT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-------------- Table for the Autoreaction ---------------

DROP TABLE IF EXISTS `AutoReactions`;

CREATE TABLE AutoReactionSettings (
    guildId BIGINT UNSIGNED NOT NULL,
    channelId BIGINT UNSIGNED NULL,
    categoryId BIGINT UNSIGNED NULL,
    parameter VARCHAR(255) NOT NULL,
    emoji VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


