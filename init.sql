-- Enable the UUID extension if it doesn't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the users table
CREATE TABLE users (
    userid   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mobile   VARCHAR(15) UNIQUE NOT NULL,
    username VARCHAR(50),
    password VARCHAR(128) NOT NULL,
    salt     VARCHAR(64) NOT NULL,
    subscription_tier VARCHAR(20) NOT NULL DEFAULT 'basic',
    stripe_customer_id VARCHAR(128) UNIQUE
);

-- Create the chatrooms table
CREATE TABLE chatrooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(100) NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    user_id UUID NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES users(userid)
        ON DELETE CASCADE
);

-- Create the messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL, -- 'user' or 'ai'
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    chatroom_id UUID NOT NULL,
    CONSTRAINT fk_chatroom
        FOREIGN KEY(chatroom_id) 
        REFERENCES chatrooms(id)
        ON DELETE CASCADE
);

-- Optional: Add an index for faster lookups
CREATE INDEX idx_chatrooms_user_id ON chatrooms(user_id);
CREATE INDEX idx_messages_chatroom_id ON messages(chatroom_id);
