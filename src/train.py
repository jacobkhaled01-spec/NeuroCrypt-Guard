#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train.py
محرك التدريب التنافسي لمنظومة التشفير العصبي NeuroCrypt-Guard
Adversarial Training Engine for Neural Cryptography with Rigorous Validation

المراجع العلمية المعتمدة (APA 7th Edition):
- Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with
  adversarial neural cryptography. arXiv preprint arXiv:1610.06918.
- Shannon, C. E. (1949). Communication theory of secrecy systems. 
  Bell System Technical Journal, 28(4), 656-715.
- Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. 
  Advances in Cryptology - CRYPTO '85 Proceedings, 523-534.
"""

from pathlib import Path
import sys
import time
import argparse
import csv
import logging
from typing import Tuple

import torch
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, BobNet, EveNet, DEFAULT_MESSAGE_SIZE
from src.loss import loss_eve, loss_alice_bob, calculate_ber

# الثوابت المعيارية للتدريب (No Magic Numbers)
DEFAULT_STEPS: int = 5000
DEFAULT_BATCH_SIZE: int = 256
DEFAULT_LR: float = 0.0008
DEFAULT_K_EVE: int = 2
VALIDATION_SAMPLES: int = 5000
TARGET_BOB_BER: float = 0.01
EVE_BER_MIN: float = 0.44
EVE_BER_MAX: float = 0.52


def generate_batch(batch_size: int, bit_length: int, device: torch.device) -> torch.Tensor:
    """
    توليد دفعة عشوائية من البتات التشفيرية الموزعة بانتظام في الفضاء {-1.0, 1.0}.
    Generates a batch of uniformly distributed cryptographic binary vectors.
    """
    bits = torch.randint(0, 2, (batch_size, bit_length), device=device, dtype=torch.float32)
    return (bits * 2.0) - 1.0


def validate_models(
    alice: AliceNet,
    bob: BobNet,
    eve: EveNet,
    val_msg: torch.Tensor,
    val_key: torch.Tensor,
) -> Tuple[float, float, float]:
    """
    تقييم النماذج على مجموعة تحقق مستقلة لحساب BER وفجوة السرية.
    Evaluates models on independent validation set without computing gradients.
    """
    alice.eval()
    bob.eval()
    eve.eval()

    with torch.no_grad():
        ciphertext = alice(val_msg, val_key)
        bob_decrypted = bob(ciphertext, val_key)
        eve_guess = eve(ciphertext)

        ber_bob = calculate_ber(val_msg, bob_decrypted)
        ber_eve = calculate_ber(val_msg, eve_guess)
        secrecy_gap = (ber_eve - ber_bob) * 100.0

    return ber_bob, ber_eve, secrecy_gap


def plot_training_curves(history_file: Path, output_plot: Path) -> None:
    """
    رسم منحنيات التدريب وحفظها كصورة عالية الدقة PNG.
    Generates and saves high-resolution publication-quality training curves.
    """
    steps = []
    loss_ab = []
    ber_bob = []
    ber_eve = []

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                steps.append(int(row["step"]))
                loss_ab.append(float(row["loss_ab"]))
                ber_bob.append(float(row["val_ber_bob"]) * 100.0)
                ber_eve.append(float(row["val_ber_eve"]) * 100.0)

        if not steps:
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # رسم الخسارة المشتركة
        ax1.plot(steps, loss_ab, color="#2563EB", lw=2, label="Loss (Alice & Bob Joint)")
        ax1.set_ylabel("Loss Magnitude", fontsize=11, fontweight="bold")
        ax1.set_title("NeuroCrypt-Guard Adversarial Training Dynamics", fontsize=13, fontweight="bold")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="upper right")

        # رسم معدلات خطأ البتات (BER)
        ax2.plot(steps, ber_bob, color="#059669", lw=2, label="Bob BER % (Target < 1%)")
        ax2.plot(steps, ber_eve, color="#DC2626", lw=2, label="Eve BER % (Target ~ 50%)")
        ax2.axhline(50.0, color="#9CA3AF", linestyle=":", label="Shannon Ideal Eve (50%)")
        ax2.axhline(1.0, color="#10B981", linestyle=":", label="Acceptable Bob Limit (1%)")
        ax2.set_xlabel("Adversarial Steps", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Bit Error Rate (BER %)", fontsize=11, fontweight="bold")
        ax2.set_ylim(-2, 60)
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="center right")

        plt.tight_layout()
        output_plot.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_plot, dpi=300)
        plt.close()
    except Exception as e:
        print(f"[!] Warning: Could not generate training plot: {e}")


def train(args: argparse.Namespace) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    eval_dir = PROJECT_ROOT / "نتائج_التقييم"
    eval_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  بدء محرك التدريب التنافسي الموثوق: NeuroCrypt-Guard v2.0")
    print(f"  • جهاز التشغيل: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print(f"  • طول الرسالة والمفتاح: {args.msg_len} بت")
    print(f"  • حجم الدفعة (Batch Size): {args.batch_size}")
    print(f"  • عدد الخطوات الإجمالي: {args.steps:,}")
    print(f"  • خطوات الخصم إيف (k-steps): {args.k_eve}")
    print(f"  • معدل التعلم الابتدائي: {args.lr}")
    print("=" * 72)

    # 1. تهيئة النماذج بأوزان عشوائية جديدة
    alice = AliceNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    bob   = BobNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    eve   = EveNet(message_size=args.msg_len).to(device)

    # 2. إعداد المحسنات ومجدول معدل التعلم
    opt_ab  = optim.Adam(list(alice.parameters()) + list(bob.parameters()), lr=args.lr, betas=(0.9, 0.999))
    opt_eve = optim.Adam(eve.parameters(), lr=args.lr, betas=(0.9, 0.999))

    scheduler_ab = CosineAnnealingLR(opt_ab, T_max=args.steps, eta_min=args.lr * 0.05)
    scheduler_eve = CosineAnnealingLR(opt_eve, T_max=args.steps, eta_min=args.lr * 0.05)

    # 3. توليد مجموعة تحقق مستقلة وثابتة
    val_msg = generate_batch(VALIDATION_SAMPLES, args.msg_len, device)
    val_key = generate_batch(VALIDATION_SAMPLES, args.msg_len, device)

    # 4. إعداد ملف التاريخ
    history_file = save_dir / "training_history.csv"
    with open(history_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["step", "loss_ab", "loss_bob", "loss_eve", "val_ber_bob", "val_ber_eve", "secrecy_gap", "time_sec"])

    start_time = time.time()
    best_score = -999.0
    best_bob_ber = 1.0
    best_eve_ber = 0.0
    saved_flag = False

    print("\n[🚀] جاري بدء حلقة التنافس والتشفير العصبي...\n")
    print(f"{'Step':<7} | {'Loss AB':<9} | {'Bob L1':<8} | {'Eve L1':<8} | {'Bob BER':<9} | {'Eve BER':<9} | {'Gap %':<7} | {'Status'}")
    print("-" * 80)

    for step in range(1, args.steps + 1):
        # -------------------------------------------------------------
        # المرحلة 1: تدريب المتنصت Eve لـ k خطوات
        # -------------------------------------------------------------
        alice.eval()
        bob.eval()
        eve.train()

        for _ in range(args.k_eve):
            opt_eve.zero_grad()
            msg = generate_batch(args.batch_size, args.msg_len, device)
            key = generate_batch(args.batch_size, args.msg_len, device)

            with torch.no_grad():
                ciphertext = alice(msg, key)

            eve_guess = eve(ciphertext)
            l_eve = loss_eve(msg, eve_guess)
            l_eve.backward()
            opt_eve.step()

        # -------------------------------------------------------------
        # المرحلة 2: تدريب تحالف Alice & Bob
        # -------------------------------------------------------------
        alice.train()
        bob.train()
        eve.eval()

        opt_ab.zero_grad()
        msg = generate_batch(args.batch_size, args.msg_len, device)
        key = generate_batch(args.batch_size, args.msg_len, device)

        ciphertext = alice(msg, key)
        bob_decrypted = bob(ciphertext, key)
        eve_guess = eve(ciphertext)

        l_ab, l_bob_val, l_eve_val = loss_alice_bob(msg, bob_decrypted, eve_guess)
        l_ab.backward()
        opt_ab.step()

        scheduler_ab.step()
        scheduler_eve.step()

        # -------------------------------------------------------------
        # التقييم والتحقق الدوري المستقل
        # -------------------------------------------------------------
        if step % args.print_every == 0 or step == 1 or step == args.steps:
            val_ber_bob, val_ber_eve, secrecy_gap = validate_models(alice, bob, eve, val_msg, val_key)
            elapsed = time.time() - start_time

            # تسجيل المؤشرات
            with open(history_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    step,
                    f"{l_ab.item():.4f}",
                    f"{l_bob_val.item():.4f}",
                    f"{l_eve_val.item():.4f}",
                    f"{val_ber_bob:.4f}",
                    f"{val_ber_eve:.4f}",
                    f"{secrecy_gap:.2f}",
                    f"{elapsed:.1f}"
                ])

            status = "Training..."
            is_secure = (val_ber_bob <= TARGET_BOB_BER) and (EVE_BER_MIN <= val_ber_eve <= EVE_BER_MAX)
            
            # مقياس الجودة المركب للنموذج الأفضل
            composite_score = (1.0 - val_ber_bob) * 100.0 - 200.0 * abs(val_ber_eve - 0.50)

            if is_secure:
                status = "★ SECURE!"
                if composite_score > best_score:
                    best_score = composite_score
                    best_bob_ber = val_ber_bob
                    best_eve_ber = val_ber_eve
                    torch.save(alice.state_dict(), save_dir / "best_alice.pt")
                    torch.save(bob.state_dict(), save_dir / "best_bob.pt")
                    torch.save(eve.state_dict(), save_dir / "best_eve.pt")
                    saved_flag = True
            elif val_ber_bob < 0.05 and val_ber_eve >= 0.40:
                status = "Near Secure"
                if not saved_flag and composite_score > best_score:
                    best_score = composite_score
                    best_bob_ber = val_ber_bob
                    best_eve_ber = val_ber_eve
                    torch.save(alice.state_dict(), save_dir / "best_alice.pt")
                    torch.save(bob.state_dict(), save_dir / "best_bob.pt")
                    torch.save(eve.state_dict(), save_dir / "best_eve.pt")

            print(f"{step:<7} | {l_ab.item():<9.4f} | {l_bob_val.item():<8.4f} | {l_eve_val.item():<8.4f} | {val_ber_bob*100:<8.2f}% | {val_ber_eve*100:<8.2f}% | {secrecy_gap:<6.1f}% | {status}")

    # حفظ الأوزان عند نهاية التدريب
    torch.save(alice.state_dict(), save_dir / "final_alice.pt")
    torch.save(bob.state_dict(), save_dir / "final_bob.pt")
    torch.save(eve.state_dict(), save_dir / "final_eve.pt")

    # توليد رسم المنحنيات
    plot_output = eval_dir / "training_curves.png"
    plot_training_curves(history_file, plot_output)

    print("-" * 80)
    total_time = time.time() - start_time
    print(f"\n[✓] اكتملت دورة التدريب بالكامل بنجاح في {total_time:.1f} ثانية!")
    if saved_flag:
        print(f"[✓] تم تحقيق معيار الأمان التام بنجاح وحفظ النماذج المعتمدة (Best Checkpoints):")
        print(f"    • دقة فك تشفير بوب: {(1.0 - best_bob_ber)*100:.2f}% (BER: {best_bob_ber*100:.2f}%)")
        print(f"    • حيرة إيف التامة: {best_eve_ber*100:.2f}% (قريب من التخمين المثالي 50%)")
        print(f"    • الفجوة الأمنية المحققة: {(best_eve_ber - best_bob_ber)*100:.2f}%")
    else:
        print(f"[*] تم حفظ النماذج في: {save_dir}")
    print(f"[📊] تم حفظ رسم المنحنيات في: {plot_output}")
    print(f"[📋] تم تسجيل التاريخ في: {history_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NeuroCrypt-Guard Models")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help="عدد خطوات التدريب التنافسي")
    parser.add_argument("--batch_size", type=int, default=DEFAULT_BATCH_SIZE, help="حجم الدفعة")
    parser.add_argument("--msg_len", type=int, default=DEFAULT_MESSAGE_SIZE, help="طول الرسالة والمفتاح بالبت")
    parser.add_argument("--lr", type=float, default=DEFAULT_LR, help="معدل التعلم الأولي")
    parser.add_argument("--k_eve", type=int, default=DEFAULT_K_EVE, help="عدد خطوات إيف لكل خطوة أليس وبوب")
    parser.add_argument("--print_every", type=int, default=200, help="معدل الرصد والطباعة")
    parser.add_argument("--save_dir", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مجلد حفظ النماذج")

    args = parser.parse_args()
    train(args)
