-- Create the messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    passcode VARCHAR(100) NOT NULL UNIQUE,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO messages (passcode, message) VALUES 
    ('hello123', 'Hello, world!'),
    ('test456', 'Welcome to the Flask application!'),
    ('admin789', 'Admin access granted - Hello, world!')
ON CONFLICT (passcode) DO NOTHING;

-- Create an index on passcode for faster lookups
CREATE INDEX IF NOT EXISTS idx_messages_passcode ON messages(passcode);
