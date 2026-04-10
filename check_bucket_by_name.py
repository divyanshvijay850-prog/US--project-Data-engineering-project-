# ============================================================
# FILE: check_bucket_by_name.py
# PURPOSE: Ek function jo bucket ka naam leke check kare
#          ki woh bucket S3 pe exist karti hai ya nahi
# ============================================================

import boto3  # AWS S3 se connect karne ke liye
from botocore.exceptions import ClientError  # AWS errors handle karne ke liye

# ---------------------------------------------------------------
# FUNCTION: check_bucket_by_name
# WHAT IT DOES: Bucket ka naam parameter mein leta hai
#               aur check karta hai ki woh S3 pe hai ya nahi
# PARAMETER: bucket_name (str) - jis bucket ko check karna hai
# RETURNS: True agar bucket hai, False agar nahi hai
# ---------------------------------------------------------------
def check_bucket_by_name(bucket_name):

    # check karo bucket ka naam empty toh nahi
    if not bucket_name:
        print("[ERROR] Bucket ka naam empty hai!")
        return False

    print(f"\n[INFO] '{bucket_name}' bucket check ho rahi hai...")

    # boto3 se S3 client banao
    s3_client = boto3.client("s3")

    try:
        # head_bucket() se check karo bucket exist karti hai ya nahi
        # yeh ek lightweight call hai - koi data download nahi hota
        s3_client.head_bucket(Bucket=bucket_name)

        # agar koi error nahi aaya matlab bucket exist karti hai
        print(f"[FOUND] '{bucket_name}' bucket S3 pe exist karti hai!")
        return True  # bucket mili

    except ClientError as error:

        # AWS ka error code nikalo
        error_code = int(error.response["Error"]["Code"])

        if error_code == 404:
            # 404 matlab bucket exist nahi karti
            print(f"[NOT FOUND] '{bucket_name}' bucket S3 pe nahi hai! (404)")

        elif error_code == 403:
            # 403 matlab bucket hai par access nahi hai
            print(f"[NO ACCESS] '{bucket_name}' bucket hai par access nahi! (403)")

        else:
            # koi aur error
            print(f"[ERROR] Kuch aur problem aayi: {error}")

        return False  # bucket nahi mili


# ----- ENTRY POINT -----
if __name__ == "__main__":

    # yahan apna bucket naam daalo test karne ke liye
    bucket = "New-airport-bucket"
    result = check_bucket_by_name(bucket)
    print(f"\n[RESULT] Bucket exist karti hai? → {result}")