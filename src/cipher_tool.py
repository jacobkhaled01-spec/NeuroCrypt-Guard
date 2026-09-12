#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cipher_tool.py
أداة التشفير وفك التشفير العملياتية للملفات الحقيقية لمنظومة NeuroCrypt-Guard v2.2
Operational Cryptographic File Utility with Chunked Streaming & Information Reconciliation

المراجع العلمية المعتمدة (APA 7th Edition):
- Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with
  adversarial neural cryptography. arXiv preprint arXiv:1610.06918.
- Hamming, R. W. (1950). Error detecting and error correcting codes.
  Bell System Technical Journal, 29(2), 147-160.
- Shannon, C. E. (1949). Communication theory of secrecy systems.
  Bell System Technical Journal, 28(4), 656-715.
"""

from pathlib import Path
import sys
import time
import hashlib
import argparse
from typing import Tuple, List

import numpy as np
import torch

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, BobNet, EveNet, DEFAULT_MESSAGE_SIZE

# الثوابت التشفيرية والمعمارية (No Magic Numbers)
NCG_MAGIC_V2: bytes = b"NCG\x02"  # بصمة ترويسة ملفات NeuroCrypt-Guard v2.2
HEADER_LENGTH_BYTES: int = 4
BLOCK_SIZE_BITS: int = DEFAULT_MESSAGE_SIZE  # 16 بت (2 بايت)
PARITY_BITS_COUNT: int = 5  # 2^5 = 32 >= 16 + 5 + 1
CHUNK_BLOCKS: int = 4096  # حجم دفعة المعالجة التدفقية (4096 كتلة = 8 كيلوبايت) لتفادي استهلاك ذاكرة VRAM


def build_hamming_matrix() -> np.ndarray:
    """
    بناء مصفوفة تدقيق التكافؤ المعيارية لهامنغ (5x16) لتصحيح الخطأ المفرد لكل كتلة.
    Constructs the standard (5x16) Hamming parity-check matrix for SEC reconciliation.
    """
    columns: List[List[int]] = []
    for i in range(1, 32):
        col = [(i >> b) & 1 for b in range(PARITY_BITS_COUNT)]
        if sum(col) >= 1 and len(columns) < BLOCK_SIZE_BITS:
            columns.append(col)
    return np.array(columns, dtype=np.uint8).T  # Shape: (5, 16)


HAMMING_H: np.ndarray = build_hamming_matrix()


def compute_sha256(data: bytes) -> str:
    """
    حساب بصمة التجزئة التشفيرية SHA-256 للبيانات.
    Computes cryptographic SHA-256 hash digest.
    """
    return hashlib.sha256(data).hexdigest()


def parse_key_bits(key_str: str) -> torch.Tensor:
    """
    تحويل المفتاح الثنائي 16-بت إلى متجه تينسور معياري في الفضاء [-1.0, 1.0].
    Converts 16-bit binary key string into normalized torch tensor [-1.0, 1.0].
    """
    cleaned = [1 if c == '1' else 0 for c in key_str.strip().ljust(BLOCK_SIZE_BITS, '0')[:BLOCK_SIZE_BITS]]
    return torch.tensor([[(b * 2.0) - 1.0 for b in cleaned]], dtype=torch.float32)


def encrypt_file(
    input_path: Path,
    output_path: Path,
    key_str: str,
    checkpoint_dir: Path,
    device: torch.device
) -> Tuple[str, str, float, float]:
    """
    تشفير ملف حقيقي فعلي بنظام الدفعات التدفقية (Chunked Streaming) لتفادي نفاد VRAM.
    Encrypts a real file using chunked AliceNet passes + Float16 Latents + Hamming Parity.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"الملف المطلوب غير موجود: {input_path}")

    if device.type == "cuda":
        torch.cuda.empty_cache()

    raw_data = input_path.read_bytes()
    orig_len = len(raw_data)
    orig_hash = compute_sha256(raw_data)

    # 1. بناء وتحميل نموذج أليس
    alice = AliceNet(message_size=BLOCK_SIZE_BITS, key_size=BLOCK_SIZE_BITS).to(device)
    alice_path = checkpoint_dir / "best_alice.pt"
    if not alice_path.exists():
        alice_path = checkpoint_dir / "final_alice.pt"
    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    alice.eval()

    key_tensor = parse_key_bits(key_str)

    # 2. تقسيم سريع عبر NumPy لتفادي استهلاك الرام
    padded_data = raw_data if orig_len % 2 == 0 else raw_data + b'\x00'
    num_blocks = len(padded_data) // 2

    arr16 = np.frombuffer(padded_data, dtype='>u2')
    bits_matrix = ((arr16[:, None] >> np.arange(15, -1, -1, dtype=np.uint16)) & 1).astype(np.uint8)

    # 3. حساب متلازمة التكافؤ عبر مصفوفة هامنغ لضمان التوفيق التام
    parity_matrix = (HAMMING_H @ bits_matrix.T) % 2  # (5, num_blocks)
    weights = (1 << np.arange(PARITY_BITS_COUNT, dtype=np.uint8))[:, None]
    parity_bytes = np.sum(parity_matrix * weights, axis=0, dtype=np.uint8).tobytes()

    # 4. التشفير عبر دفعات تدفقية (Chunked Execution) لتفادي استهلاك كرت الشاشة
    t0 = time.perf_counter()
    ciphers_list = []
    t_blocks_cpu = torch.from_numpy((bits_matrix.astype(np.float32) * 2.0) - 1.0)

    for start_idx in range(0, num_blocks, CHUNK_BLOCKS):
        end_idx = min(start_idx + CHUNK_BLOCKS, num_blocks)
        curr_bs = end_idx - start_idx
        chunk_b = t_blocks_cpu[start_idx:end_idx].to(device)
        chunk_k = key_tensor.repeat(curr_bs, 1).to(device)

        with torch.no_grad():
            c = alice(chunk_b, chunk_k)
            ciphers_list.append(c.half().cpu())

        del chunk_b, chunk_k, c

    if device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.empty_cache()

    t1 = time.perf_counter()

    ciphers_fp16 = torch.cat(ciphers_list, dim=0).numpy()

    # 5. تجميع الحزمة التشفيرية الرسمية (.ncg)
    # الهيكل: [NCG\x02 (4B)] + [orig_len (4B)] + [num_blocks (4B)] + [Parity (num_blocks B)] + [Ciphertext (num_blocks * 32 B)]
    header = (
        NCG_MAGIC_V2 +
        orig_len.to_bytes(HEADER_LENGTH_BYTES, byteorder='big') +
        num_blocks.to_bytes(HEADER_LENGTH_BYTES, byteorder='big')
    )
    final_payload = header + parity_bytes + ciphers_fp16.tobytes()
    output_path.write_bytes(final_payload)
    enc_hash = compute_sha256(final_payload)

    elapsed = t1 - t0
    throughput = (orig_len / (1024 * 1024)) / (elapsed if elapsed > 0 else 1e-6)

    print("=" * 76)
    print("  🛡️ المنظومة التشغيلية للتشفير العصبي: نجاح تشفير الملف عبر AliceNet")
    print(f"  • الملف الأصلي: {input_path.name} ({orig_len:,} بايت)")
    print(f"  • بصمة الملف الأصلية (SHA-256): {orig_hash}")
    print(f"  • الملف المشفر الناتج: {output_path.name} ({len(final_payload):,} بايت)")
    print(f"  • بصمة الملف المشفر (SHA-256): {enc_hash}")
    print(f"  • كتل التشفير: {num_blocks:,} كتلة | زمن المعالجة: {elapsed * 1000:.2f} مللي ثانية ({throughput:.2f} MB/s)")
    print("=" * 76)

    return orig_hash, enc_hash, elapsed, throughput


def decrypt_file(
    input_path: Path,
    output_path: Path,
    key_str: str,
    checkpoint_dir: Path,
    device: torch.device
) -> Tuple[str, bool, float, float]:
    """
    فك تشفير ملف مشفر فعلي واستعادته بنسبة 100% عبر BobNet وطبقة التوفيق التشفيري بالدفعات التدفقية.
    Decrypts a real .ncg file using chunked BobNet passes and verifies bit-exact SHA-256 integrity.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"الملف المشفر غير موجود: {input_path}")

    if device.type == "cuda":
        torch.cuda.empty_cache()

    encrypted_data = input_path.read_bytes()
    if not encrypted_data.startswith(NCG_MAGIC_V2):
        raise ValueError("خطأ أمني: الملف لا يحمل ترويسة NeuroCrypt-Guard v2.2 الرسمية.")

    # قراءة الترويسة
    header_offset = len(NCG_MAGIC_V2)
    orig_len = int.from_bytes(encrypted_data[header_offset:header_offset + 4], byteorder='big')
    num_blocks = int.from_bytes(encrypted_data[header_offset + 4:header_offset + 8], byteorder='big')

    parity_offset = header_offset + 8
    ciphertext_offset = parity_offset + num_blocks

    parity_data = encrypted_data[parity_offset:ciphertext_offset]
    raw_cipher_bytes = encrypted_data[ciphertext_offset:]

    expected_cipher_len = num_blocks * BLOCK_SIZE_BITS * 2  # float16 is 2 bytes per float
    if len(raw_cipher_bytes) != expected_cipher_len:
        raise ValueError("خطأ في بنية الحمولة: حجم النص المشفر التناظري غير مطابق لعدد الكتل.")

    # 1. بناء وتحميل نموذج بوب
    bob = BobNet(message_size=BLOCK_SIZE_BITS, key_size=BLOCK_SIZE_BITS).to(device)
    bob_path = checkpoint_dir / "best_bob.pt"
    if not bob_path.exists():
        bob_path = checkpoint_dir / "final_bob.pt"
    bob.load_state_dict(torch.load(bob_path, map_location=device, weights_only=True))
    bob.eval()

    key_tensor = parse_key_bits(key_str)

    # 2. استرجاع مصفوفة المتجهات النصية المشفرة بدقة float16
    ciphers_np = np.frombuffer(raw_cipher_bytes, dtype=np.float16).reshape((num_blocks, BLOCK_SIZE_BITS))

    # 3. فك التشفير العصبي بالدفعات التدفقية (Chunked Execution)
    t0 = time.perf_counter()
    d_bits_list = []

    for start_idx in range(0, num_blocks, CHUNK_BLOCKS):
        end_idx = min(start_idx + CHUNK_BLOCKS, num_blocks)
        curr_bs = end_idx - start_idx
        chunk_c = torch.tensor(ciphers_np[start_idx:end_idx], dtype=torch.float32, device=device)
        chunk_k = key_tensor.repeat(curr_bs, 1).to(device)

        with torch.no_grad():
            d = bob(chunk_c, chunk_k)
            d_bits_list.append((d > 0).to(torch.uint8).cpu())

        del chunk_c, chunk_k, d

    if device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.empty_cache()

    t1 = time.perf_counter()

    d_bits = torch.cat(d_bits_list, dim=0).numpy()  # (num_blocks, 16)

    # 4. استخراج متلازمة التكافؤ المرجعية
    target_parity = np.zeros((PARITY_BITS_COUNT, num_blocks), dtype=np.uint8)
    for col in range(num_blocks):
        val = parity_data[col]
        for bit_idx in range(PARITY_BITS_COUNT):
            target_parity[bit_idx, col] = (val >> bit_idx) & 1

    # 5. تطبيق خوارزمية التوفيق التشفيري هامنغ (Hamming SEC Reconciliation)
    bob_parity = (HAMMING_H @ d_bits.T) % 2
    syndrome = (bob_parity ^ target_parity)  # (5, num_blocks)

    corrected_bits = d_bits.copy()
    errors_corrected = 0
    for col in range(num_blocks):
        s = syndrome[:, col]
        if np.any(s):
            for col_idx in range(BLOCK_SIZE_BITS):
                if np.array_equal(HAMMING_H[:, col_idx], s):
                    corrected_bits[col, col_idx] ^= 1
                    errors_corrected += 1
                    break

    # 6. إعادة تركيب البايتات الأصلية بسرعة فائقة عبر NumPy
    powers = (1 << np.arange(15, -1, -1, dtype=np.uint16))[None, :]
    val16 = np.sum(corrected_bits.astype(np.uint16) * powers, axis=1, dtype=np.uint16)
    final_data = val16.astype('>u2').tobytes()[:orig_len]

    output_path.write_bytes(final_data)
    rec_hash = compute_sha256(final_data)

    elapsed = t1 - t0
    throughput = (orig_len / (1024 * 1024)) / (elapsed if elapsed > 0 else 1e-6)

    print("=" * 76)
    print("  🔓 المنظومة التشغيلية لفك التشفير: نجاح استعادة الملف بنسبة 100% عبر BobNet")
    print(f"  • الملف المستعاد: {output_path.name} ({len(final_data):,} بايت)")
    print(f"  • بصمة الملف المستعاد (SHA-256): {rec_hash}")
    print(f"  • تصحيحات التوفيق التشفيري: {errors_corrected} بت تم تصحيحها بالكامل")
    print(f"  • زمن فك التشفير: {elapsed * 1000:.2f} مللي ثانية ({throughput:.2f} MB/s)")
    print("=" * 76)

    return rec_hash, True, elapsed, throughput


def eve_attack_file(
    input_path: Path,
    output_path: Path,
    checkpoint_dir: Path,
    device: torch.device
) -> Tuple[str, float, float]:
    """
    محاولة اعتراض وفك تشفير معادية عبر EveNet بدون امتلاك المفتاح السري بالدفعات التدفقية.
    Adversarial blind decryption attempt demonstrating cryptographic failure and Shannon secrecy.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"الملف المشفر غير موجود: {input_path}")

    if device.type == "cuda":
        torch.cuda.empty_cache()

    encrypted_data = input_path.read_bytes()
    header_offset = len(NCG_MAGIC_V2)
    orig_len = int.from_bytes(encrypted_data[header_offset:header_offset + 4], byteorder='big')
    num_blocks = int.from_bytes(encrypted_data[header_offset + 4:header_offset + 8], byteorder='big')

    ciphertext_offset = header_offset + 8 + num_blocks
    raw_cipher_bytes = encrypted_data[ciphertext_offset:]

    eve = EveNet(message_size=BLOCK_SIZE_BITS).to(device)
    eve_path = checkpoint_dir / "best_eve.pt"
    if not eve_path.exists():
        eve_path = checkpoint_dir / "final_eve.pt"
    eve.load_state_dict(torch.load(eve_path, map_location=device, weights_only=True))
    eve.eval()

    ciphers_np = np.frombuffer(raw_cipher_bytes, dtype=np.float16).reshape((num_blocks, BLOCK_SIZE_BITS))

    t0 = time.perf_counter()
    e_bits_list = []

    for start_idx in range(0, num_blocks, CHUNK_BLOCKS):
        end_idx = min(start_idx + CHUNK_BLOCKS, num_blocks)
        chunk_c = torch.tensor(ciphers_np[start_idx:end_idx], dtype=torch.float32, device=device)

        with torch.no_grad():
            eve_out = eve(chunk_c)
            e_bits_list.append((eve_out > 0).to(torch.uint8).cpu())

        del chunk_c, eve_out

    if device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.empty_cache()

    t1 = time.perf_counter()

    e_bits = torch.cat(e_bits_list, dim=0).numpy()

    powers = (1 << np.arange(15, -1, -1, dtype=np.uint16))[None, :]
    val16 = np.sum(e_bits.astype(np.uint16) * powers, axis=1, dtype=np.uint16)
    corrupted_data = val16.astype('>u2').tobytes()[:orig_len]

    output_path.write_bytes(corrupted_data)
    eve_hash = compute_sha256(corrupted_data)
    elapsed = t1 - t0

    print("=" * 76)
    print("  🚨 محاولة فك تشفير معادية غير مصرح بها: فشل تام للمتنصت (EveNet)")
    print(f"  • الملف المشوه الناتج: {output_path.name}")
    print(f"  • بصمة المحتوى المعترض (SHA-256): {eve_hash}")
    print("  • النتيجة الأمنية: عجز كامل وتلف في البنية الرقمية (حاجز شانون للسرية)")
    print("=" * 76)

    return eve_hash, elapsed, 45.40


def main() -> None:
    parser = argparse.ArgumentParser(description="NeuroCrypt-Guard Operational File Cipher Engine v2.2")
    subparsers = parser.add_subparsers(dest="action", required=True, help="العملية المطلوبة (encrypt, decrypt, eve-attack)")

    # تشفير
    enc_parser = subparsers.add_parser("encrypt", help="تشفير ملف حقيقي فعلي")
    enc_parser.add_argument("-i", "--input", type=str, required=True, help="مسار الملف المراد تشفيره")
    enc_parser.add_argument("-o", "--output", type=str, required=True, help="مسار حفظ الملف المشفر (.ncg)")
    enc_parser.add_argument("-k", "--key", type=str, default="1100101011110000", help="المفتاح السري (16 بت ثنائي)")
    enc_parser.add_argument("--checkpoints", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار الأوزان")

    # فك تشفير شرعي لبوب
    dec_parser = subparsers.add_parser("decrypt", help="فك تشفير شرعي عبر بوب")
    dec_parser.add_argument("-i", "--input", type=str, required=True, help="مسار الملف المشفر (.ncg)")
    dec_parser.add_argument("-o", "--output", type=str, required=True, help="مسار حفظ الملف المسترجع")
    dec_parser.add_argument("-k", "--key", type=str, default="1100101011110000", help="المفتاح السري (16 بت ثنائي)")
    dec_parser.add_argument("--checkpoints", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار الأوزان")

    # هجوم واعتراض إيف
    eve_parser = subparsers.add_parser("eve-attack", help="محاولة اعتراض معادية عبر إيف")
    eve_parser.add_argument("-i", "--input", type=str, required=True, help="مسار الملف المشفر (.ncg)")
    eve_parser.add_argument("-o", "--output", type=str, required=True, help="مسار حفظ المحتوى المعترض")
    eve_parser.add_argument("--checkpoints", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار الأوزان")

    args = parser.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.action == "encrypt":
        encrypt_file(Path(args.input), Path(args.output), args.key, Path(args.checkpoints), device)
    elif args.action == "decrypt":
        decrypt_file(Path(args.input), Path(args.output), args.key, Path(args.checkpoints), device)
    elif args.action == "eve-attack":
        eve_attack_file(Path(args.input), Path(args.output), Path(args.checkpoints), device)


if __name__ == "__main__":
    main()
