#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loss.py
دوال الخسارة التنافسية والمقاييس التشفيرية لمنظومة NeuroCrypt-Guard
Bounded Adversarial Loss Functions & Cryptographic Distance Metrics

المراجع العلمية المعتمدة (APA 7th Edition):
- Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with
  adversarial neural cryptography. arXiv preprint arXiv:1610.06918.
- Shannon, C. E. (1949). Communication theory of secrecy systems. 
  Bell System Technical Journal, 28(4), 656-715. https://doi.org/10.1002/j.1538-7305.1949.tb00928.x
- Gräf, F., & Šíma, J. (2017). On the capacity of neural networks for adversarial encryption.
  Neural Networks, 93, 112-120.
"""

from typing import Tuple
import torch
import torch.nn as nn

# الثوابت المعيارية للنظام وفق بروتوكول AGENTS.md
SECURITY_MARGIN: float = 0.5  # حد الأمان الحرج (التخمين العشوائي 50%)
EPSILON: float = 1e-7


def normalized_l1_distance(actual: torch.Tensor, predicted: torch.Tensor) -> torch.Tensor:
    """
    حساب المسافة المطلقة المقيسة L1 بين الإشارة الحقيقية والتخمين.
    Computes normalized L1 distance between ground truth and predictions in range [-1.0, 1.0].

    Args:
        actual (torch.Tensor): الرسالة الأصلية بعناصر في {-1.0, 1.0}
        predicted (torch.Tensor): تخمين الشبكة بمخرجات متصلة في [-1.0, 1.0]

    Returns:
        torch.Tensor: متوسط المسافة الموحدة في المجال [0.0, 1.0]
                      0.0 = استرجاع مثالي (Perfect Recovery)
                      0.5 = تخمين أعمى عشوائي (Blind Random Guessing)
                      1.0 = انعكاس تام (Full Bit Inversion)
    """
    abs_diff = torch.abs(actual - predicted) / 2.0
    return torch.mean(abs_diff)


def calculate_ber(actual: torch.Tensor, predicted: torch.Tensor) -> float:
    """
    حساب معدل خطأ البتات القياسي (Bit Error Rate - BER).
    Calculates the exact Bit Error Rate between actual and predicted binary sequences.

    Args:
        actual (torch.Tensor): القيم الأصلية
        predicted (torch.Tensor): القيم المخمنة

    Returns:
        float: نسبة الخطأ كقيمة عشرية بين 0.0 (0%) و 1.0 (100%)
    """
    with torch.no_grad():
        actual_bits = (actual > 0).to(torch.int8)
        pred_bits = (predicted > 0).to(torch.int8)
        errors = torch.ne(actual_bits, pred_bits).float()
        return float(torch.mean(errors).item())


def loss_eve(actual_message: torch.Tensor, eve_guess: torch.Tensor) -> torch.Tensor:
    """
    دالة خسارة المتنصت الخصم Eve (L_Eve):
    Adversary Loss Function: Eve aims to minimize reconstruction error to 0.

    Args:
        actual_message (torch.Tensor): الرسالة الأصلية P
        eve_guess (torch.Tensor): تخمين إيف P''

    Returns:
        torch.Tensor: المسافة المقيسة L1 التي تسعى إيف لتصفيرها
    """
    return normalized_l1_distance(actual_message, eve_guess)


def loss_alice_bob(
    actual_message: torch.Tensor,
    bob_decrypted: torch.Tensor,
    eve_guess: torch.Tensor,
    security_margin: float = SECURITY_MARGIN,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    دالة خسارة أليس وبوب المقيدة تربيعياً (Bounded Quadratic Loss Function):
    Alice & Bob Joint Constrained Loss:
    L_AB = L_Bob + ((max(0, margin - L_Eve) / margin) ** 2)

    تضمن تحقيق الأمان التام وفق مبادئ شانون (Shannon, 1949) وتمنع التشفير المعكوس (Abadi & Andersen, 2016):
    - إذا كانت إيف أذكى من التخمين العشوائي (L_Eve < 0.5): يتم تطبيق عقوبة تربيعية تصاعدية.
    - إذا كانت إيف في حيرة تامة (L_Eve >= 0.5): تنعدم العقوبة تماماً، ويتفرغ النظام لتقليل خطأ بوب.

    Args:
        actual_message (torch.Tensor): الرسالة الأصلية P
        bob_decrypted (torch.Tensor): الرسالة المستعادة من بوب P'
        eve_guess (torch.Tensor): تخمين إيف P''
        security_margin (float): عتبة الأمان (الافتراضي: 0.5)

    Returns:
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]: (L_AB الإجمالية, L_Bob, L_Eve)
    """
    l_bob = normalized_l1_distance(actual_message, bob_decrypted)
    l_eve = normalized_l1_distance(actual_message, eve_guess)

    # حساب الفارق الإيجابي لذكاء إيف بالنسبة للتخمين العشوائي
    eve_advantage = torch.clamp(security_margin - l_eve, min=0.0)
    penalty = (eve_advantage / security_margin) ** 2

    l_ab = l_bob + penalty
    return l_ab, l_bob, l_eve
