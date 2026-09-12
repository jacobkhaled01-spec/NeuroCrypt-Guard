#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aes_benchmark.py
المقارنة المعيارية للأداء والإنتاجية بين NeuroCrypt-Guard و AES-128
Performance Benchmarking vs Standard AES-128 (Throughput & Latency)

المراجع العلمية المعتمدة (APA 7th Edition):
- Daemen, J., & Rijmen, V. (2002). The design of Advanced Encryption Standard (AES). 
  Springer Science & Business Media. https://doi.org/10.1007/978-3-662-04722-4
- National Institute of Standards and Technology. (2001). Advanced Encryption Standard (AES)
  (FIPS PUB 197). U.S. Department of Commerce.
"""

from pathlib import Path
import sys
import os
import time
import json
import argparse
from typing import Dict, Any
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# استخدام مكتبة cryptography القياسية المدعومة بمكتبة OpenSSL
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, BobNet, DEFAULT_MESSAGE_SIZE

# ثوابت الفحص المعياري
BENCHMARK_BYTES: int = 4 * 1024 * 1024  # 4 ميجابايت من البيانات للاختبار
WARMUP_ROUNDS: int = 5


def benchmark_aes(data_bytes: bytes, key_bytes: bytes) -> Dict[str, float]:
    """قياس سرعة تشفير وفك تشفير AES-128 عبر محرك OpenSSL المسرع عتادياً"""
    backend = default_backend()
    
    # تسخين (Warm-up)
    warmup_cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=backend)
    warmup_enc = warmup_cipher.encryptor()
    for _ in range(WARMUP_ROUNDS):
        _ = warmup_enc.update(data_bytes[:1024])

    # 1. قياس زمن التشفير
    cipher_enc = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=backend)
    encryptor = cipher_enc.encryptor()
    
    t0 = time.perf_counter()
    ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
    t1 = time.perf_counter()
    enc_time = t1 - t0

    # 2. قياس زمن فك التشفير
    cipher_dec = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=backend)
    decryptor = cipher_dec.decryptor()
    
    t0 = time.perf_counter()
    _ = decryptor.update(ciphertext) + decryptor.finalize()
    t1 = time.perf_counter()
    dec_time = t1 - t0

    size_mb = len(data_bytes) / (1024 * 1024)
    enc_throughput = size_mb / enc_time
    dec_throughput = size_mb / dec_time

    num_blocks = len(data_bytes) // 16
    latency_enc_us = (enc_time / num_blocks) * 1e6
    latency_dec_us = (dec_time / num_blocks) * 1e6

    return {
        "enc_throughput_mb_s": round(enc_throughput, 2),
        "dec_throughput_mb_s": round(dec_throughput, 2),
        "enc_latency_us_per_block": round(latency_enc_us, 3),
        "dec_latency_us_per_block": round(latency_dec_us, 3),
        "total_time_sec": round(enc_time + dec_time, 4)
    }


def benchmark_neurocrypt(alice: AliceNet, bob: BobNet, total_bits: int, msg_len: int, device: torch.device) -> Dict[str, float]:
    """قياس سرعة وتأخير تشفير وفك تشفير NeuroCrypt-Guard"""
    alice.eval()
    bob.eval()

    batch_size = 4096
    num_blocks = total_bits // msg_len
    num_batches = num_blocks // batch_size
    actual_blocks = num_batches * batch_size
    total_bytes = (actual_blocks * msg_len) // 8

    # توليد عينات الاختبار دفعة واحدة
    msgs = (torch.randint(0, 2, (batch_size, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
    keys = (torch.randint(0, 2, (batch_size, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0

    # تسخين
    with torch.no_grad():
        for _ in range(WARMUP_ROUNDS):
            c = alice(msgs, keys)
            _ = bob(c, keys)
        if device.type == "cuda":
            torch.cuda.synchronize()

    # قياس زمن التشفير
    with torch.no_grad():
        t0 = time.perf_counter()
        for _ in range(num_batches):
            c = alice(msgs, keys)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
    enc_time = t1 - t0

    # قياس زمن فك التشفير
    with torch.no_grad():
        t0 = time.perf_counter()
        for _ in range(num_batches):
            _ = bob(c, keys)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
    dec_time = t1 - t0

    size_mb = total_bytes / (1024 * 1024)
    enc_throughput = size_mb / enc_time
    dec_throughput = size_mb / dec_time

    latency_enc_us = (enc_time / actual_blocks) * 1e6
    latency_dec_us = (dec_time / actual_blocks) * 1e6

    return {
        "enc_throughput_mb_s": round(enc_throughput, 2),
        "dec_throughput_mb_s": round(dec_throughput, 2),
        "enc_latency_us_per_block": round(latency_enc_us, 3),
        "dec_latency_us_per_block": round(latency_dec_us, 3),
        "total_time_sec": round(enc_time + dec_time, 4)
    }


def plot_comparison_chart(report: Dict[str, Any], output_image: Path) -> None:
    """رسم بياني شريطي لمقارنة الإنتاجية والكمون"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    systems = ['AES-128 (OpenSSL/C)', 'NeuroCrypt-Guard']
    enc_throughputs = [report['aes_128']['enc_throughput_mb_s'], report['neurocrypt_guard']['enc_throughput_mb_s']]
    dec_throughputs = [report['aes_128']['dec_throughput_mb_s'], report['neurocrypt_guard']['dec_throughput_mb_s']]

    x = np.arange(len(systems))
    width = 0.35

    # 1. رسم الإنتاجية
    ax1.bar(x - width/2, enc_throughputs, width, label='Encryption Throughput', color='#2563EB')
    ax1.bar(x + width/2, dec_throughputs, width, label='Decryption Throughput', color='#059669')
    ax1.set_ylabel('Throughput (MB/s)', fontsize=11, fontweight='bold')
    ax1.set_title('Throughput Comparison (Higher is Better)', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(systems, fontweight='bold')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.4, axis='y')

    # 2. رسم الكمون لكل كتلة
    enc_latencies = [report['aes_128']['enc_latency_us_per_block'], report['neurocrypt_guard']['enc_latency_us_per_block']]
    dec_latencies = [report['aes_128']['dec_latency_us_per_block'], report['neurocrypt_guard']['dec_latency_us_per_block']]

    ax2.bar(x - width/2, enc_latencies, width, label='Encryption Latency', color='#EA580C')
    ax2.bar(x + width/2, dec_latencies, width, label='Decryption Latency', color='#7C3AED')
    ax2.set_ylabel('Latency per Block (µs)', fontsize=11, fontweight='bold')
    ax2.set_title('Block Latency Comparison (Lower is Better)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(systems, fontweight='bold')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.4, axis='y')

    plt.tight_layout()
    output_image.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_image, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark NeuroCrypt-Guard vs AES-128")
    parser.add_argument("--msg_len", type=int, default=DEFAULT_MESSAGE_SIZE, help="طول الرسالة")
    parser.add_argument("--checkpoint_dir", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار النماذج")
    parser.add_argument("--output_dir", type=str, default=str(PROJECT_ROOT / "نتائج_التقييم"), help="مجلد حفظ النتائج")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint_dir = Path(args.checkpoint_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 74)
    print("  المقارنة المعيارية للأداء (Benchmark): NeuroCrypt-Guard vs AES-128")
    print(f"  • جهاز فحص الشبكة العصبية: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • حجم البيانات المعيارية: {BENCHMARK_BYTES / (1024*1024):.1f} MB")
    print("=" * 74)

    # 1. فحص AES-128
    aes_key = os.urandom(16)
    aes_data = os.urandom(BENCHMARK_BYTES)
    print("[*] جاري فحص أداء معيار AES-128 عبر محرك OpenSSL...")
    aes_results = benchmark_aes(aes_data, aes_key)

    # 2. فحص NeuroCrypt-Guard
    alice = AliceNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    bob   = BobNet(message_size=args.msg_len, key_size=args.msg_len).to(device)

    alice_path = checkpoint_dir / "best_alice.pt"
    bob_path   = checkpoint_dir / "best_bob.pt"

    if not alice_path.exists():
        alice_path = checkpoint_dir / "final_alice.pt"
        bob_path   = checkpoint_dir / "final_bob.pt"

    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    bob.load_state_dict(torch.load(bob_path, map_location=device, weights_only=True))
    print(f"[✓] تم تحميل نماذج التشفير العصبي من: {alice_path.parent}")

    total_bits = BENCHMARK_BYTES * 8
    print("[*] جاري فحص أداء منظومة NeuroCrypt-Guard على الدفعات المتوازية...")
    neuro_results = benchmark_neurocrypt(alice, bob, total_bits, args.msg_len, device)

    report = {
        "timestamp": str(np.datetime64('now')),
        "hardware_device": str(device),
        "data_size_mb": BENCHMARK_BYTES / (1024 * 1024),
        "aes_128": aes_results,
        "neurocrypt_guard": neuro_results
    }

    print("\n" + "-" * 74)
    print(f"{'المعيار التشفيري (Cryptosystem)':<28} | {'سرعة التشفير':<14} | {'سرعة الفك':<14} | {'الكمون/كتلة'}")
    print("-" * 74)
    print(f"{'AES-128 (OpenSSL/C)':<28} | {aes_results['enc_throughput_mb_s']:>8.1f} MB/s | {aes_results['dec_throughput_mb_s']:>8.1f} MB/s | {aes_results['enc_latency_us_per_block']:>8.3f} µs")
    print(f"{'NeuroCrypt-Guard (GPU)':<28} | {neuro_results['enc_throughput_mb_s']:>8.1f} MB/s | {neuro_results['dec_throughput_mb_s']:>8.1f} MB/s | {neuro_results['enc_latency_us_per_block']:>8.3f} µs")
    print("-" * 74)

    # حفظ التقرير والرسم
    json_path = output_dir / "aes_benchmark_report.json"
    plot_path = output_dir / "aes_comparison_bar.png"

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    plot_comparison_chart(report, plot_path)

    print(f"\n[💾] تم حفظ التقرير المقارن في: {json_path}")
    print(f"[📊] تم حفظ المخطط البياني في: {plot_path}")
    print("=" * 74)


if __name__ == "__main__":
    main()
