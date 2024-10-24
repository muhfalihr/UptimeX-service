#!/bin/sh

USER=$(whoami)

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo privileges."
    exit 1
fi

CURRENT_PATH=$(pwd)
# echo "export CHECKER_PATH=\"$CURRENT_PATH\"" >> ~/.zshrc
# exec zsh

echo "Installing SQLite..."
apt-get update -y && apt-get install sqlite3 -y

if command -v sqlite3 >/dev/null 2>&1; then
    echo "SQLite has been successfully installed!"
else
    echo "Failed to install SQLite. Exiting..."
    exit 1
fi

DB_NAME="$CURRENT_PATH/checker.db"
echo "Creating a new SQLite database: $DB_NAME"
sqlite3 $DB_NAME <<EOF
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS server_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL DEFAULT 'root',  
    ip_address VARCHAR(45) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    python_interpreter VARCHAR(255),
    path_file_execution VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE server_status (
    id TEXT PRIMARY KEY DEFAULT (substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1) || 
        substr('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', abs(random()) % 62 + 1, 1)),
    ip_address TEXT NOT NULL,
    label VARCHAR(100),
    status TEXT NOT NULL CHECK (status IN ('active', 'timeout', 'unaccessible')),
    message TEXT
);

CREATE TABLE IF NOT EXISTS versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF
chown $USER:$USER $DB_NAME

echo "Tables 'servers', 'authservers', and 'versions' have been successfully created in $DB_NAME."

echo "Displaying the list of tables in the database:"
sqlite3 $DB_NAME ".tables"