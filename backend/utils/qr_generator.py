"""
Organic Roots QR Code Generator
Generates QR codes for product verification with consumer URLs
"""
import sys
import os
import qrcode
import qrcode.constants
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import io
import base64

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import QR_BASE_URL, QR_CODES_DIR

class QRCodeGenerator:
    """QR code generator for Organic Roots product verification"""
    
    def __init__(self):
        self.qr_codes_dir = QR_CODES_DIR
        self.base_url = QR_BASE_URL
        
        # Ensure QR codes directory exists
        self.qr_codes_dir.mkdir(exist_ok=True)
        
        # QR code styling
        self.box_size = 10
        self.border = 4
        self.fill_color = "#2D6A4F"  # Organic Roots green
        self.back_color = "#FFFFFF"  # White background
        
        # Logo settings (optional)
        self.logo_size = 60
        self.logo_position = None  # Will be calculated
    
    def generate_verification_url(self, batch_code: str) -> str:
        """Generate verification URL for a batch"""
        return f"{self.base_url}{batch_code}"
    
    def create_qr_code(self, batch_code: str, include_logo: bool = True) -> Dict[str, Any]:
        """Create a QR code for a batch"""
        print(f"🔄 Generating QR code for batch: {batch_code}")
        
        # Generate verification URL
        verification_url = self.generate_verification_url(batch_code)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)
        
        # Add logo if requested
        if include_logo:
            qr_img = self._add_logo(qr_img)
        
        # Add text label
        qr_img = self._add_text_label(qr_img, batch_code)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_{batch_code}_{timestamp}.png"
        filepath = self.qr_codes_dir / filename
        
        # Save QR code
        qr_img.save(filepath, "PNG", quality=95)
        
        print(f"✅ QR code saved: {filepath}")
        
        return {
            "batch_code": batch_code,
            "verification_url": verification_url,
            "filename": filename,
            "filepath": str(filepath),
            "relative_path": f"qr_codes/{filename}",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _add_logo(self, qr_img: Image.Image) -> Image.Image:
        """Add Organic Roots logo to QR code (placeholder)"""
        # Create a simple logo placeholder
        logo_size = self.logo_size
        logo_img = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo_img)
        
        # Draw a simple "OR" logo
        font_size = 20
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Draw green circle background
        margin = 5
        draw.ellipse([margin, margin, logo_size-margin, logo_size-margin], 
                    fill="#2D6A4F")
        
        # Draw "OR" text
        text = "OR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (logo_size - text_width) // 2
        y = (logo_size - text_height) // 2
        
        draw.text((x, y), text, fill="white", font=font)
        
        # Calculate position to center logo
        qr_width, qr_height = qr_img.size
        logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        
        # Paste logo onto QR code
        qr_img.paste(logo_img, logo_pos, logo_img)
        
        return qr_img
    
    def _add_text_label(self, qr_img: Image.Image, batch_code: str) -> Image.Image:
        """Add text label below QR code"""
        # Create space for text
        qr_width, qr_height = qr_img.size
        text_height = 40
        new_height = qr_height + text_height + 10
        
        # Create new image with space for text
        new_img = Image.new('RGB', (qr_width, new_height), 'white')
        new_img.paste(qr_img, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(new_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Draw batch code
        text = f"Batch: {batch_code}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        x = (qr_width - text_width) // 2
        y = qr_height + 5
        
        draw.text((x, y), text, fill="#2D6A4F", font=font)
        
        # Draw "Scan to verify" text
        verify_text = "Scan to verify"
        bbox = draw.textbbox((0, 0), verify_text, font=font)
        verify_width = bbox[2] - bbox[0]
        
        x = (qr_width - verify_width) // 2
        y = y + 20
        
        draw.text((x, y), verify_text, fill="#888888", font=font)
        
        return new_img
    
    def generate_qr_base64(self, batch_code: str) -> Dict[str, Any]:
        """Generate QR code as base64 string for API responses"""
        # Generate verification URL
        verification_url = self.generate_verification_url(batch_code)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,  # Smaller for base64
            border=2,
        )
        
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)
        
        # Convert to base64
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "batch_code": batch_code,
            "verification_url": verification_url,
            "qr_base64": qr_base64,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def batch_generate_qr_codes(self, batch_codes: list) -> list:
        """Generate QR codes for multiple batches"""
        results = []
        
        for batch_code in batch_codes:
            try:
                result = self.create_qr_code(batch_code)
                results.append(result)
            except Exception as e:
                print(f"❌ Error generating QR code for {batch_code}: {e}")
                results.append({
                    "batch_code": batch_code,
                    "error": str(e)
                })
        
        return results
    
    def get_qr_code_info(self, batch_code: str) -> Optional[Dict[str, Any]]:
        """Get information about existing QR code for a batch"""
        # Search for existing QR code files
        qr_files = list(self.qr_codes_dir.glob(f"qr_{batch_code}_*.png"))
        
        if not qr_files:
            return None
        
        # Get the most recent file
        latest_file = max(qr_files, key=os.path.getctime)
        
        return {
            "batch_code": batch_code,
            "filename": latest_file.name,
            "filepath": str(latest_file),
            "relative_path": f"qr_codes/{latest_file.name}",
            "verification_url": self.generate_verification_url(batch_code),
            "created_at": datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
        }
    
    def delete_qr_code(self, batch_code: str) -> bool:
        """Delete QR code for a batch"""
        qr_files = list(self.qr_codes_dir.glob(f"qr_{batch_code}_*.png"))
        
        if not qr_files:
            return False
        
        for file_path in qr_files:
            try:
                file_path.unlink()
                print(f"🗑️ Deleted QR code: {file_path}")
            except Exception as e:
                print(f"❌ Error deleting {file_path}: {e}")
                return False
        
        return True
    
    def cleanup_old_qr_codes(self, days_old: int = 30) -> int:
        """Clean up QR codes older than specified days"""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        deleted_count = 0
        
        for file_path in self.qr_codes_dir.glob("*.png"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"🗑️ Deleted old QR code: {file_path}")
                except Exception as e:
                    print(f"❌ Error deleting {file_path}: {e}")
        
        print(f"✅ Cleaned up {deleted_count} old QR codes")
        return deleted_count
    
    def get_qr_stats(self) -> Dict[str, Any]:
        """Get QR code generation statistics"""
        qr_files = list(self.qr_codes_dir.glob("*.png"))
        
        total_codes = len(qr_files)
        
        if total_codes == 0:
            return {
                "total_codes": 0,
                "storage_dir": str(self.qr_codes_dir),
                "oldest_code": None,
                "newest_code": None
            }
        
        # Get file stats
        file_times = [os.path.getctime(f) for f in qr_files]
        oldest_time = min(file_times)
        newest_time = max(file_times)
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in qr_files)
        
        return {
            "total_codes": total_codes,
            "storage_dir": str(self.qr_codes_dir),
            "oldest_code": datetime.fromtimestamp(oldest_time).isoformat(),
            "newest_code": datetime.fromtimestamp(newest_time).isoformat(),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

# Global instance
qr_generator = QRCodeGenerator()

def test_qr_generator():
    """Test the QR code generator"""
    print("🧪 Testing QR Code Generator...")
    
    # Test single QR code generation
    test_batch_code = "TEST_QR_001"
    result = qr_generator.create_qr_code(test_batch_code)
    
    print(f"Generated QR code for {result['batch_code']}:")
    print(f"  Verification URL: {result['verification_url']}")
    print(f"  File: {result['filename']}")
    print(f"  Path: {result['filepath']}")
    
    # Test base64 generation
    print("\nTesting base64 QR code generation...")
    base64_result = qr_generator.generate_qr_base64("TEST_QR_002")
    print(f"Base64 QR code generated: {len(base64_result['qr_base64'])} characters")
    
    # Test batch generation
    print("\nTesting batch QR code generation...")
    batch_codes = ["BATCH_001", "BATCH_002", "BATCH_003"]
    batch_results = qr_generator.batch_generate_qr_codes(batch_codes)
    print(f"Generated {len(batch_results)} QR codes in batch")
    
    # Test QR code info retrieval
    print("\nTesting QR code info retrieval...")
    info = qr_generator.get_qr_code_info(test_batch_code)
    if info:
        print(f"Found QR code info for {info['batch_code']}")
        print(f"  Created: {info['created_at']}")
    
    # Test statistics
    print("\nTesting QR code statistics...")
    stats = qr_generator.get_qr_stats()
    print(f"Total QR codes: {stats['total_codes']}")
    print(f"Storage directory: {stats['storage_dir']}")
    if stats['total_codes'] > 0:
        print(f"Oldest: {stats['oldest_code']}")
        print(f"Newest: {stats['newest_code']}")
        print(f"Total size: {stats['total_size_mb']} MB")
    
    print("✅ QR Code Generator test completed!")

if __name__ == "__main__":
    test_qr_generator()
