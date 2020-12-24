import argparse
import codecs
import glob
import shutil
import typing as t

REDACTNAME = "REDACTED"
REDACTEMAILNAME = "redacted"
REDACTEMAILEXT = "email"
REDACTEMAILTLD = "tld"


def to_bytes(data: str) -> bytes:
    return data.encode()


def to_hex(data: t.Union[str, bytes]) -> str:
    if isinstance(data, str):
        data = to_bytes(data)
    return codecs.encode(data, "hex").decode()


def redact_data(username, email, real_name, file_path):
    fp = open(file_path, "rb")
    hexfile = fp.read().hex()
    fp.close()
    mail_length = len(email) - 2
    if mail_length < 4:
        print("Invalid mail received, length is way too low")
        return
    if mail_length < 5:
        redacted_mail = REDACTEMAILNAME[0] + "@" + REDACTEMAILEXT[0] + "." + REDACTEMAILTLD[0:1]
    elif mail_length < 6:
        redacted_mail = REDACTEMAILNAME[0] + "@" + REDACTEMAILEXT[0] + "." + REDACTEMAILTLD
    else:
        ext_length = mail_length - 3
        if ext_length > 5:
            ext_length = 5
        name_length = mail_length - ext_length - 3
        if name_length < 1:
            ext_length -= 1
            name_length = 1
        redacted_mail = ""
        if (name_length + ext_length + 5) > len(
            REDACTEMAILNAME + "@" + REDACTEMAILEXT + "." + REDACTEMAILEXT
        ):
            redacted_mail = to_bytes(REDACTEMAILNAME) + to_bytes("@" + REDACTEMAILEXT + "." + REDACTEMAILTLD)
            extra = b"\x00" * (len(email) - len(redacted_mail))
            redacted_mail += extra
        else:
            redacted_mail = (
                REDACTEMAILNAME[0 : name_length - 1] + "@" + REDACTEMAILEXT[0:ext_length] + REDACTEMAILTLD
            )
    redacted_mail = to_hex(redacted_mail)
    if len(username) > len(REDACTNAME):
        extra = b"\x00" * (len(username) - len(REDACTNAME))
        redacted_uname = to_bytes(REDACTNAME) + extra
    else:
        redacted_uname = to_bytes(REDACTNAME[0 : len(username) - 1])
    redacted_uname = to_hex(redacted_uname)
    if len(real_name) > len(REDACTNAME):
        extra = b"\x00" * (len(real_name) - len(REDACTNAME))
        redacted_name = to_bytes(REDACTNAME) + extra
    else:
        redacted_name = to_bytes(REDACTNAME[0 : len(real_name) - 1])
    redacted_name = to_hex(redacted_name)

    original_name = to_hex(real_name)
    original_uname = to_hex(username)
    original_email = to_hex(email)

    # Replace name, username, email
    hexfile = hexfile.replace(original_name, redacted_name)
    hexfile = hexfile.replace(original_email, redacted_mail)
    hexfile = hexfile.replace(original_uname, redacted_uname)

    # Replace Transaction ID
    transaction_id_path = "61 76 65 72 01 01 01 00 74 72 61 6E".replace(" ", "").lower()
    transaction_start = hexfile.find(transaction_id_path)
    tr_max_path = len(transaction_id_path) + transaction_start + (2 * 4)
    hexfile = hexfile[: transaction_start + len(transaction_id_path)] + ("ff" * 4) + hexfile[tr_max_path:]

    # Replace User ID
    user_id_path = "73 63 68 69 00 00 00 0C 75 73 65 72".replace(" ", "").lower()
    user_id_start = hexfile.find(user_id_path)
    user_max_path = len(user_id_path) + user_id_start + (2 * 4)
    hexfile = hexfile[: user_id_start + len(user_id_path)] + ("ff" * 4) + hexfile[user_max_path:]

    # Replace Item ID
    item_id_path = "73 69 6E 67 00 00 00 00 73 6F 6E 67".replace(" ", "").lower()
    item_id_start = hexfile.find(item_id_path)
    item_max_path = len(item_id_path) + item_id_start + (2 * 4)
    hexfile = hexfile[: item_id_start + len(item_id_path)] + ("ff" * 4) + hexfile[item_max_path:]

    # Replace Country Purchase Location
    country_path = "73 66 49 44 00 00 00 14 64 61 74 61".replace(" ", "").lower()
    country_start = hexfile.find(country_path)
    country_real_start = len(country_path) + country_start + (2 * 8)
    hexfile = hexfile[:country_real_start] + ("00" * 4) + hexfile[country_real_start + (2 * 4) :]

    # Replace Purchase Date
    redacted_purchase_date = to_hex("1970-01-01 00:00:00")
    purchase_date_path = "2B 70 75 72 64 00 00 00 23 64 61 74 61 00 00 00 01 00 00 00 00".replace(
        " ", ""
    ).lower()
    purchase_date_start = hexfile.find(purchase_date_path)
    purchase_date_max = len(purchase_date_path) + purchase_date_start + len(redacted_purchase_date)
    hexfile = (
        hexfile[: purchase_date_start + len(purchase_date_path)]
        + redacted_purchase_date
        + hexfile[purchase_date_max:]
    )

    redacted_bytes = codecs.decode(to_bytes(hexfile), "hex")
    with open(file_path, "wb") as fp:
        fp.write(redacted_bytes)


parser = argparse.ArgumentParser()
parser.add_argument("username", help="Your iTunes Username")
parser.add_argument("-e", "--email", dest="mail", required=True, help="Your iTunes Email")
parser.add_argument("-n", "--name", dest="name", required=True, help="Your iTunes Real Name")
args = parser.parse_args()

all_m4a_files = glob.glob("*.m4a")
print("Old data:", args.username, args.mail, args.name)
for m4a_file in all_m4a_files:
    # Create backup
    try:
        shutil.copy(m4a_file, m4a_file + ".original")
    except Exception:
        pass
    print(f">> Redacting: {m4a_file}")
    redact_data(args.username, args.mail, args.name, m4a_file)
