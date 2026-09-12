#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sac_eval.py
فاحص معيار تأثير الانهيار الصارم (Strict Avalanche Criterion - SAC)
Strict Avalanche Criterion Evaluator for NeuroCrypt-Guard (AliceNet)

المراجع العلمية المعتمدة (APA 7th Edition):
- Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. 
  Advances in Cryptology - CRYPTO '85 Proceedings, 523-534. https://doi.org/10.1007/3-540-39799-X_41
- Shannon, C. E. (1949). Communication theory of secrecy systems. 
  Bell System Technical Journal, 28(4), 656-715.
"""

from pathlib import Path
import sys
import argparse
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# ضبط مسار المشروع الأساسي
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import AliceNet, DEFAULT_MESSAGE_SIZE

# الثوابت المعيارية لمعيار SAC وفق Webster & Tavares (1985)
DEFAULT_NUM_TRIALS: int = 5000
SAC_IDEAL_PROBABILITY: float = 0.50
SAC_ACCEPTABLE_TOLERANCE: float = 0.05  # مجال القبول [0.45, 0.55]


def compute_sac_matrix(
    alice: AliceNet,
    num_trials: int,
    msg_len: int,
    device: torch.device
) -> np.ndarray:
    """
    حساب مصفوفة SAC بمقاس (msg_len x msg_len) لشبكة AliceNet:
    لكل بت دخل i، يتم قلبه ورصد احتمالية تغير كل بت خرج j في النص المشفر.
    
    Calculates the N x N SAC dependence matrix according to Webster & Tavares (1985).
    """
    alice.eval()
    sac_matrix = np.zeros((msg_len, msg_len), dtype=np.float64)

    # توليد عينات أساسية موحدة
    base_msgs = (torch.randint(0, 2, (num_trials, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0
    base_keys = (torch.randint(0, 2, (num_trials, msg_len), device=device, dtype=torch.float32) * 2.0) - 1.0

    with torch.no_grad():
        base_cipher = alice(base_msgs, base_keys)
        base_bits = (base_cipher > 0).to(torch.int8)

        # فحص تأثير قلب كل بت في الرسالة
        for i in range(msg_len):
            flipped_msgs = base_msgs.clone()
            # قلب البت رقم i: من 1 إلى -1 أو العكس
            flipped_msgs[:, i] = -flipped_msgs[:, i]

            flipped_cipher = alice(flipped_msgs, base_keys)
            flipped_bits = (flipped_cipher > 0).to(torch.int8)

            # حساب التغير في كل بت في الخرج
            bit_changes = torch.ne(base_bits, flipped_bits).float()  # (num_trials, msg_len)
            flip_probabilities = torch.mean(bit_changes, dim=0).cpu().numpy()
            sac_matrix[i, :] = flip_probabilities

    return sac_matrix


def plot_sac_heatmap(sac_matrix: np.ndarray, output_image: Path) -> None:
    """
    رسم الخريطة الحرارية لمصفوفة SAC وحفظها كصورة PNG عالية الدقة.
    Generates and saves publication-quality SAC matrix heatmap.
    """
    msg_len = sac_matrix.shape[0]
    plt.figure(figsize=(9, 7.5))

    sns.heatmap(
        sac_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        vmin=0.35,
        vmax=0.65,
        center=0.50,
        cbar_kws={'label': 'Bit Flip Probability (Ideal = 0.500)'},
        linewidths=0.5,
        linecolor='white'
    )

    plt.title(f"Strict Avalanche Criterion (SAC) Matrix ({msg_len}x{msg_len})\nNeuroCrypt-Guard AliceNet", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Output Ciphertext Bit Position (j)", fontsize=11, fontweight='bold')
    plt.ylabel("Flipped Input Plaintext Bit Position (i)", fontsize=11, fontweight='bold')
    plt.tight_layout()

    output_image.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_image, dpi=300)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Strict Avalanche Criterion (SAC)")
    parser.add_argument("--msg_len", type=int, default=DEFAULT_MESSAGE_SIZE, help="طول الرسالة")
    parser.add_argument("--trials", type=int, default=DEFAULT_NUM_TRIALS, help="عدد العينات للاختبار")
    parser.add_argument("--checkpoint_dir", type=str, default=str(PROJECT_ROOT / "checkpoints"), help="مسار النماذج")
    parser.add_argument("--output_dir", type=str, default=str(PROJECT_ROOT / "نتائج_التقييم"), help="مجلد حفظ النتائج")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint_dir = Path(args.checkpoint_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  فحص تأثير الانهيار الصارم (SAC Evaluator): NeuroCrypt-Guard")
    print(f"  • حجم المصفوفة: {args.msg_len}x{args.msg_len}")
    print(f"  • عدد محاولات الفحص الإحصائي: {args.trials:,}")
    print("=" * 72)

    alice = AliceNet(message_size=args.msg_len, key_size=args.msg_len).to(device)
    alice_path = checkpoint_dir / "best_alice.pt"
    if not alice_path.exists():
        alice_path = checkpoint_dir / "final_alice.pt"

    if not alice_path.exists():
        print(f"[!] خطأ: لم يتم العثور على أوزان أليس في: {checkpoint_dir}")
        return

    alice.load_state_dict(torch.load(alice_path, map_location=device, weights_only=True))
    print(f"[✓] تم تحميل نموذج أليس من: {alice_path.name}")

    # حساب المصفوفة
    sac_matrix = compute_sac_matrix(alice, args.trials, args.msg_len, device)

    # التحليل الإحصائي
    mean_prob = np.mean(sac_matrix)
    std_prob  = np.std(sac_matrix)
    min_prob  = np.min(sac_matrix)
    max_prob  = np.max(sac_matrix)
    
    # نسبة البتات المتوافقة مع معيار التسامح 0.50 ± 0.05
    compliant_elements = np.sum(np.abs(sac_matrix - 0.50) <= SAC_ACCEPTABLE_TOLERANCE)
    total_elements = args.msg_len * args.msg_len
    compliance_rate = (compliant_elements / total_elements) * 100.0

    print("\n📊 المؤشرات الإحصائية لمصفوفة SAC:")
    print(f"   • متوسط احتمالية التغير (Mean Flip Prob): {mean_prob:.4f} (المثالي: 0.5000)")
    print(f"   • الانحراف المعياري (Standard Deviation): {std_prob:.4f}")
    print(f"   • أدنى احتمالية رُصدت (Min):             {min_prob:.4f}")
    print(f"   • أقصى احتمالية رُصدت (Max):             {max_prob:.4f}")
    print(f"   • نسبة الامتثال لمعيار SAC (0.50 ± 0.05):  {compliance_rate:.1f}%")

    if compliance_rate >= 80.0:
        print("   • التقييم الأمني: ✓ ممتاز — انتشار البتات يحقق معايير الانهيار الصارم.")
    elif compliance_rate >= 60.0:
        print("   • التقييم الأمني: ⚠ مقبول — انتشار جيد مع بعض الفروقات المكانية الطفيفة.")
    else:
        print("   • التقييم الأمني: ✗ ضعيف — الشبكة لا تحقق خاصية الانهيار الصارم بالشكل الكافي.")

    # حفظ النتائج
    npy_path = output_dir / "sac_matrix.npy"
    png_path = output_dir / "sac_heatmap.png"

    np.save(npy_path, sac_matrix)
    plot_sac_heatmap(sac_matrix, png_path)

    print(f"\n[💾] تم حفظ مصفوفة SAC الرقمية في: {npy_path}")
    print(f"[📊] تم حفظ الخريطة الحرارية في: {png_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
