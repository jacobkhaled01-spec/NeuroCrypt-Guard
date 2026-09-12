# دليل مجلد مجموعات البيانات وأدوات التوليد (Datasets & Data Generators)

يحتوي هذا المجلد على الأدوات ومجموعات البيانات المستخدمة في تدريب واختبار منظومة **NeuroCrypt-Guard**.

---

## 📂 محتويات المجلد:

1. **[`csprng_generator.py`](file:///d:/IT%20FILES/level%204/تشفير/عملي/مشروع/مجموعات_البيانات/csprng_generator.py):**
   * سكربت بايثون مستقل لتوليد دفقات بتات عشوائية آمنة تشفيرياً (*Cryptographically Secure Pseudo-Random Number Generator*).
   * يولد أزواج الرسائل والمفاتيح بتنسيق ثنائي متوازن $\{-1, 1\}$ متوافق مع PyTorch ونموذج Google Brain.
   * يدعم تصدير ملفات بتات ضخمة ($10^6$ بت) متوافقة مع متطلبات فحص **NIST SP 800-22**.

2. **[`plaintext_redundancy_sample.txt`](file:///d:/IT%20FILES/level%204/تشفير/عملي/مشروع/مجموعات_البيانات/plaintext_redundancy_sample.txt):**
   * عينة نصوص طبيعية باللغتين العربية والإنجليزية ذات تكرارات إحصائية معروفة.
   * تُستخدم لاختبار قدرة التشفير العصبي على إخفاء التكرارات اللغوية ومقارنتها بسلوك أنماط التشفير القياسية (مثل AES-ECB مقابل AES-CBC).

---

## 🚀 كيفية استخدام المولد:
لتوليد عينة بيانات تدريب أو اختبار:
```bash
python csprng_generator.py --num_samples 10000 --msg_len 16 --key_len 16 --output train_data.pt
```
أو لتوليد ملف بتات لاختبارات NIST:
```bash
python csprng_generator.py --mode nist --total_bits 1000000 --output nist_stream.bin
```
