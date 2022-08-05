CREATE TABLE IF NOT EXISTS pairs (
    ID TEXT PRIMARY KEY NOT NULL,
    hugs INT DEFAULT 0,
    kills INT DEFAULT 0,
    kisses INT DEFAULT 0,
    slaps INT DEFAULT 0,
    bites INT DEFAULT 0,
    pats INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS economy (
    ID TEXT PRIMARY KEY NOT NULL,
    gold INT DEFAULT 0,
    dayclaim INT DEFAULT 0,
    streak INT DEFAULT 0,
    maxbal INT DEFAULT 0,
    interest FLOAT DEFAULT 1,
    bankbal INT DEFAULT 0
);