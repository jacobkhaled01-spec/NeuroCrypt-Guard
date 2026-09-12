# NeuroCrypt-Guard — Agent Control Protocol

## مسار المشروع: `d:\IT FILES\level 4\تشفير\عملي\مشروع\`

## الإصدار: v2.0 | تاريخ: 2026-09-12

---

## 📌 هوية المشروع (Project Identity)

```
الاسم:     NeuroCrypt-Guard
النوع:     Adversarial Neural Cryptography — Academic Research Project
المقرر:    مقرر التشفير (Cryptography) — المستوى الرابع
الجامعة:   جامعة إب — كلية الحاسوب وتكنولوجيا المعلومات
الفريق:    يعقوب خالد المهاجري | سليمان صالح العربي | مالك عادل جبران
```

---

## 🛑 القواعد الإلزامية (MUST FOLLOW — No Exceptions)

### 1. قواعد الملفات والمستودع

- **لا تحذف ولا تُعيد تسمية** أي ملف أو مجلد موجود بدون موافقة صريحة من المستخدم
- **حدّث `CHANGELOG.md`** بعد كل تغيير برمجي ذي معنى مع رقم إصدار `vX.Y.Z`
- **حدّث `task.md`** بعلامة `[x]` عند إتمام كل مهمة
- **الترميز دائماً `UTF-8`** مع دعم النص العربي والإنجليزي في جميع الملفات
- **حزمة `.agents/`** لا تُعدَّل تلقائياً إلا بطلب صريح من المستخدم

### 2. قواعد كتابة الكود (Coding Standards)

- **Docstrings إلزامية** لكل كلاس ودالة: اكتب بالعربية أولاً ثم الإنجليزي
- **Type Hints إلزامية** لجميع معاملات الدوال والقيم المُعادة
- **لا Magic Numbers** — كل قيمة ثابتة لها اسم بأحرف كبيرة: `KEY_SIZE = 16`
- **استخدم `pathlib.Path`** بدلاً من `os.path` لجميع مسارات الملفات
- **استخدم `logging`** بدلاً من `print()` في الكود الإنتاجي (الاستثناء: `train.py` تقدم التدريب)
- **لا Hardcoded paths** — جميع المسارات نسبية إلى جذر المشروع أو عبر `pathlib`

### 3. قواعد النماذج العصبية (Neural Models Rules)

- **الأبعاد الثابتة:** `N ∈ {16, 32, 64}` | `BATCH_SIZE = 256` | `LEARNING_RATE = 0.0008`
- **k-steps لإيف:** `EVE_STEPS_PER_AB = 2` (يمكن رفعه إلى 3 إذا لزم)
- **دالة الخسارة المقيدة (لا تُعدَّل):**
  ```python
  L_AB = L_Bob + ((max(0, 0.5 - L_Eve) / 0.5) ** 2)
  ```
- **معيار النجاح الأمني:**
  - `BER_Bob < 0.01` (1%)
  - `BER_Eve ∈ [0.42, 0.52]` (قريب من 50% — شانون)
  - `Secrecy Gap > 40%`

### 4. قواعد التوثيق الأكاديمي

- **جميع المراجع العلمية بنمط APA 7th Edition** في أي وثيقة أو كود أو تعليق
- **لا ادعاءات غير موثقة** — كل نتيجة رقمية مدعومة بمرجع أو تجربة قابلة للتكرار
- **احفظ النتائج العددية** في ملفات JSON أو CSV في `نتائج_التقييم/`

---

## 📁 هيكلية المشروع المعتمدة

```
مشروع/
├── src/                     ← الكود الأساسي (models/loss/train/evaluate + evaluators)
├── مجموعات_البيانات/         ← مولدات البيانات والنصوص
├── checkpoints/              ← أوزان النماذج (.pt files)
├── نتائج_التقييم/            ← مخرجات SAC/NIST/Fault/AES (.npy/.json/.png)
├── وثائق_المشروع/            ← حزمة الوثائق الهندسية الخمس
├── الأوراق_والدراسات/        ← التحليلات الأكاديمية للمراجع
├── dashboard/                ← Streamlit Dashboard
├── assets/                   ← الشعارات والصور
└── .agents/                  ← هذا الملف وملفات المهارات
```

---

## ⚡ تسلسل تنفيذ الكود (Execution Order)

```bash
# 1. توليد البيانات
python مجموعات_البيانات/csprng_generator.py

# 2. التدريب
python src/train.py --steps 5000 --batch_size 256 --n_bits 16 --k_eve 2

# 3. التقييم الأساسي
python src/evaluate.py --checkpoint checkpoints/best_alice.pt

# 4. فحوصات الأمان
python src/sac_eval.py
python src/nist_eval.py
python src/fault_injection.py
python src/aes_benchmark.py

# 5. لوحة التحكم
streamlit run dashboard/app.py
```

---

## 🔑 المتغيرات البيئية المطلوبة

```bash
# اختياري — لتفعيل CUDA إذا لم يُكتشف تلقائياً
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```
