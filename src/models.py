#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
models.py
المعمارية العصبية التنافسية لمنظومة NeuroCrypt-Guard
Adversarial Neural Cryptography Architectures (AliceNet, BobNet, EveNet)

المراجع العلمية المعتمدة (APA 7th Edition):
- Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with
  adversarial neural cryptography. arXiv preprint arXiv:1610.06918.
- Gräf, F., & Šíma, J. (2017). On the capacity of neural networks for adversarial encryption.
  Neural Networks, 93, 112-120. https://doi.org/10.1016/j.neunet.2017.06.002
- Shannon, C. E. (1949). Communication theory of secrecy systems.
  Bell System Technical Journal, 28(4), 656-715.
"""

from typing import Optional
import torch
import torch.nn as nn

# الثوابت المعمارية المعتمدة (No Magic Numbers)
DEFAULT_MESSAGE_SIZE: int = 16
DEFAULT_KEY_SIZE: int = 16
LEAKY_RELU_SLOPE: float = 0.2
STANDARD_CHANNELS: int = 32
EVE_EXPANDED_CHANNELS: int = 48


class AliceNet(nn.Module):
    """
    شبكة Alice (المُشفّر - Encryption Agent):
    تستقبل الرسالة P والمفتاح السري K، وتطبق الخلط الخطي (Confusion) والالتفاف المكاني (Diffusion)
    لإنتاج النص المشفر C في الفضاء المتصل [-1.0, 1.0]^N.
    
    Transforms (P, K) into ciphertext C using 1D convolutional layers with residual-free diffusion.
    """

    def __init__(self, message_size: int = DEFAULT_MESSAGE_SIZE, key_size: int = DEFAULT_KEY_SIZE) -> None:
        super(AliceNet, self).__init__()
        self.message_size = message_size
        self.key_size = key_size
        total_input = message_size + key_size

        # 1. طبقة الخلط الخطي الشامل (Full Linear Mixing for Confusion)
        self.fc_mix = nn.Linear(total_input, 2 * message_size)
        self.act1 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        # 2. طبقات الالتفاف أحادية البعد (1D-CNN for Spatial Diffusion)
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=STANDARD_CHANNELS, kernel_size=4, stride=1, padding="same")
        self.act2 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv2 = nn.Conv1d(in_channels=STANDARD_CHANNELS, out_channels=STANDARD_CHANNELS, kernel_size=2, stride=1, padding="same")
        self.act3 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv3 = nn.Conv1d(in_channels=STANDARD_CHANNELS, out_channels=1, kernel_size=1, stride=1, padding="same")

        # 3. طبقة الإسقاط والتنشيط النهائي لإنتاج النص المشفر
        self.fc_out = nn.Linear(2 * message_size, message_size)
        self.tanh = nn.Tanh()

    def forward(self, message: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
        """
        التمرير الأمامي للتشفير: C = Alice(P, K)
        Forward pass for Alice encryption.
        """
        x = torch.cat([message, key], dim=-1)
        x = self.act1(self.fc_mix(x))

        x = x.unsqueeze(1)  # (Batch, 1, 2*N)
        x = self.act2(self.conv1(x))
        x = self.act3(self.conv2(x))
        x = self.conv3(x)

        x = x.squeeze(1)  # (Batch, 2*N)
        ciphertext = self.tanh(self.fc_out(x))  # (Batch, N)
        return ciphertext


class BobNet(nn.Module):
    """
    شبكة Bob (فاك التشفير الشرعي - Authorized Decryption Agent):
    تستقبل النص المشفر C والمفتاح السري المشترك K لاستعادة الرسالة الأصلية P'.
    
    Transforms (C, K) into reconstructed plaintext P' with minimal bit error rate.
    """

    def __init__(self, message_size: int = DEFAULT_MESSAGE_SIZE, key_size: int = DEFAULT_KEY_SIZE) -> None:
        super(BobNet, self).__init__()
        self.message_size = message_size
        self.key_size = key_size
        total_input = message_size + key_size

        # 1. طبقة الخلط الخطي الشامل
        self.fc_mix = nn.Linear(total_input, 2 * message_size)
        self.act1 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        # 2. طبقات الالتفاف أحادية البعد
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=STANDARD_CHANNELS, kernel_size=4, stride=1, padding="same")
        self.act2 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv2 = nn.Conv1d(in_channels=STANDARD_CHANNELS, out_channels=STANDARD_CHANNELS, kernel_size=2, stride=1, padding="same")
        self.act3 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv3 = nn.Conv1d(in_channels=STANDARD_CHANNELS, out_channels=1, kernel_size=1, stride=1, padding="same")

        # 3. طبقة الاسترجاع والتنشيط النهائي
        self.fc_out = nn.Linear(2 * message_size, message_size)
        self.tanh = nn.Tanh()

    def forward(self, ciphertext: torch.Tensor, key: torch.Tensor) -> torch.Tensor:
        """
        التمرير الأمامي لفك التشفير الشرعي: P' = Bob(C, K)
        Forward pass for Bob decryption.
        """
        x = torch.cat([ciphertext, key], dim=-1)
        x = self.act1(self.fc_mix(x))

        x = x.unsqueeze(1)
        x = self.act2(self.conv1(x))
        x = self.act3(self.conv2(x))
        x = self.conv3(x)

        x = x.squeeze(1)
        decrypted = self.tanh(self.fc_out(x))
        return decrypted


class EveNet(nn.Module):
    """
    شبكة Eve (المتنصت الخصم - Adversarial Eavesdropper):
    تستقبل النص المشفر C فقط (دون المفتاح K) في محاولة لاستنتاج الرسالة الأصلية P''.
    تتمتع بسعة حوسبية متفوقة (48 قناة) لتمثيل الخصم الأمثل وفق Gräf & Šíma (2017).
    
    Attempts to predict P'' from ciphertext C alone without access to key K.
    """

    def __init__(self, message_size: int = DEFAULT_MESSAGE_SIZE) -> None:
        super(EveNet, self).__init__()
        self.message_size = message_size

        # توسيع سعة الدخل (N -> 2*N) لتمكين إيف من كشف الارتباطات
        self.fc_expand = nn.Linear(message_size, 2 * message_size)
        self.act1 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        # قنوات أوسع (48 قناة) لنمذجة الخصم الأقوى
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=EVE_EXPANDED_CHANNELS, kernel_size=4, stride=1, padding="same")
        self.act2 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv2 = nn.Conv1d(in_channels=EVE_EXPANDED_CHANNELS, out_channels=EVE_EXPANDED_CHANNELS, kernel_size=2, stride=1, padding="same")
        self.act3 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv3 = nn.Conv1d(in_channels=EVE_EXPANDED_CHANNELS, out_channels=1, kernel_size=1, stride=1, padding="same")

        self.fc_out = nn.Linear(2 * message_size, message_size)
        self.tanh = nn.Tanh()

    def forward(self, ciphertext: torch.Tensor) -> torch.Tensor:
        """
        التمرير الأمامي لمحاولة كسر التشفير: P'' = Eve(C)
        Forward pass for Eve eavesdropping.
        """
        x = self.act1(self.fc_expand(ciphertext))

        x = x.unsqueeze(1)
        x = self.act2(self.conv1(x))
        x = self.act3(self.conv2(x))
        x = self.conv3(x)

        x = x.squeeze(1)
        eavesdropped = self.tanh(self.fc_out(x))
        return eavesdropped


class DeepEveNet(nn.Module):
    """
    شبكة Deep Eve (المتنصت فائق السعة والعمق - Over-Parameterized Deep Adversary):
    تتضمن 4 طبقات التفافية مع 64 قناة ووصلات متبقية (Residual Connections) لنمذجة
    أعتى هجمات كسر التشفير وفق متطلبات مراجعي مجلات Q1 (IEEE TIFS / ACM CCS).

    Deep, over-parameterized eavesdropper with residual connections and 64 channels
    designed for rigorous cryptanalytic stress testing in Q1 academic benchmarks.
    """

    def __init__(self, message_size: int = DEFAULT_MESSAGE_SIZE, channels: int = 64) -> None:
        super(DeepEveNet, self).__init__()
        self.message_size = message_size
        self.channels = channels

        self.fc_in = nn.Linear(message_size, 2 * message_size)
        self.act1 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv1 = nn.Conv1d(in_channels=1, out_channels=channels, kernel_size=4, stride=1, padding="same")
        self.act2 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv2 = nn.Conv1d(in_channels=channels, out_channels=channels, kernel_size=3, stride=1, padding="same")
        self.act3 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv3 = nn.Conv1d(in_channels=channels, out_channels=channels, kernel_size=3, stride=1, padding="same")
        self.act4 = nn.LeakyReLU(LEAKY_RELU_SLOPE)

        self.conv4 = nn.Conv1d(in_channels=channels, out_channels=1, kernel_size=1, stride=1, padding="same")

        self.fc_out = nn.Linear(2 * message_size, message_size)
        self.tanh = nn.Tanh()

    def forward(self, ciphertext: torch.Tensor) -> torch.Tensor:
        """
        التمرير الأمامي للمتنصت العميق: P''' = DeepEve(C)
        Forward pass for deep adversary decryption attempt.
        """
        x = self.act1(self.fc_in(ciphertext))
        x = x.unsqueeze(1)  # (Batch, 1, 2*N)

        c1 = self.act2(self.conv1(x))
        c2 = self.act3(self.conv2(c1)) + c1  # Residual Connection
        c3 = self.act4(self.conv3(c2)) + c2  # Residual Connection
        out = self.conv4(c3)

        out = out.squeeze(1)
        return self.tanh(self.fc_out(out))

