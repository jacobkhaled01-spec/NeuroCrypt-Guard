# بطاقة دراسة: هجمات حقن الأخطاء واضطراب الأوزان (Fault-Injection & Bit-Flip Studies)

---

## 1. بيانات التوثيق الأكاديمي (APA 7)
* **الدراسة الأولى (الأصل التشفيري لحقن الأخطاء):**
  > Boneh, D., DeMillo, R. A., & Lipton, R. J. (1997). On the importance of checking cryptographic protocols for faults. In W. Fumy (Ed.), *Advances in Cryptology — EUROCRYPT '97* (Lecture Notes in Computer Science, Vol. 1233, pp. 37–51). Springer. https://doi.org/10.1007/3-540-69053-0_4
* **الدراسة الثانية (هجمات قلب البتات في الشبكات العصبية):**
  > Rakin, A. S., He, Z., & Fan, D. (2019). Bit-flip attack: Crushing neural networks with progressive bit search. In *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)* (pp. 1211–1220). https://doi.org/10.1109/ICCV.2019.00130

---

## 2. المفاهيم الأساسية لهجمات حقن الأخطاء
* **في التشفير الكلاسيكي (Classical Fault Analysis):**
  * إحداث خطأ مقصود في العتاد أثناء تنفيذ دورات التشفير (عبر ومضات ليزر أو تذبذب الجهد الكهربائي) يؤدي إلى إنتاج نص مشفر تالف جزئياً.
  * بمقارنة النص المشفر السليم مع النص المشفر المعيوب، يمكن استخراج المفتاح السري في خطوات محدودة.
* **في الشبكات العصبية (Adversarial Weight Perturbation):**
  * تؤدي هجمات حقن الأخطاء (مثل استغلال ثغرة Rowhammer في ذاكرة DRAM) إلى قلب بتات محددة في مصفوفات أوزان الطبقات، مما قد يدمر قدرة بوب على فك التشفير أو يسرب مخرجات غير مشفرة لإيف.

---

## 3. تطبيق المفهوم في مشروعنا:
* سنقوم ببرمجة محاكاة برمجية لهجمات حقن الأخطاء:
  1. **حقن الضوضاء الغاوسية (Gaussian Noise Injection):** إضافة تشويش تدريجي للأوزان $\mathcal{N}(0, \sigma^2)$ ورصد متى ينهار النظام.
  2. **تصفير الأوزان الانتقائي (Weight Pruning / Zeroing):** تصفير نسبة من أوزان طبقات الالتفاف لمحاكاة تلف الذاكرة.
  3. **قياس عتبة التسامح مع الأخطاء (Fault Tolerance Threshold):** حساب أقصى نسبة تلف تحتفظ عندها الشبكة بالقدرة على فك التشفير الآمن.
