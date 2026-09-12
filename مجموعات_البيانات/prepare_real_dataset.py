#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_real_dataset.py
أداة تنزيل ومعالجة مجموعات البيانات النصية الحقيقية لمنظومة التشفير العصبي
Real-World Dataset Downloader & Binary Preprocessor for NeuroCrypt-Guard
"""

import os
import sys
import urllib.request
import ssl
import numpy as np

CORPUS_URLS = [
    # رابط رسمي من Project Gutenberg: The Adventures of Sherlock Holmes
    "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    # رابط بديل احتياطي في حال حجب أو بطء الخادم الأول
    "https://raw.githubusercontent.com/redacted-authors/sherlock/master/holmes.txt",
    # رابط إضافي: Alice's Adventures in Wonderland
    "https://www.gutenberg.org/cache/epub/11/pg11.txt"
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_corpora")

def download_corpus(target_path: str) -> bool:
    """تنزيل النص الحقيقي من المستودع العالمي وحفظه محلياً"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # إعداد سياق SSL مرن ومتوافق
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for url in CORPUS_URLS:
        try:
            print(f"[*] محاولة تنزيل الداتا سيت من الرابط:\n    {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                # إزالة ترويسة وتذييل مشروع غوتنبرغ للاحتفاظ بالنص الخام فقط
                start_marker = "*** START OF THE PROJECT GUTENBERG"
                end_marker = "*** END OF THE PROJECT GUTENBERG"
                
                start_idx = content.find(start_marker)
                if start_idx != -1:
                    content = content[content.find("\n", start_idx) + 1:]
                    
                end_idx = content.find(end_marker)
                if end_idx != -1:
                    content = content[:end_idx]
                    
                content = content.strip()
                
                if len(content) > 10_000:
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"[✓] تم تنزيل وحفظ الداتا سيت بنجاح! الحجم: {len(content):,} حرف.")
                    return True
        except Exception as e:
            print(f"[-] تعذر التنزيل من الرابط ({e})، جاري تجربة الرابط التالي...")
            continue
            
    return False

def preprocess_and_convert_to_bits(raw_path: str, block_size: int = 16) -> np.ndarray:
    """
    تحويل النص الكامل إلى مصفوفة كتل ثنائية {-1.0, 1.0} جاهزة للشبكة
    """
    with open(raw_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # تحويل النص إلى بايتات UTF-8
    byte_array = text.encode('utf-8')
    # تفكيك البايتات إلى مصفوفة بتات فردية (0 و 1)
    raw_bits = np.unpackbits(np.frombuffer(byte_array, dtype=np.uint8))
    
    # ضبط الطول ليكون من مضاعفات حجم الكتلة (Padding)
    total_bits = len(raw_bits)
    remainder = total_bits % block_size
    if remainder != 0:
        pad_size = block_size - remainder
        raw_bits = np.pad(raw_bits, (0, pad_size), mode='constant', constant_values=0)
        
    num_blocks = len(raw_bits) // block_size
    blocks = raw_bits.reshape((num_blocks, block_size))
    
    # التحويل إلى ثنائي قطبي {-1.0, 1.0} لملائمة الشبكات العصبية
    bipolar_blocks = (blocks.astype(np.float32) * 2.0) - 1.0
    return bipolar_blocks

def main():
    print("=" * 65)
    print("  بدء تجهيز وتحميل مجموعة البيانات الحقيقية لمشروع NeuroCrypt-Guard")
    print("=" * 65)
    
    corpus_file = os.path.join(OUTPUT_DIR, "sherlock_holmes_crypto_corpus.txt")
    
    # 1. تنزيل البيانات إذا لم تكن موجودة
    if not os.path.exists(corpus_file):
        success = download_corpus(corpus_file)
        if not success:
            print("[!] فشل تنزيل النص من جميع الروابط. يرجى التحقق من الاتصال بالإنترنت.")
            return
    else:
        print(f"[*] ملف النص الحقيقي موجود مسبقاً في: {corpus_file}")
        
    # 2. إحصائيات النص
    with open(corpus_file, 'r', encoding='utf-8') as f:
        text = f.read()
    words = text.split()
    print(f"\n📊 إحصائيات مجموعة البيانات الحقيقية:")
    print(f"   • إجمالي عدد الأحرف: {len(text):,} حرف")
    print(f"   • إجمالي عدد الكلمات: {len(words):,} كلمة")
    print(f"   • الحجم التقديري بالبتات: {len(text.encode('utf-8')) * 8:,} بت")

    # 3. معالجة وتصدير الكتل الثنائية بأحجام مختلفة (16، 32، 64 بت)
    for bit_len in [16, 32, 64]:
        blocks = preprocess_and_convert_to_bits(corpus_file, block_size=bit_len)
        out_npz = os.path.join(OUTPUT_DIR, f"real_dataset_blocks_{bit_len}bit.npz")
        
        # تقسيم إلى 80% تدريب و 20% اختبار
        split_idx = int(0.8 * len(blocks))
        train_blocks = blocks[:split_idx]
        test_blocks = blocks[split_idx:]
        
        np.savez_compressed(out_npz, train=train_blocks, test=test_blocks)
        print(f"\n[✓] تم تصدير كتل ({bit_len}-bit):")
        print(f"    - المسار: {out_npz}")
        print(f"    - كتل التدريب (Train): {train_blocks.shape[0]:,} كتلة")
        print(f"    - كتل الاختبار (Test):  {test_blocks.shape[0]:,} كتلة")
        
    print("\n" + "=" * 65)
    print("  [✓] اكتملت بنجاح عملية تجهيز وتحويل مجموعة البيانات الحقيقية!")
    print("=" * 65)

if __name__ == "__main__":
    main()
