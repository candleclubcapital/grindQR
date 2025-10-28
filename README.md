<img width="1188" height="789" alt="Screenshot 2025-10-28 at 1 13 50 PM" src="https://github.com/user-attachments/assets/6b275d4d-e91f-4dcf-9f5a-ac5833e77247" />

# grindQR - Solana Vanity Key Generator

GUI application for generating Solana vanity addresses and exporting them as QR codes for easy wallet import.

## Features

- 🎨 **Futuristic UI** - Sleek cyberpunk design with real-time statistics
- 🔑 **Vanity Address Generation** - Create custom Solana addresses with specific prefixes/suffixes
- 📱 **Automatic QR Codes** - Instant QR code generation and preview
- 👻 **Phantom Wallet Compatible** - Export keys in Phantom-compatible format
- 📊 **Live Statistics** - Track keys generated and session time
- 🖥️ **Verbose Logging** - Color-coded console with detailed operation logs
- 📁 **Keypair Import** - Generate QR codes from existing keypair files

## Requirements

- Python 3.7+
- Solana CLI tools (`solana-keygen` must be installed and in PATH)
- Required Python packages:
  ```bash
  pip install pillow qrcode base58
  ```

## Usage

Run the application:
```bash
python grindqr.py
```

### Grinding Vanity Keys

1. Enter your desired prefix in "Starts With" (e.g., `ABC`)
2. Optionally enable "Ends With" and enter a suffix
3. Set quantity (number of keys to generate)
4. Click "▶ START GRINDING"
5. QR codes will automatically appear in the preview panel

### Importing Existing Keys

1. Click "📁 BROWSE"
2. Select your Solana keypair JSON file
3. QR code will be generated and displayed automatically

### Output

- All QR codes are saved in the `qrcodes/` directory
- Each QR contains the full private key in Base58 format
- Scan with Phantom wallet to import

DONATE IF YOU LIKE MY SOFTWARE
SToReRokJZCQ1tABAzLfLfNFDkLCtuMgYdgPrvXB26H <-- solana wallet
