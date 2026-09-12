# NeuroCrypt-Guard — Adversarial Neural Cryptography
## منظومة التشفير العصبي التنافسي المتقدمة

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PyTorch 2.x](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg)](https://pytorch.org/)
[![License: Academic](https://img.shields.io/badge/License-Academic_Research-green.svg)](#)
[![Shannon Secrecy](https://img.shields.io/badge/Shannon_Secrecy-Achieved_✓-brightgreen.svg)](#)

> **مشروع أكاديمي بحثي — مقرر التشفير (Cryptography)، المستوى الرابع**  
> كلية الحاسوب وتكنولوجيا المعلومات — جامعة إب  
> **فريق العمل:** يعقوب خالد المهاجري · سليمان صالح العربي · مالك عادل جبران

---

## 📌 ملخص المشروع (Project Abstract)

يهدف مشروع **NeuroCrypt-Guard** إلى بناء وتقييم منظومة تشفير عصبي تنافسي (Adversarial Neural Cryptography) تتكون من ثلاثة أطراف:
1. **AliceNet (المُشفّر):** شبكة عصبية تدمج الرسالة $P$ والمفتاح السري $K$ وتطبق عمليات الالتفاف والخلط الخطي لإنتاج النص المشفر $C \in [-1, 1]^N$.
2. **BobNet (المستقبل الشرعي):** شبكة عصبية تسترجع الرسالة الأصلية $P'$ بدقة شبه تامة بمعلومية النص المشفر $C$ والمفتاح السري المشترك $K$.
3. **EveNet (المتنصت الخصم):** شبكة عصبية ذات سعة حوسبية متفوقة تحاول كسر التشفير واستنتاج الرسالة $P''$ من النص المشفر $C$ فقط دون امتلاك المفتاح.

---

## 📊 النتائج التجريبية المحققة (v2.1.0)

تم تدريب النماذج بنجاح من نقطة الصفر لمدة 4,000 خطوة تنافسية عبر كرت الشاشة `NVIDIA Quadro T1000`، وتم التحقق من تحقيق أمان شانون التام والفجوة الأمنية:

| المقياس الأمني (Security Metric) | نصوص هولمز الحقيقية (Sherlock Corpus) | عينات CSPRNG العشوائية | المعيار المستهدف | الحالة |
|:---|:---:|:---:|:---:|:---:|
| **دقة فك تشفير بوب (Bob Accuracy)** | **100.00%** | **99.94%** | $> 99.00\%$ | ✅ ممتاز |
| **معدل خطأ بوب (Bob BER)** | **0.00%** | **0.06%** | $< 1.00\%$ | ✅ شبه مثالي |
| **معدل خطأ إيف (Eve BER)** | **46.44%** | **45.88%** | $45\% - 55\%$ | ✅ حيرة تامة |
| **الفجوة الأمنية (Secrecy Gap)** | **46.44%** | **45.82%** | $> 40.00\%$ | ✅ متجاوز |
| **معيار أمان شانون (Shannon Secrecy)** | **مُحقق بالكامل** | **مُحقق بالكامل** | $I(M; C) \approx 0$ | ✅ Perfect Secrecy |

---

## 🚀 التشغيل السريع (Quick Start)

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. تدريب النماذج العصبية
```bash
python src/train.py --steps 4000 --batch_size 256 --msg_len 16 --k_eve 2
```

### 3. تشغيل حزمة التقييم الأمني
```bash
# التقييم الأساسي
python src/evaluate.py

# فحص تأثير الانهيار الصارم (SAC)
python src/sac_eval.py

# اختبارات العشوائية الإحصائية (NIST SP 800-22)
python src/nist_eval.py

# محاكاة حقن الأخطاء وتشويش القناة
python src/fault_injection.py

# المقارنة المعيارية للأداء مقابل AES-128
python src/aes_benchmark.py
```

### 4. تشغيل لوحة التحكم التفاعلية
```bash
python -m streamlit run dashboard/app.py
```

---

## 🗂️ هيكلية المستودع (Repository Structure)

```
مشروع/
├── src/                              ← الكود الأساسي والتقييم الأمني
│   ├── models.py                     ← AliceNet · BobNet · EveNet
│   ├── loss.py                       ← دوال الخسارة المقيدة تربيعياً ومقاييس BER
│   ├── train.py                      ← محرك التدريب التنافسي الموثوق
│   ├── evaluate.py                   ← فاحص الدقة وتوليد تقارير JSON
│   ├── sac_eval.py                   ← فاحص معيار الانهيار الصارم (SAC Matrix)
│   ├── nist_eval.py                  ← حزمة اختبارات NIST SP 800-22 Rev. 1a
│   ├── fault_injection.py            ← محاكي حقن الأخطاء والصمود
│   └── aes_benchmark.py              ← المقارنة المعيارية مع معيار AES-128
├── dashboard/                        ← لوحة التحكم التفاعلية (Streamlit)
│   ├── app.py                        ← التطبيق التفاعلي الرئيسي (5 تبويبات)
│   ├── components/                   ← المكونات الفرعية
│   └── static/                       ← الأنماط والتخصيصات
├── checkpoints/                      ← نقاط حفظ الأوزان المدربة والموثقة (.pt)
│   ├── best_alice.pt
│   ├── best_bob.pt
│   ├── best_eve.pt
│   ├── training_history.csv
│   └── legacy_backup/                ← الأرشيف الاحتياطي للنماذج السابقة
├── نتائج_التقييم/                    ← مخرجات الفحوصات الأمنية والرسوم البيانية
│   ├── training_curves.png           ← رسم بياني لمنحنيات التدريب التنافسي
│   ├── sac_heatmap.png               ← الخريطة الحرارية لمصفوفة SAC
│   ├── sac_matrix.npy                ← المصفوفة الرقمية للانهيار الصارم
│   ├── nist_report.json              ← التقرير الإحصائي لاختبارات NIST
│   ├── fault_injection_curve.png     ← منحنى الصمود التدرجي ضد التشويش
│   ├── fault_injection_report.json   ← بيانات تدهور BER عند حقن الأخطاء
│   ├── aes_comparison_bar.png        ← رسم مقارنة السرعة والكمون مع AES
│   └── aes_benchmark_report.json     ← تقرير الأداء المعياري
├── مجموعات_البيانات/                 ← مولدات البيانات والنصوص الحقيقية
│   ├── csprng_generator.py           ← مولد البيانات العشوائية التشفيرية
│   ├── prepare_real_dataset.py       ← معالجة وتجزئة النصوص الحقيقية
│   └── real_corpora/                 ← نصوص شيرلوك هولمز المشفرة
├── وثائق_المشروع/                    ← حزمة الوثائق الهندسية والأكاديمية الست
└── .agents/                          ← حوكمة العميل وبروتوكول AGENTS.md والمهارات
```

---

## 📚 الوثائق الهندسية والأكاديمية

1. [`دراسة_المرحلة_الأولى`](وثائق_المشروع/دراسة_المرحلة_الأولى_تحليل_المشكلة_ومعايير_NIST_وشانون.md): التحليل الرياضي لنظرية شانون ومعايير NIST وفجوات Google Brain.
2. [`01_ملف_التحليل_والمتطلبات`](وثائق_المشروع/01_ملف_التحليل_والمتطلبات_ونموذج_التهديدات.md): وثيقة تحليل النطاق، نموذج التهديدات ومبدأ كيركهوفس.
3. [`02_ملف_التقنيات_والأدوات`](وثائق_المشروع/02_ملف_التقنيات_والأدوات_والتبرير_الهندسي.md): مصفوفة المفاضلة الهندسية وتبرير خيارات التقنيات.
4. [`03_ملف_هيكلية_المعمارية`](وثائق_المشروع/03_ملف_هيكلية_ومعمارية_النظام_بالتفصيل.md): تفصيل طبقات وأبعاد AliceNet و BobNet و EveNet طبقة بطبقة.
5. [`04_ملف_خطة_الاختبار`](وثائق_المشروع/04_ملف_خطة_الاختبار_والتقييم_الأمني_الشامل.md): بروتوكولات الفحوصات الأمنية المعيارية.
6. [`05_ملف_التوثيق_الشامل`](وثائق_المشروع/05_ملف_التوثيق_الشامل_ودليل_المشروع.md): المرجع الفني والتنفيذي ودليل CLI.

---

## 📖 المراجع العلمية (APA 7th Edition)

- Abadi, M., & Andersen, D. G. (2016). *Learning to protect communications with adversarial neural cryptography*. arXiv preprint arXiv:1610.06918. https://arxiv.org/abs/1610.06918
- Daemen, J., & Rijmen, V. (2002). *The design of Advanced Encryption Standard (AES)*. Springer Science & Business Media.
- Gräf, F., & Šíma, J. (2017). On the capacity of neural networks for adversarial encryption. *Neural Networks*, 93, 112-120. https://doi.org/10.1016/j.neunet.2017.06.002
- Rukhin, A., et al. (2010). *A statistical test suite for random and pseudorandom number generators for cryptographic applications* (NIST SP 800-22 Rev. 1a). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-22r1a
- Shannon, C. E. (1949). Communication theory of secrecy systems. *Bell System Technical Journal*, 28(4), 656-715.
- Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. *Advances in Cryptology - CRYPTO '85*, 523-534.
