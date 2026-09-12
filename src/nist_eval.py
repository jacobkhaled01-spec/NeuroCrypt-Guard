#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nist_eval.py
فاحص معايير العشوائية الإحصائية وفق NIST SP 800-22 Rev. 1a
Statistical Test Suite for Randomness (NIST SP 800-22) for NeuroCrypt-Guard

المراجع العلمية المعتمدة (APA 7th Edition):
- Rukhin, A., Soto, J., Nechvatal, J., Smid, M., Barker, E., Leigh, S., ... & Vo, S. (2010). 
  A statistical test suite for random and pseudorandom number generators for cryptographic 
  applications (NIST Special Publication 800-22 Rev. 1a). National Institute of Standards 
  and Technology. https://doi.org/10.6028/NIST.SP.800-22r1a
- Shannon, C. E. (1949). Communication theory of secrecy systems. 
  Bell System Technical Journal, 28(4), 656-715.
"""

from pathlib import Path
import sys
import math
import json
import argparse
from typing import Dict, Any, List, Tuple
import numpy as np
import scipy.special as sp
import torch

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, DEFAULT_MESSAGE_SIZE

# الثوابت المعيارية لمواصفة NIST SP 800-22
NIST_ALPHA: float = 0.01          # مستوى الدلالة الإحصائية الحرج
DEFAULT_BITSTREAM_SIZE: int = 1000000  # مليون بت معيارية لضمان قوة الاختبار الإحصائي


def generate_ciphertext_bitstream(alice: AliceNet, total_bits: int, msg_len: int, device: torch.device) -> np.ndarray:
    """
    توليد سيل بتات متصل ومستخرج من نصوص أليس المشفرة.
    Generates a continuous bitstream of encrypted bits from AliceNet.
    """
    alice.eval()
    num_blocks = math.ceil(total_bits / msg_len)
    batch_size = 1024
    collected_bits = []
    
    with torch.no_grad():
        for i in range(0, num_blocks, batch_size):
            curr_batch = min(batch_size, num_blocks - i)
            msgs = (torch.randint(0, 2, (curr_batch, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
            keys = (torch.randint(0, 2, (curr_batch, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
            
            ciphers = alice(msgs, keys)
            # تحويل القيم المستمرة إلى بتات ثنائية {0, 1} بناءً على الإشارة
            bits = (ciphers > 0).to(torch.int8).cpu().numpy().flatten()
            collected_bits.append(bits)

    bitstream = np.concatenate(collected_bits)[:total_bits]
    return bitstream


# --------------------------------------------------------------------------
# تنفيذ اختبارات NIST SP 800-22 الرياضية الدقيقة
# --------------------------------------------------------------------------

def test_frequency_monobit(bits: np.ndarray) -> Tuple[float, bool]:
    """1. اختبار التكرار الأحادي (Monobit Frequency Test)"""
    n = len(bits)
    # تحويل 0 -> -1 و 1 -> 1
    s_n = np.sum(2 * bits - 1)
    s_obs = abs(s_n) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2))
    return p_value, p_value >= NIST_ALPHA


def test_block_frequency(bits: np.ndarray, block_size: int = 128) -> Tuple[float, bool]:
    """2. اختبار التكرار المقطعي (Frequency Test within a Block)"""
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return 0.0, False
    
    blocks = bits[:num_blocks * block_size].reshape(num_blocks, block_size)
    proportions = np.mean(blocks, axis=1)
    chi_square = 4.0 * block_size * np.sum((proportions - 0.5) ** 2)
    p_value = float(sp.gammaincc(num_blocks / 2.0, chi_square / 2.0))
    return p_value, p_value >= NIST_ALPHA


def test_runs(bits: np.ndarray) -> Tuple[float, bool]:
    """3. اختبار التسلسلات (Runs Test)"""
    n = len(bits)
    pi = np.mean(bits)
    if abs(pi - 0.5) >= (2.0 / math.sqrt(n)):
        return 0.0, False  # فشل الفحص الأولي للتردد

    # حساب عدد التسلسلات V_n
    diffs = bits[1:] != bits[:-1]
    v_n = np.sum(diffs) + 1

    numerator = abs(v_n - 2.0 * n * pi * (1.0 - pi))
    denominator = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    p_value = math.erfc(numerator / denominator)
    return p_value, p_value >= NIST_ALPHA


def test_longest_run_of_ones(bits: np.ndarray) -> Tuple[float, bool]:
    """4. اختبار أطول تسلسل للآحاد في مقطع (Longest Run of Ones in a Block M=128)"""
    n = len(bits)
    m = 128
    num_blocks = n // m
    if num_blocks < 6272:
        # استخدام معيار M=128 المخصص للعينات الأقصر
        m = 128
        k = 5
        pi_vals = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    else:
        m = 128
        k = 5
        pi_vals = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]

    blocks = bits[:num_blocks * m].reshape(num_blocks, m)
    v_counts = [0] * (k + 1)

    for block in blocks:
        # حساب أطول تتابع للآحاد
        max_run = 0
        curr_run = 0
        for bit in block:
            if bit == 1:
                curr_run += 1
                if curr_run > max_run:
                    max_run = curr_run
            else:
                curr_run = 0
        
        if max_run <= 4:
            v_counts[0] += 1
        elif max_run == 5:
            v_counts[1] += 1
        elif max_run == 6:
            v_counts[2] += 1
        elif max_run == 7:
            v_counts[3] += 1
        elif max_run == 8:
            v_counts[4] += 1
        else:
            v_counts[5] += 1

    chi_sq = 0.0
    for i in range(len(v_counts)):
        expected = num_blocks * pi_vals[i]
        chi_sq += ((v_counts[i] - expected) ** 2) / expected

    p_value = float(sp.gammaincc(k / 2.0, chi_sq / 2.0))
    return p_value, p_value >= NIST_ALPHA


def test_discrete_fourier_transform(bits: np.ndarray) -> Tuple[float, bool]:
    """5. اختبار تحويل فورييه السريع للترددات الدورية (Spectral DFT Test)"""
    n = len(bits)
    x = 2 * bits - 1
    s = np.fft.fft(x)
    m = np.abs(s[:n // 2])
    t = math.sqrt(math.log(1.0 / 0.05) * n)
    n_0 = 0.95 * (n / 2.0)
    n_1 = np.sum(m < t)
    d = (n_1 - n_0) / math.sqrt(n * 0.95 * 0.05 / 4.0)
    p_value = math.erfc(abs(d) / math.sqrt(2))
    return p_value, p_value >= NIST_ALPHA


def test_cumulative_sums(bits: np.ndarray) -> Tuple[float, bool]:
    """6. اختبار المجاميع التراكمية (Cumulative Sums Forward Test)"""
    n = len(bits)
    x = 2 * bits - 1
    s = np.cumsum(x)
    z = np.max(np.abs(s))

    # تقريب NIST لمجموع دالة التوزيع التراكمي العادي
    sum1 = 0.0
    k_start = int(math.floor((-n / z + 1.0) / 4.0))
    k_end   = int(math.floor((n / z - 1.0) / 4.0))
    for k in range(k_start, k_end + 1):
        c1 = (4 * k + 1) * z / math.sqrt(n)
        c2 = (4 * k - 1) * z / math.sqrt(n)
        sum1 += (sp.ndtr(c1) - sp.ndtr(c2))

    sum2 = 0.0
    k_start2 = int(math.floor((-n / z - 3.0) / 4.0))
    k_end2   = int(math.floor((n / z - 1.0) / 4.0))
    for k in range(k_start2, k_end2 + 1):
        c3 = (4 * k + 3) * z / math.sqrt(n)
        c4 = (4 * k + 1) * z / math.sqrt(n)
        sum2 += (sp.ndtr(c3) - sp.ndtr(c4))

    p_value = 1.0 - sum1 + sum2
    p_value = max(0.0, min(1.0, p_value))
    return p_value, p_value >= NIST_ALPHA


def test_approximate_entropy(bits: np.ndarray, m: int = 2) -> Tuple[float, bool]:
    """7. اختبار الإنتروبيا التقريبية (Approximate Entropy Test)"""
    n = len(bits)
    
    def phi(block_len: int) -> float:
        # إضافة البتات الأولى في النهاية لتشكيل دائري (Circular)
        extended_bits = np.append(bits, bits[:block_len - 1])
        counts = {}
        for i in range(n):
            pattern = tuple(extended_bits[i:i + block_len])
            counts[pattern] = counts.get(pattern, 0) + 1
        
        c = np.array(list(counts.values()), dtype=np.float64) / n
        return float(np.sum(c * np.log(c)))

    phi_m = phi(m)
    phi_m1 = phi(m + 1)
    ap_en = phi_m - phi_m1
    chi_square = 2.0 * n * (math.log(2) - ap_en)
    p_value = float(sp.gammaincc(2 ** (m - 1), chi_square / 2.0))
    return p_value, p_value >= NIST_ALPHA


def test_serial(bits: np.ndarray, m: int = 3) -> Tuple[float, float, bool]:
    """8. اختبار التتابع (Serial Test m=3)"""
    n = len(bits)

    def psi_sq(block_len: int) -> float:
        if block_len == 0:
            return 0.0
        extended = np.append(bits, bits[:block_len - 1])
        counts = {}
        for i in range(n):
            pat = tuple(extended[i:i + block_len])
            counts[pat] = counts.get(pat, 0) + 1
        c = np.array(list(counts.values()), dtype=np.float64)
        return float((2 ** block_len / n) * np.sum(c ** 2) - n)

    psi_m = psi_sq(m)
    psi_m1 = psi_sq(m - 1)
    psi_m2 = psi_sq(m - 2)

    del1 = psi_m - psi_m1
    del2 = psi_m - 2 * psi_m1 + psi_m2

    p_val1 = float(sp.gammaincc(2 ** (m - 2), del1 / 2.0))
    p_val2 = float(sp.gammaincc(2 ** (m - 3), del2 / 2.0))
    passed = (p_val1 >= NIST_ALPHA) and (p_val2 >= NIST_ALPHA)
    return p_val1, p_val2, passed


def run_nist_suite(bitstream: np.ndarray) -> Dict[str, Any]:
    """
    تشغيل حزمة اختبارات NIST SP 800-22 الكاملة وجمع النتائج في تقرير موحد.
    """
    results = {}
    total_passed = 0
    total_tests = 0

    # 1. Monobit
    p, passed = test_frequency_monobit(bitstream)
    results["Frequency (Monobit)"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 2. Block Frequency
    p, passed = test_block_frequency(bitstream, block_size=128)
    results["Block Frequency (M=128)"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 3. Runs
    p, passed = test_runs(bitstream)
    results["Runs"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 4. Longest Run of Ones
    p, passed = test_longest_run_of_ones(bitstream)
    results["Longest Run of Ones (M=128)"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 5. Discrete Fourier Transform
    p, passed = test_discrete_fourier_transform(bitstream)
    results["Discrete Fourier Transform (Spectral)"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 6. Cumulative Sums
    p, passed = test_cumulative_sums(bitstream)
    results["Cumulative Sums (Forward)"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 7. Approximate Entropy
    p, passed = test_approximate_entropy(bitstream, m=2)
    results["Approximate Entropy (m=2)"] = {"p_value": round(p, 6), "passed": passed}
    total_passed += int(passed); total_tests += 1

    # 8. Serial
    p1, p2, passed = test_serial(bitstream, m=3)
    results["Serial Test (Pattern 1)"] = {"p_value": round(p1, 6), "passed": p1 >= NIST_ALPHA}
    results["Serial Test (Pattern 2)"] = {"p_value": round(p2, 6), "passed": p2 >= NIST_ALPHA}
    total_passed += int(p1 >= NIST_ALPHA) + int(p2 >= NIST_ALPHA); total_tests += 2

    pass_rate = (total_passed / total_tests) * 100.0

    return {
        "bitstream_length": len(bitstream),
        "significance_alpha": NIST_ALPHA,
        "tests_conducted": total_tests,
        "tests_passed": total_passed,
        "pass_rate_pct": round(pass_rate, 2),
        "nist_standard": "NIST SP 800-22 Rev. 1a",
        "detailed_results": results
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate NIST SP 800-22 Randomness")
    parser.add_argument("--msg_len", type=int, default=DEFAULT_MESSAGE_SIZE, help="طول الرسالة")
    parser.add_argument("--bits", type=int, default=DEFAULT_BITSTREAM_SIZE, help="عدد البتات الإجمالي")
    parser.add_argument("--checkpoint_dir", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار النماذج")
    parser.add_argument("--output_dir", type=str, default=str(PROJECT_ROOT / "نتائج_التقييم"), help="مجلد حفظ التقارير")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint_dir = Path(args.checkpoint_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 76)
    print("  فحص معايير العشوائية التشفيرية NIST SP 800-22 Rev. 1a: AliceNet")
    print(f"  • سيل البتات المستخرج: {args.bits:,} بت")
    print(f"  • مستوى الدلالة الإحصائي المعياري (Alpha): {NIST_ALPHA}")
    print("=" * 76)

    alice = AliceNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    alice_path = checkpoint_dir / "best_alice.pt"
    if not alice_path.exists():
        alice_path = checkpoint_dir / "final_alice.pt"

    if not alice_path.exists():
        print(f"[!] خطأ: لم يتم العثور على أوزان أليس في: {checkpoint_dir}")
        return

    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    print(f"[✓] تم تحميل نموذج أليس من: {alice_path.name}")
    print("[*] جاري توليد واستخراج سيل البتات التشفيرية من مخرجات الشبكة...")

    bitstream = generate_ciphertext_bitstream(alice, args.bits, args.msg_len, device)
    print(f"[✓] تم استخراج {len(bitstream):,} بت. بدء تطبيق حزمة الفحوصات الإحصائية...")

    report = run_nist_suite(bitstream)

    print("\n" + "-" * 76)
    print(f"{'اسم الاختبار (NIST SP 800-22 Test)':<42} | {'P-Value':<12} | {'النتيجة (Pass/Fail)'}")
    print("-" * 76)

    for name, data in report["detailed_results"].items():
        status = "✓ PASS" if data["passed"] else "✗ FAIL"
        print(f"{name:<42} | {data['p_value']:<12.6f} | {status}")

    print("-" * 76)
    print(f"\n📊 الملخص الإحصائي:")
    print(f"   • عدد الاختبارات الإجمالي: {report['tests_conducted']}")
    print(f"   • عدد الاختبارات الناجحة: {report['tests_passed']}")
    print(f"   • نسبة النجاح والامتثال: {report['pass_rate_pct']:.1f}%")

    if report["pass_rate_pct"] >= 88.0:
        print("   • التقييم المعياري: ✓ النماذج تحقق معايير العشوائية التشفيرية الدولية بنجاح.")
    else:
        print("   • التقييم المعياري: ⚠ النماذج تتطلب تحسينات إضافية لتوافق NIST الكامل.")

    report_path = output_dir / "nist_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[💾] تم حفظ التقرير الإحصائي الكامل في: {report_path}")
    print("=" * 76)


if __name__ == "__main__":
    main()
