#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fault_injection.py
محاكي هجمات حقن الأخطاء وفحص متانة قناة الاتصال المشوشة لـ NeuroCrypt-Guard
Fault Injection & Channel Noise Robustness Evaluator

المراجع العلمية المعتمدة (APA 7th Edition):
- Shannon, C. E. (1948). A mathematical theory of communication. 
  Bell System Technical Journal, 27(3), 379-423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
- Boneh, D., DeMillo, R. A., & Lipton, R. J. (2001). On the importance of eliminating 
  errors in cryptographic computations. Journal of Cryptology, 14(2), 101-119.
"""

from pathlib import Path
import sys
import json
import argparse
from typing import Dict, Any, List
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, BobNet, EveNet, DEFAULT_MESSAGE_SIZE
from src.loss import calculate_ber

# مستويات التشويش وحقن الأخطاء المحاكاة (من 0% إلى 50%)
NOISE_LEVELS: List[float] = [0.0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
DEFAULT_SAMPLES: int = 5000


def inject_noise_into_ciphertext(ciphertext: torch.Tensor, noise_rate: float) -> torch.Tensor:
    """
    محاكاة حقن الأخطاء في النص المشفر بقلب الإشارة باحتمالية noise_rate.
    Simulates physical fault injection / noisy BSC channel by flipping signs with probability noise_rate.
    """
    if noise_rate <= 0.0:
        return ciphertext

    # توليد قناع أخطاء برنولي
    noise_mask = (torch.rand_like(ciphertext) < noise_rate).float()
    # قلب إشارة البتات المشوشة (-1 -> 1, 1 -> -1)
    # المعادلة: x_noisy = x * (1 - 2 * mask)
    noisy_cipher = ciphertext * (1.0 - 2.0 * noise_mask)
    return noisy_cipher


def evaluate_robustness(
    alice: AliceNet,
    bob: BobNet,
    eve: EveNet,
    num_samples: int,
    msg_len: int,
    device: torch.device
) -> Dict[str, Any]:
    """
    قياس تدهور دقة استرجاع بوب وتخمين إيف عبر مستويات متزايدة من حقن الأخطاء.
    """
    alice.eval()
    bob.eval()
    eve.eval()

    msgs = (torch.randint(0, 2, (num_samples, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
    keys = (torch.randint(0, 2, (num_samples, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0

    results = []

    with torch.no_grad():
        clean_cipher = alice(msgs, keys)

        for rate in NOISE_LEVELS:
            noisy_cipher = inject_noise_into_ciphertext(clean_cipher, rate)
            
            bob_decrypted = bob(noisy_cipher, keys)
            eve_guess = eve(noisy_cipher)

            bob_ber = calculate_ber(msgs, bob_decrypted)
            eve_ber = calculate_ber(msgs, eve_guess)

            results.append({
                "noise_rate": rate,
                "noise_pct": round(rate * 100.0, 1),
                "bob_ber": round(bob_ber, 5),
                "bob_ber_pct": round(bob_ber * 100.0, 2),
                "eve_ber": round(eve_ber, 5),
                "eve_ber_pct": round(eve_ber * 100.0, 2),
                "secrecy_gap_pct": round((eve_ber - bob_ber) * 100.0, 2)
            })

    return {
        "num_samples": num_samples,
        "msg_len_bits": msg_len,
        "curve_data": results
    }


def plot_fault_curves(report: Dict[str, Any], output_path: Path) -> None:
    """
    رسم منحنيات استجابة بوب وإيف لحقن الأخطاء وحفظها PNG عالية الدقة.
    """
    noise_pcts = [item["noise_pct"] for item in report["curve_data"]]
    bob_bers   = [item["bob_ber_pct"] for item in report["curve_data"]]
    eve_bers   = [item["eve_ber_pct"] for item in report["curve_data"]]

    plt.figure(figsize=(10, 6))

    plt.plot(noise_pcts, bob_bers, 'o-', color='#059669', lw=2.5, label='Bob BER % (Decryption Error)')
    plt.plot(noise_pcts, eve_bers, 's--', color='#DC2626', lw=2.0, label='Eve BER % (Eavesdropper Error)')

    plt.axhline(50.0, color='#9CA3AF', linestyle=':', label='Theoretical Random Guess (50%)')
    plt.axvline(10.0, color='#F59E0B', linestyle='--', alpha=0.7, label='10% Fault Threshold')

    plt.title("NeuroCrypt-Guard Resilience against Fault Injection & Channel Noise", fontsize=13, fontweight='bold')
    plt.xlabel("Injected Fault / Noise Rate in Ciphertext (%)", fontsize=11, fontweight='bold')
    plt.ylabel("Observed Bit Error Rate (BER %)", fontsize=11, fontweight='bold')
    plt.ylim(-2, 60)
    plt.xlim(-1, 52)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='center right', fontsize=10)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Fault Injection Resilience")
    parser.add_argument("--msg_len", type=int, default=DEFAULT_MESSAGE_SIZE, help="طول الرسالة")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES, help="عدد العينات")
    parser.add_argument("--checkpoint_dir", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار النماذج")
    parser.add_argument("--output_dir", type=str, default=str(PROJECT_ROOT / "نتائج_التقييم"), help="مجلد حفظ النتائج")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint_dir = Path(args.checkpoint_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  فحص متانة حقن الأخطاء (Fault Injection Evaluator): NeuroCrypt-Guard")
    print(f"  • جهاز التشغيل: {device}")
    print(f"  • عدد العينات لكل مستوى تشويش: {args.samples:,}")
    print("=" * 72)

    alice = AliceNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    bob   = BobNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    eve   = EveNet(message_size=args.msg_len).to(device)

    alice_path = checkpoint_dir / "best_alice.pt"
    bob_path   = checkpoint_dir / "best_bob.pt"
    eve_path   = checkpoint_dir / "best_eve.pt"

    if not alice_path.exists():
        alice_path = checkpoint_dir / "final_alice.pt"
        bob_path   = checkpoint_dir / "final_bob.pt"
        eve_path   = checkpoint_dir / "final_eve.pt"

    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    bob.load_state_dict(torch.load(bob_path, map_location=device, weights_only=True))
    eve.load_state_dict(torch.load(eve_path, map_location=device, weights_only=True))
    print(f"[✓] تم تحميل النماذج المعتمدة من: {alice_path.parent}")

    report = evaluate_robustness(alice, bob, eve, args.samples, args.msg_len, device)

    print("\n" + "-" * 72)
    print(f"{'نسبة التشويش (Noise Rate)':<25} | {'Bob BER %':<15} | {'Eve BER %':<15} | {'الفجوة (Gap %)'}")
    print("-" * 72)

    for item in report["curve_data"]:
        print(f"{item['noise_pct']:>5.1f}%{' ': <19} | {item['bob_ber_pct']:>6.2f}%{' ': <7} | {item['eve_ber_pct']:>6.2f}%{' ': <7} | {item['secrecy_gap_pct']:>6.2f}%")

    print("-" * 72)

    # حفظ التقرير والرسم
    json_file = output_dir / "fault_injection_report.json"
    plot_file = output_dir / "fault_injection_curve.png"

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    plot_fault_curves(report, plot_file)

    print(f"\n[💾] تم حفظ تقرير حقن الأخطاء في: {json_file}")
    print(f"[📊] تم حفظ رسم المنحنى البياني في: {plot_file}")
    print("=" * 72)


if __name__ == "__main__":
    main()
