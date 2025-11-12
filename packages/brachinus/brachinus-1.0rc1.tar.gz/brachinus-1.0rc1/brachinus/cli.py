import argparse
import os
from brachinus import AES256, encrypt_file_with_password, decrypt_file_with_password

def main():
    parser = argparse.ArgumentParser(
        description="Brachinus AES256 encryption and decryption CLI"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # -----------------------------
    # encrypt-file
    # -----------------------------
    encrypt_file_cmd = sub.add_parser("encfile", help="Encrypt a file")
    encrypt_file_cmd.add_argument("-t", help="Input file path")
    encrypt_file_cmd.add_argument("-p", "--password", help="Password to derive key")
    encrypt_file_cmd.add_argument("-k", "--keyfile", help="Path to binary key file")
    encrypt_file_cmd.add_argument("-o", "--output", help="Output encrypted file path")

    # -----------------------------
    # decrypt-file
    # -----------------------------
    decrypt_file_cmd = sub.add_parser("decfile", help="Decrypt a file")
    decrypt_file_cmd.add_argument("-t", help="Encrypted file path")
    decrypt_file_cmd.add_argument("-p", "--password", help="Password to derive key")
    decrypt_file_cmd.add_argument("-k", "--keyfile", help="Key file to load key from")
    decrypt_file_cmd.add_argument("-o", "--output", help="Output decrypted file path")

    # -----------------------------
    # encrypt-directory
    # -----------------------------
    encrypt_dir_cmd = sub.add_parser("encdir", help="Encrypt all files in a directory")
    encrypt_dir_cmd.add_argument("-t", help="Directory path")
    encrypt_dir_cmd.add_argument("-p", "--password", help="Password to derive key")
    encrypt_dir_cmd.add_argument("-k", "--keyfile", help="Key file to load key")
    encrypt_dir_cmd.add_argument("-o", "--output-dir", help="Output directory")

    # -----------------------------
    # decrypt-directory
    # -----------------------------
    decrypt_dir_cmd = sub.add_parser("decdir", help="Decrypt all .enc files in a directory")
    decrypt_dir_cmd.add_argument("-t", help="Directory path")
    decrypt_dir_cmd.add_argument("-p", "--password", help="Password to derive key")
    decrypt_dir_cmd.add_argument("-k", "--keyfile", help="Key file to load key")
    decrypt_dir_cmd.add_argument("-o", "--output-dir", help="Output directory")

    # -----------------------------
    # key-info
    # -----------------------------
    key_info_cmd = sub.add_parser("keyinfo", help="Display key information")
    key_info_cmd.add_argument("-p", "--password", help="Password to derive key")
    key_info_cmd.add_argument("-k", "--keyfile", help="Load key from file path")

    # -----------------------------
    # save-key
    # -----------------------------
    save_key_cmd = sub.add_parser("savekey", help="Save binary AES key to a file")
    save_key_cmd.add_argument("-k", "--keyfile", required=True, help="Output key file path")

    # -----------------------------
    # load-key
    # -----------------------------
    load_key_cmd = sub.add_parser("loadkey", help="Load key and print info")
    load_key_cmd.add_argument("keyfile", help="Path to key file to load")

    args = parser.parse_args()

    # ------------------------------------------
    # Create AES instance logic
    # ------------------------------------------
    def create_instance():
        if args.password:
            return AES256(password=args.password)
        elif args.keyfile:
            return AES256.load_from_keyfile(args.keyfile)
        else:
            raise ValueError("You must provide either --password or --keyfile")

    # --------------------------------------------------
    # Handle commands
    # --------------------------------------------------

    if args.command == "encfile":
        aes = create_instance()
        result = aes.encrypt_file(args.t, args.output)
        print("✅ File encrypted!")
        print("Input:", result["input_file"])
        print("Output:", result["output_file"])
        print("Salt:", result["salt"])
        print("IV:", result["iv"].hex())

    elif args.command == "decfile":
        aes = create_instance()
        output = aes.decrypt_file(args.t, args.output)
        print("✅ File decrypted!")
        print("Output:", output)

    elif args.command == "encdir":
        aes = create_instance()
        files = aes.encrypt_directory(args.t, args.output_dir)
        print("✅ Directory encrypted! Files:")
        for f in files:
            print(" -", f)

    elif args.command == "decdir":
        aes = create_instance()
        files = aes.decrypt_directory(args.t, args.output_dir)
        print("✅ Directory decrypted! Files:")
        for f in files:
            print(" -", f)

    elif args.command == "key-info":
        aes = create_instance()
        info = aes.get_key_info()
        print("🔑 Key info:")
        print("Key (hex):", info["key_hex"])
        print("Salt:", info["salt"])
        print("Salt hex:", info["salt_hex"])
        print("Type:", info["key_type"])

    elif args.command == "save-key":
        aes = AES256()  # random key
        aes.save_key(args.keyfile)
        print("✅ Key saved!")
        print("Key file:", args.keyfile)

    elif args.command == "load-key":
        aes = AES256.load_from_keyfile(args.keyfile)
        info = aes.get_key_info()
        print("✅ Key loaded!")
        print("Key hex:", info["key_hex"])

    else:
        parser.print_help()
