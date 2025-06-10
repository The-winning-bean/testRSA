import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def extract_rsa_parameters(pem_file):
    with open(pem_file, "rb") as f:
        pem_data = f.read()

    public_key = serialization.load_pem_public_key(pem_data, backend=default_backend())
    numbers = public_key.public_numbers()
    n = numbers.n
    e = numbers.e

    print(f"e (decimal): {e}")
    print(f"e (hex):     {hex(e)}\n")

    print(f"n (decimal): {n}")
    print(f"n (hex):     {hex(n)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract RSA public key parameters from PEM file")
    parser.add_argument("-f", "--file", required=True, help="Path to the PEM public key file")
    args = parser.parse_args()

    extract_rsa_parameters(args.file)
