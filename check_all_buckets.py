# ============================================================
# FILE: check_all_buckets.py
# PURPOSE: AWS S3 pe jo bhi buckets hain unko check karo
#          aur saari buckets ki list print karo
# ============================================================

import boto3  # AWS S3 se connect karne ke liye

# ---------------------------------------------------------------
# FUNCTION: check_all_buckets
# WHAT IT DOES: AWS S3 account mein jo bhi buckets hain
#               unko dhundh ke print karta hai
# ---------------------------------------------------------------
def check_all_buckets():

    print("\n" + "="*50)
    print("   S3 PE SAARI BUCKETS CHECK HO RAHI HAIN")
    print("="*50 + "\n")

    # boto3 se S3 client banao
    # yeh AWS se connect karne ka tarika hai
    s3_client = boto3.client("s3")

    # S3 se saari buckets ki list lo
    # list_buckets() function AWS se saari buckets return karta hai
    response = s3_client.list_buckets()

    # response mein se sirf buckets wala part nikalo
    buckets = response.get("Buckets", [])

    # check karo koi bucket hai ya nahi
    if not buckets:
        print("[INFO] Koi bucket nahi mili S3 pe.")
        return

    # kitni buckets mili yeh print karo
    print(f"[INFO] Total {len(buckets)} bucket(s) mili hain:\n")
    print("-"*50)

    # har bucket ka naam aur date print karo
    for index, bucket in enumerate(buckets, start=1):

        # bucket ka naam nikalo
        bucket_name = bucket["Name"]

        # bucket kab bani yeh nikalo
        created_on = bucket["CreationDate"]

        # print karo
        print(f"  {index}. Name    : {bucket_name}")
        print(f"     Created : {created_on}\n")

    print("-"*50)
    print("[DONE] Saari buckets check ho gayi!")


# ----- ENTRY POINT -----
if __name__ == "__main__":
    check_all_buckets()