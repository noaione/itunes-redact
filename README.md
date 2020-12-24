# iTunes Music Personal Info Stripper
This is mostly the same as [un-istore](https://github.com/avibrazil/un-istore) but in Python.

This program will try to redact or remove any offending/private information from your `.m4a` files.

Ensuring your information will be privated before you share it.

## What will be redacted?
Most of the personal info including:
- User ID
- Transaction ID
- Item ID (Might not be important)
- ownr Tag (Include your username)
- Real name used in the Apple Account
- Email used to purchase
- Country purchasing location
- Purchasing date

## What it will be changed to?
- User ID, Transaction ID, Item ID: `0xffffffff`
- Real Name, Username: `REDACTED` with extra `\x00` padding if needed.
- Email: `redacted@email.tld` with extra `\x00` padding if needed.
- Purchasing date: `1970-01-01 00:00:00`
- Country: hex bytes will be changed to `00 00 00 00`

## Requirements
- Python 3.6+

## Running
Put every `.m4a` files you want to redact/remove the personal information in the same folder as `redact.py`

Then run:<br>
`python3 redact.py -n "REAL NAME USED" -e "emailused@mailservice.tld" "USERNAME USED"` or `python redact.py "REAL NAME USED" -e "emailused@mailservice.tld" "USERNAME USED"`

For example, if your username is `JohnSmith` and your real name used in the Apple account is `John Smith` with email `johnsmith@gmail.com`:<br>
```bash
python3 redact.py -n "John Smith" -e "johnsmith@gmail.com" "JohnSmith"
```

or

```bash
python redact.py -n "John Smith" -e "johnsmith@gmail.com" "JohnSmith"
```

This will recursively check for `.m4a` files in the folder then remove the offending personal information.

This will also create an original `.m4a` files just in case it failed.

## License
This project is licensed with MIT License
