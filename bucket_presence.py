# ============================================================
# FILE: bucket_presence.py
# PURPOSE: Check karo bucket hai ya nahi aur clearly
#          PRESENT ya NOT PRESENT print karo
# ============================================================

import boto3  # AWS S3 se connect karne ke liye
from botocore.exceptions import ClientError  # AWS errors ke liye

# ---------------------------------------------------------------
# FUNCTION: bucket_presence
# WHAT IT DOES: Bucket ka naam leke check karta hai
#               aur clearly PRESENT ya NOT PRESENT print karta hai
# PARAMETER: bucket_name (str) - jis bucket ko check karna hai
# RETURNS: "PRESENT" ya "NOT PRESENT" string
# ---------------------------------------------------------------
def bucket_presence(bucket_name):

    # boto3 se S3 client banao
    s3_client = boto3.client("s3")

    try:
        # head_bucket() se bucket check karo
        s3_client.head_bucket(Bucket=bucket_name)

        # koi error nahi aaya matlab bucket hai
        print(f"  Bucket : {bucket_name}")
        print(f"  Status : ✅ PRESENT")
        print("-"*40)
        return "PRESENT"

    except ClientError as error:

        # error code nikalo
        error_code = int(error.response["Error"]["Code"])

        print(f"  Bucket : {bucket_name}")

        if error_code == 404:
            # bucket exist nahi karti
            print(f"  Status : ❌ NOT PRESENT")

        elif error_code == 403:
            # bucket hai par access nahi
            print(f"  Status : ❌ NOT PRESENT (Access Denied)")

        print("-"*40)
        return "NOT PRESENT"


# ---------------------------------------------------------------
# FUNCTION: check_multiple_buckets
# WHAT IT DOES: Buckets ki list leke ek ek check karta hai
#               aur PRESENT ya NOT PRESENT print karta hai
# PARAMETER: bucket_list (list) - saari buckets ke naam
# ---------------------------------------------------------------
def check_multiple_buckets(bucket_list):

    print("\n" + "="*40)
    print("   BUCKET PRESENCE CHECKER")
    print("="*40 + "\n")

    # results store karne ke liye dictionary
    results = {}

    # har bucket check karo
    for bucket_name in bucket_list:
        status = bucket_presence(bucket_name)
        results[bucket_name] = status  # result save karo

    # summary print karo
    print("\n📋 SUMMARY:")
    print("="*40)
    for name, status in results.items():
        print(f"  {name:<30} → {status}")
    print("="*40)

    return results


# ----- ENTRY POINT -----
if __name__ == "__main__":

    # test karne ke liye buckets ki list
    buckets_to_check = [
        "New-airport-bucket",
        "fake-bucket-xyz-123",
        "another-fake-bucket",
    ]

    check_multiple_buckets(buckets_to_check)