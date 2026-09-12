# بطاقة معيار: حزمة اختبارات العشوائية NIST SP 800-22 Rev. 1a

---

## 1. بيانات التوثيق الأكاديمي (APA 7)
* **المؤلفون:** Andrew Rukhin, Juan Soto, James Nechvatal, Miles Smid, Elaine Barker, Stefan Leigh, Mark Levenson, Mark Vangel, David Banks, Alan Heckert, James Dray, & San Vo
* **سنة النشر:** 2010
* **عنوان الوثيقة:** *A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications*
* **الجهة المصدرة:** National Institute of Standards and Technology (NIST Special Publication 800-22, Rev. 1a)
* **رابط الوصول المباشر:** https://doi.org/10.6028/NIST.SP.800-22r1a

---

## 2. أهمية المعيار في التشفير
* يُعد هذا المعيار المرجع العالمي الأهم لاختبار ما إذا كانت السلاسل الثنائية الناتجة عن خوارزميات التشفير ومولدات الأرقام شبه العشوائية (PRNGs) تظهر سلوكاً عشوائياً إحصائياً غير قابل للتنبؤ.
* يتكون المعيار من **15 اختباراً إحصائياً** رئيسياً، أبرزها:
  1. **Monobit Frequency Test:** فحص نسبة الآحاد والأصفار في السلسلة (يجب أن تكون 50%).
  2. **Frequency Test within a Block:** فحص توازن البتات داخل كتل محددة الطول.
  3. **Runs Test:** فحص التغير المتتابع بين الآحاد والأصفار للتأكد من عدم وجود تكتلات.
  4. **Discrete Fourier Transform (Spectral) Test:** فحص الأنماط الدورية الخفية في السلسلة عبر تحويل فورييه.
  5. **Non-overlapping Template Matching Test:** فحص عدم تكرار أنماط بتات محددة مسبقاً.

---

## 3. معيار القبول والنجاح الإحصائي ($P\text{-value}$)
* يحدد المعيار مستوى الدلالة الإحصائية عند $\alpha = 0.01$.
* **شرط النجاح:** إذا كانت قيمة $P\text{-value} \ge 0.01$، يُعتبر التسلسل عشوائياً بالكامل واجتاز الاختبار. أما إذا كانت $P\text{-value} < 0.01$، فيُعتبر التسلسل غير عشوائي ويحمل نمطاً إحصائياً يفشل التشفير.

---

## 4. تطبيق المعيار في مشروعنا:
* سنقوم بجمع نصوص أليس المشفرة بحجم إجمالي يصل إلى $10^6$ بت وتمريرها عبر حزمة NIST للتأكد من اجتيازها لهذه الاختبارات، ومقارنة نسب النجاح مع خوارزمية AES-128.
