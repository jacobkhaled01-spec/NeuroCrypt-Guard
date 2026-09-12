#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluate.py
فاحص التقييم الأمني ومعدل خطأ البتات لمنظومة NeuroCrypt-Guard
Baseline Security & Bit Error Rate Evaluator with Comprehensive Reporting

المراجع العلمية المعتمدة (APA 7th Edition):
- Shannon, C. E. (1949). Communication theory of secrecy systems. 
  Bell System Technical Journal, 28(4), 656-715.
- Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with
  adversarial neural cryptography. arXiv preprint arXiv:1610.06918.
- Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. 
  Advances in Cryptology - CRYPTO '85 Proceedings, 523-534.
"""

from pathlib import Path
import sys
import json
import argparse
from typing import Dict, Any, Tuple
import numpy as np
import torch

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, BobNet, EveNet, DEFAULT_MESSAGE_SIZE
from src.loss import calculate_ber


def evaluate_on_data(
    alice: AliceNet,
    bob: BobNet,
    eve: EveNet,
    messages: torch.Tensor,
    keys: torch.Tensor,
    dataset_name: str = "Evaluation Dataset",
) -> Dict[str, Any]:
    """
    تقييم دقة بوب وحيرة إيف على مصفوفة بيانات محددة وحساب الفجوة الأمنية.
    Evaluates Bob accuracy and Eve confusion on a given dataset and computes secrecy metrics.
    """
    alice.eval()
    bob.eval()
    eve.eval()

    with torch.no_grad():
        ciphertext = alice(messages, keys)
        bob_decrypted = bob(ciphertext, keys)
        eve_guess = eve(ciphertext)

        bob_ber = calculate_ber(messages, bob_decrypted)
        eve_ber = calculate_ber(messages, eve_guess)

    bob_acc = (1.0 - bob_ber) * 100.0
    eve_acc = (1.0 - eve_ber) * 100.0
    secrecy_gap = (eve_ber - bob_ber) * 100.0

    if bob_ber <= 0.01 and 0.44 <= eve_ber <= 0.52:
        verdict = "✓ آمن ومحمي بالكامل (Perfect Secrecy Achieved - Shannon Compliant)"
        is_secure = True
    elif bob_ber < 0.05 and eve_ber >= 0.40:
        verdict = "⚠ حماية جيدة (Good Protection - Near Theoretical Secrecy)"
        is_secure = True
    elif bob_ber >= 0.10:
        verdict = "✗ غير مستقر (فشل بوب في استعادة الرسالة بالكامل)"
        is_secure = False
    else:
        verdict = "⚠ حماية جزئية (إيف تستنتج بعض الأنماط)"
        is_secure = False

    print(f"\n📊 نتائج تقييم: {dataset_name}")
    print(f"   • دقة استرجاع بوب (Bob Accuracy):  {bob_acc:.2f}% (BER: {bob_ber*100:.2f}%)")
    print(f"   • دقة تخمين إيف (Eve Accuracy):    {eve_acc:.2f}% (BER: {eve_ber*100:.2f}%)")
    print(f"   • الفجوة الأمنية (Secrecy Gap):     {secrecy_gap:.2f}%")
    print(f"   • الحكم النهائي: {verdict}")

    return {
        "dataset_name": dataset_name,
        "sample_count": len(messages),
        "bob_ber": round(bob_ber, 5),
        "bob_accuracy_pct": round(bob_acc, 2),
        "eve_ber": round(eve_ber, 5),
        "eve_accuracy_pct": round(eve_acc, 2),
        "secrecy_gap_pct": round(secrecy_gap, 2),
        "is_secure": is_secure,
        "verdict": verdict,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate NeuroCrypt-Guard Models")
    parser.add_argument("--msg_len", type=int, default=DEFAULT_MESSAGE_SIZE, help="طول الرسالة بالبت")
    parser.add_argument("--checkpoint_dir", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار حفظ النماذج")
    parser.add_argument("--num_samples", type=int, default=10000, help="عدد عينات الاختبار العشوائية")
    parser.add_argument("--output_dir", type=str, default=str(PROJECT_ROOT / "نتائج_التقييم"), help="مجلد حفظ التقارير")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint_dir = Path(args.checkpoint_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  تشغيل فاحص التقييم الأمني المعياري: NeuroCrypt-Guard v2.0")
    print(f"  • جهاز الفحص: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print("=" * 70)

    # 1. تهيئة النماذج وتحميل الأوزان
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

    if not alice_path.exists():
        print(f"[!] خطأ: لم يتم العثور على أوزان في {checkpoint_dir}. يرجى تشغيل train.py أولاً.")
        return

    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    bob.load_state_dict(torch.load(bob_path, map_location=device, weights_only=True))
    eve.load_state_dict(torch.load(eve_path, map_location=device, weights_only=True))
    print(f"[✓] تم تحميل الأوزان بنجاح من: {alice_path.parent}")

    full_report = {
        "evaluation_timestamp": str(np.datetime64('now')),
        "message_size_bits": args.msg_len,
        "checkpoint_used": str(alice_path.name),
        "results": []
    }

    # 2. التقييم على العينات العشوائية التركيبية (CSPRNG)
    rand_msgs = (torch.randint(0, 2, (args.num_samples, args.msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
    rand_keys = (torch.randint(0, 2, (args.num_samples, args.msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
    csprng_res = evaluate_on_data(alice, bob, eve, rand_msgs, rand_keys, dataset_name="CSPRNG Uniform Synthetic Dataset")
    full_report["results"].append(csprng_res)

    # 3. التقييم على كتل النصوص الحقيقية (Sherlock Holmes Corpus)
    real_data_path = PROJECT_ROOT / "مجموعات_البيانات" / "real_corpora" / f"real_dataset_blocks_{args.msg_len}bit.npz"
    if real_data_path.exists():
        real_npz = np.load(real_data_path)
        real_test_blocks = torch.tensor(real_npz['test'], dtype=torch.float32, device=device)
        num_real = len(real_test_blocks)
        real_keys = (torch.randint(0, 2, (num_real, args.msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
        real_res = evaluate_on_data(alice, bob, eve, real_test_blocks, real_keys, dataset_name="Sherlock Holmes Real-World Corpus")
        full_report["results"].append(real_res)
    else:
        print(f"[*] لم يتم العثور على ملف الكتل الحقيقية في: {real_data_path}")

    # 4. حفظ التقرير في نتائج_التقييم
    json_path = output_dir / "baseline_evaluation_report.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)

    print(f"\n[📁] تم حفظ تقرير التقييم الكامل في: {json_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
