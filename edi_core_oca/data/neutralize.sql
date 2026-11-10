-- Copied/neutralized databases must not talk to live partners.
UPDATE edi_backend SET test_mode = true;
