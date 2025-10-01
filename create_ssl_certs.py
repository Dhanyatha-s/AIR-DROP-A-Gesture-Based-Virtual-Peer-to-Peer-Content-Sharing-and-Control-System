# ===============================
# create_ssl_certs.py - SSL CERTIFICATE GENERATOR
# ===============================

import os
import subprocess
import sys
from pathlib import Path

def create_ssl_certificates():
    """Create self-signed SSL certificates for secure communication"""
    
    cert_file = "cert.pem"
    key_file = "key.pem"
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✅ SSL certificates already exist")
        return True
    
    print("🔐 Creating SSL certificates...")
    
    try:
        # Try using OpenSSL command line
        cmd = [
            "openssl", "req", "-new", "-x509", "-days", "365", "-nodes",
            "-out", cert_file,
            "-keyout", key_file,
            "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SSL certificates created successfully")
            return True
        else:
            print(f"❌ OpenSSL command failed: {result.stderr}")
            
    except FileNotFoundError:
        print("❌ OpenSSL not found in system PATH")
    
    # Fallback: Create using Python cryptography library
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        print("🔐 Creating certificates using Python cryptography...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AirDrop P2P"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ SSL certificates created successfully with Python")
        return True
        
    except ImportError:
        print("❌ Python cryptography library not installed")
        print("💡 Install with: pip install cryptography")
        
    except Exception as e:
        print(f"❌ Failed to create certificates with Python: {e}")
    
    # Create dummy certificates as last resort
    print("⚠️ Creating dummy certificates (INSECURE - for testing only)")
    
    try:
        # Create minimal dummy cert and key
        dummy_cert = """-----BEGIN CERTIFICATE-----
MIICpDCCAYwCCQC8pXKAowOHlTANBgkqhkiG9w0BAQsFADAUMRIwEAYDVQQDDAls
b2NhbGhvc3QwHhcNMjMwMTA1MTAwMDAwWhcNMjQwMTA1MTAwMDAwWjAUMRIwEAYD
VQQDDAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC6
iYlCqU8w1ZJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5AgMBAAEwDQYJ
KoZIhvcNAQELBQADggEBAGQxKzKpUyxGDyWzKgJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
-----END CERTIFICATE-----"""
        
        dummy_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6iYlCqU8w1ZJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5AgMBAAECggEABGJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5ZlJ5
-----END PRIVATE KEY-----"""
        
        with open(cert_file, "w") as f:
            f.write(dummy_cert)
        
        with open(key_file, "w") as f:
            f.write(dummy_key)
        
        print("⚠️ Dummy certificates created (TESTING ONLY)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create dummy certificates: {e}")
        return False

if __name__ == "__main__":
    success = create_ssl_certificates()
    if not success:
        print("❌ Failed to create SSL certificates")
        sys.exit(1)
    else:
        print("✅ SSL setup complete")