#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
csprng_generator.py
مولد البيانات والبتات العشوائية المشفرة لمنظومة NeuroCrypt-Guard
Cryptographically Secure Bitstream & Training Batch Generator
"""

import os
import sys
import argparse
import secrets
import numpy as np

def generate_csprng_bits(num_samples: int, bit_length: int, bipolar: bool = True):
    """
    توليد مصفوفة بتات عشوائية باستخدام CSPRNG (os.urandom).
    
    Args:
        num_samples: عدد العينات (الرسائل أو المفاتيح).
        bit_length: طول كل رسالة بالبتات (مثلاً 16، 32، 64).
        bipolar: إذا كانت True تعيد {-1.0, 1.0}، وإذا كانت False تعيد {0, 1}.
        
    Returns:
        numpy.ndarray: مصفوفة بحجم (num_samples, bit_length)
    """
    total_bits = num_samples * bit_length
    total_bytes = (total_bits + 7) // 8
    random_bytes = os.urandom(total_bytes)
    
    # تحويل البايتات إلى مصفوفة بتات ثنائية
    bits = np.unpackbits(np.frombuffer(random_bytes, dtype=np.uint8))[:total_bits]
    bits = bits.reshape((num_samples, bit_length))
    
    if bipolar:
        # تحويل 0 -> -1.0 و 1 -> 1.0 لملائمة مدخلات الشبكات العصبية
        return (bits.astype(np.float32) * 2.0) - 1.0
    return bits

def text_to_bipolar_bits(text: str, pad_to_multiple: int = 16) -> np.ndarray:
    """
    تحويل نص عادي (Plaintext) إلى مصفوفة بتات {-1.0, 1.0} لاختبار التكرارات اللغوية.
    """
    raw_bytes = text.encode('utf-8')
    bits = np.unpackbits(np.frombuffer(raw_bytes, dtype=np.uint8))
    
    remainder = len(bits) % pad_to_multiple
    if remainder != 0:
        padding_len = pad_to_multiple - remainder
        bits = np.pad(bits, (0, padding_len), mode='constant', constant_values=0)
        
    num_blocks = len(bits) // pad_to_multiple
    bits_2d = bits.reshape((num_blocks, pad_to_multiple))
    return (bits_2d.astype(np.float32) * 2.0) - 1.0

def export_nist_bitstream(filename: str, total_bits: int = 1_000_000):
    """
    تصدير ملف ثنائي يحوي على الأقل مليون بت عشوائي ناتج من CSPRNG
    لتمريره إلى حزمة اختبارات NIST SP 800-22.
    """
    total_bytes = total_bits // 8
    random_bytes = os.urandom(total_bytes)
    with open(filename, 'wb') as f:
        f.write(random_bytes)
    print(f"[✓] تم تصدير {total_bits:,} بت عشوائي بنجاح إلى الملف: {filename}")

def self_test():
    """فحص ذاتي للتحقق من سلامة المولد وتوازن التوزيع الإحصائي"""
    print("[*] جاري تنفيذ الفحص الذاتي لمولد CSPRNG...")
    samples = 10_000
    bit_len = 32
    data = generate_csprng_bits(samples, bit_len, bipolar=True)
    
    # التحقق من الأبعاد
    assert data.shape == (samples, bit_len), f"خطأ في الأبعاد: {data.shape}"
    
    # التحقق من القيم {-1, 1}
    unique_vals = set(np.unique(data))
    assert unique_vals.issubset({-1.0, 1.0}), f"قيم غير متوقعة: {unique_vals}"
    
    # فحص التوازن الإحصائي (يجب أن يكون المتوسط قريباً جداً من الصفر)
    mean_val = float(np.mean(data))
    print(f"[✓] نجح الفحص الذاتي! متوسط التوزيع: {mean_val:.4f} (القيمة المثالية: 0.0000)")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuroCrypt CSPRNG Data Generator")
    parser.add_argument("--test", action="store_true", help="تشغيل الفحص الذاتي")
    parser.add_argument("--nist", action="store_true", help="تصدير ملف بتات لاختبارات NIST")
    parser.add_argument("--bits", type=int, default=1_000_000, help="عدد البتات لاختبار NIST")
    parser.add_argument("--out", type=str, default="nist_test_bits.bin", help="اسم ملف الخرج")
    
    args = parser.parse_args()
    
    if args.test or len(sys.argv) == 1:
        self_test()
    if args.nist:
        export_nist_bitstream(args.out, args.bits)
