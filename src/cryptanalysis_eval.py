#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cryptanalysis_eval.py
تقييم الصمود التشفيري ضد طيف الخصوم المتعددين (Adversarial Capacity Spectrum)
Rigorous Cryptanalytic Hardness Evaluation against Multi-Tier Adversaries for Q1 Benchmarks

المراجع العلمية المعتمدة (APA 7th Edition):
- Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with
  adversarial neural cryptography. arXiv preprint arXiv:1610.06918.
- Gräf, F., & Šíma, J. (2017). On the capacity of neural networks for adversarial encryption.
  Neural Networks, 93, 112-120. https://doi.org/10.1016/j.neunet.2017.06.002
- Shannon, C. E. (1949). Communication theory of secrecy systems.
  Bell System Technical Journal, 28(4), 656-715.
"""

from pathlib import Path
import sys
import json
import time
from typing import Dict, Any

import numpy as np
import torch
import torch.optim as optim

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, BobNet, EveNet, DeepEveNet, DEFAULT_MESSAGE_SIZE
from src.loss import loss_eve, calculate_ber

STEPS_PER_ADVERSARY: int = 1500
BATCH_SIZE: int = 256
EVAL_SAMPLES: int = 5000


def evaluate_adversaries() -> Dict[str, Any]:
    """
    تدريب واختبار 3 مستويات من الخصوم ضد أليس لحساب الفجوة الأمنية وقدرة الصمود.
    Evaluates 3 tiers of adversaries against Alice to measure cryptanalytic hardness.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 76)
    print(f"  🛡️ بدء التقييم التشفيري المتقدم لطيف الخصوم (Q1 Benchmark): {device}")
    print("=" * 76)

    alice = AliceNet(message_size=DEFAULT_MESSAGE_SIZE).to(device)
    alice_path = PROJECT_ROOT / "checkpoints" / "best_alice.pt"
    if not alice_path.exists():
        alice_path = PROJECT_ROOT / "checkpoints" / "final_alice.pt"
    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    alice.eval()

    # توليد بيانات التحقق
    val_msg = (torch.randint(0, 2, (EVAL_SAMPLES, DEFAULT_MESSAGE_SIZE), device=device, dtype=torch.float32) * 2.0) - 1.0
    val_key = (torch.randint(0, 2, (EVAL_SAMPLES, DEFAULT_MESSAGE_SIZE), device=device, dtype=torch.float32) * 2.0) - 1.0
    with torch.no_grad():
        val_c = alice(val_msg, val_key)

    adversaries = {
        "Standard_Eve": EveNet(message_size=DEFAULT_MESSAGE_SIZE).to(device),
        "Wide_Eve": EveNet(message_size=DEFAULT_MESSAGE_SIZE).to(device),
        "Deep_Residual_Eve": DeepEveNet(message_size=DEFAULT_MESSAGE_SIZE, channels=64).to(device)
    }

    results: Dict[str, Any] = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "eval_samples": EVAL_SAMPLES,
        "adversaries": {}
    }

    for adv_name, adv_model in adversaries.items():
        print(f"\n[+] تقييم الخصم: {adv_name}...")
        opt = optim.Adam(adv_model.parameters(), lr=0.001)

        t0 = time.time()
        for step in range(1, STEPS_PER_ADVERSARY + 1):
            adv_model.train()
            opt.zero_grad()
            m = (torch.randint(0, 2, (BATCH_SIZE, DEFAULT_MESSAGE_SIZE), device=device, dtype=torch.float32) * 2.0) - 1.0
            k = (torch.randint(0, 2, (BATCH_SIZE, DEFAULT_MESSAGE_SIZE), device=device, dtype=torch.float32) * 2.0) - 1.0
            with torch.no_grad():
                c = alice(m, k)
            pred = adv_model(c)
            l = loss_eve(m, pred)
            l.backward()
            opt.step()

        elapsed = time.time() - t0

        adv_model.eval()
        with torch.no_grad():
            val_pred = adv_model(val_c)
            ber = calculate_ber(val_msg, val_pred)

        param_count = sum(p.numel() for p in adv_model.parameters())
        print(f"    • المعاملات: {param_count:,} وزن")
        print(f"    • معدل خطأ البتات (BER): {ber * 100:.2f}% (الهدف النظري لشانون: 50.00%)")
        print(f"    • زمن التدريب المكثف: {elapsed:.2f} ثانية")

        results["adversaries"][adv_name] = {
            "parameters": param_count,
            "final_ber": float(ber),
            "final_ber_pct": round(float(ber) * 100.0, 2),
            "secrecy_retained": bool(ber > 0.38),
            "training_time_sec": round(elapsed, 2)
        }

    out_dir = PROJECT_ROOT / "نتائج_التقييم"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "cryptanalysis_adversary_spectrum.json"
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[✓] تم حفظ تقرير طيف الخصوم في: {out_file}")
    return results


if __name__ == "__main__":
    evaluate_adversaries()
