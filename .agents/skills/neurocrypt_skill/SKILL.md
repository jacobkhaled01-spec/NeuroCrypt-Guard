---
name: neurocrypt-dev
description: >
  مهارة متخصصة لتطوير مشروع NeuroCrypt-Guard. استخدمها عند:
  - بناء أو تعديل الشبكات العصبية (AliceNet / BobNet / EveNet)
  - كتابة سكريبتات التقييم الأمني (SAC / NIST / Fault Injection / AES)
  - تطوير لوحة التحكم Streamlit Dashboard
  - كتابة أو مراجعة الوثائق الهندسية والأكاديمية
  - تشخيص مشاكل التدريب أو الأداء
---

## 🎯 هوية المشروع التقنية

| البند | القيمة |
|:------|:-------|
| **مسار الجذر** | `d:\IT FILES\level 4\تشفير\عملي\مشروع\` |
| **Python** | 3.11 |
| **Framework** | PyTorch 2.x + CUDA (NVIDIA Quadro T1000, 4GB VRAM) |
| **OS** | Windows 11 |
| **N_BITS** | 16 (الأساسي)، 32، 64 (موسع) |
| **BATCH_SIZE** | 256 |
| **LEARNING_RATE** | 0.0008 |
| **EVE_STEPS_PER_AB** | 2 (k-steps) |

---

## 🏗️ معمارية الشبكات العصبية

### AliceNet (المُشفِّر):
```
Input: [P: (B, N)] + [K: (B, N)] → Concat → (B, 2N)
FC(2N→2N) + LeakyReLU(0.2)
→ Reshape (B, 1, 2N)
→ Conv1D(1→32, kernel=4, same) + LeakyReLU
→ Conv1D(32→32, kernel=2, same) + LeakyReLU
→ Conv1D(32→1, kernel=1, same)
→ Squeeze (B, 2N)
→ FC(2N→N) + Tanh
Output: C ∈ [-1, 1]^N
```

### BobNet (فاك التشفير الشرعي):
```
Input: [C: (B, N)] + [K: (B, N)] → معمارية مطابقة لـ AliceNet
Output: P' ∈ [-1, 1]^N (يُقرَّب لـ {-1, 1})
```

### EveNet (المتنصت الخصم — سعة مضاعفة):
```
Input: [C: (B, N)] فقط (لا مفتاح)
FC(N→2N) + LeakyReLU
→ Conv1D(1→64, kernel=4) + LeakyReLU   ← 64 قناة بدل 32
→ Conv1D(64→64, kernel=2) + LeakyReLU
→ Conv1D(64→32, kernel=2) + LeakyReLU  ← طبقة إضافية
→ Conv1D(32→1, kernel=1)
→ FC(2N→N) + Tanh
Output: P'' ∈ [-1, 1]^N
```

---

## ⚖️ دالة الخسارة المقيدة (لا تُعدَّل أبداً)

```python
# مسافة L1 المقيسة (Normalized L1 Distance)
L_Bob = torch.mean(torch.abs(P - P_bob)) / 2.0   # ∈ [0, 1]
L_Eve = torch.mean(torch.abs(P - P_eve)) / 2.0   # ∈ [0, 1]

# دالة خسارة أليس وبوب المشروطة (Bounded Quadratic Penalty)
penalty = torch.clamp(0.5 - L_Eve, min=0.0) / 0.5
L_AB = L_Bob + (penalty ** 2)

# دالة خسارة إيف (مستقلة)
L_Eve_standalone = L_Eve  # تُحسَّن بشكل مستقل
```

**الخواص الحرجة:**
- عندما `L_Eve ≥ 0.5` → العقوبة = 0 → أليس تركز على تقليل `L_Bob` فقط ✓
- عندما `L_Eve < 0.5` → عقوبة تربيعية → أليس تُجبر على تغيير التشفير ✓
- لا يمكن لأليس الاستفادة من قلب البتات (السرية المعكوسة) ✓

---

## 📊 معايير النجاح الأمني

```
BER_Bob  < 1.0%  ← دقة فك التشفير (محقق: 0.28%)
BER_Eve  ∈ [42%, 52%] ← شرط شانون للأمان التام
Secrecy Gap > 40% ← الفجوة = BER_Eve - BER_Bob (محقق: 43.29%)

NIST SP 800-22: P-value ≥ 0.01 لجميع الاختبارات الـ 15
SAC Matrix: D[i,j] ∈ [0.45, 0.55] لجميع خلايا 16×16
Fault Tolerance: BER_Bob < 5% عند σ = 0.02
```

---

## 📁 الملفات الرئيسية وأدوارها

| الملف | الدور | الحالة |
|:---|:---|:---:|
| `src/models.py` | AliceNet, BobNet, EveNet | ✅ v1 |
| `src/loss.py` | دوال الخسارة المقيدة + BER metric | ✅ v1 |
| `src/train.py` | محرك التدريب التنافسي k-steps | ✅ v1 |
| `src/evaluate.py` | تقييم BER + Secrecy Gap | ✅ v1 |
| `src/sac_eval.py` | مصفوفة الانهيار الصارم 16×16 | ❌ يجب البناء |
| `src/nist_eval.py` | حزمة اختبارات NIST SP 800-22 | ❌ يجب البناء |
| `src/fault_injection.py` | محاكاة حقن الأخطاء والتشويش | ❌ يجب البناء |
| `src/aes_benchmark.py` | مقارنة مع AES-128-CBC | ❌ يجب البناء |
| `dashboard/app.py` | لوحة التحكم التفاعلية | ❌ يجب البناء |
| `checkpoints/best_alice.pt` | أوزان النموذج الأفضل | ✅ موجود |

---

## ⚠️ نقاط حرجة يجب مراعاتها

1. **ثغرة BER_Eve الحالية (56.43%):** أعلى قليلاً من 50% — يجب ضبط `γ` في دالة الخسارة أو زيادة k-steps إلى 3
2. **مشكلة LFSR لـ NIST:** الاختبار #10 (Linear Complexity) يتطلب `n ≥ 10⁶` بت — تأكد من توليد عدد كافٍ من الكتل
3. **توافق Seaborn مع Streamlit:** استخدم `plt.close()` بعد كل رسم في Dashboard لتجنب تراكم الأشكال
4. **الحفظ التلقائي:** احفظ نقطة تحقق كل 500 خطوة تدريب في `checkpoints/`
5. **JSON Encoding للعربية:** استخدم `ensure_ascii=False` عند حفظ ملفات JSON

---

## 📚 المراجع الأساسية (APA 7th Edition)

- Abadi, M., & Andersen, D. G. (2016). *Learning to protect communications with adversarial neural cryptography*. arXiv:1610.06918.
- Rukhin, A., et al. (2010). *NIST Special Publication 800-22, Rev. 1a*. https://doi.org/10.6028/NIST.SP.800-22r1a
- Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. *CRYPTO '85*, LNCS 218, 523–534.
- Shannon, C. E. (1949). Communication theory of secrecy systems. *Bell System Technical Journal*, 28(4), 656–715.
- Gräf, J., & Šíma, J. (2017). *Analysis and cracking of adversarial neural cryptography*. arXiv:1705.03458.
