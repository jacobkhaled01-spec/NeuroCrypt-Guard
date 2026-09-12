#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_exact_proposal.py
أداة بناء وتصدير مقترح المشروع النهائي (PDF + Word + LaTeX)
مطابق 100% لقالب جامعة إب - كلية الحاسبات وتقنية المعلومات
"""

import os
import sys
import base64
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# قراءة الشعارات الشفافة الأصلية بصيغة Base64
with open(os.path.join(ASSETS_DIR, "logo_ibb_clean.png"), "rb") as f:
    ibb_logo_b64 = base64.b64encode(f.read()).decode("utf-8")

with open(os.path.join(ASSETS_DIR, "logo_yemen_clean.png"), "rb") as f:
    yemen_logo_b64 = base64.b64encode(f.read()).decode("utf-8")

def generate_html():
    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>مقترح مشروع مقرر التشفير - NeuroCrypt-Guard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Amiri:ital,wght@0,400;0,700;1,400&family=Segoe+UI:wght@400;600;700&display=swap');

  @page {{
    size: A4 portrait;
    margin: 0;
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  body {{
    margin: 0;
    padding: 0;
    background-color: #f1f5f9;
    font-family: 'Cairo', 'Traditional Arabic', 'Segoe UI', Tahoma, sans-serif;
    color: #111827;
    line-height: 1.45;
  }}

  .page {{
    width: 210mm;
    height: 297mm;
    margin: 10px auto;
    background: #fff;
    padding: 8mm;
    page-break-after: always;
    page-break-inside: avoid;
    position: relative;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  }}

  @media print {{
    body {{
      background: none;
    }}
    .page {{
      margin: 0;
      box-shadow: none;
      width: 210mm;
      height: 297mm;
      padding: 8mm;
      page-break-after: always;
    }}
  }}

  /* الإطار المزدوج المطابق تماماً للقالب */
  .outer-border {{
    width: 100%;
    height: 100%;
    border: 1.2px solid #000;
    padding: 2.5px;
    position: relative;
  }}

  .inner-border {{
    width: 100%;
    height: 100%;
    border: 1.2px solid #000;
    padding: 10mm 13mm;
    position: relative;
    display: flex;
    flex-direction: column;
  }}

  /* الصفحة الأولى - الغلاف */
  .header-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }}

  .header-table td {{
    vertical-align: top;
    text-align: center;
    font-size: 11pt;
    font-weight: 600;
    line-height: 1.4;
  }}

  .logo-img {{
    height: 75px;
    margin-bottom: 6px;
    display: block;
    margin-left: auto;
    margin-right: auto;
  }}

  .cover-proposal-title {{
    text-align: center;
    color: #1e40af;
    font-size: 21pt;
    font-weight: 700;
    font-style: italic;
    margin-top: 45mm;
    margin-bottom: 25mm;
    font-family: 'Cairo', 'Segoe UI', sans-serif;
  }}

  .project-title-en-main {{
    font-size: 24pt;
    font-weight: 800;
    color: #1e40af;
    font-family: 'Segoe UI', Arial, sans-serif;
    text-align: left;
    direction: ltr;
    margin-bottom: 6px;
  }}

  .project-title-en-sub {{
    font-size: 13pt;
    font-weight: 700;
    color: #1e40af;
    font-family: 'Segoe UI', Arial, sans-serif;
    text-align: left;
    direction: ltr;
    line-height: 1.35;
    margin-bottom: 18px;
  }}

  .project-title-ar {{
    font-size: 13pt;
    font-weight: 700;
    color: #1e40af;
    text-align: center;
    line-height: 1.4;
  }}

  .cover-footer {{
    position: absolute;
    bottom: 10mm;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 12pt;
    font-weight: 700;
  }}

  /* الصفحات الداخلية */
  .section-h1 {{
    font-size: 13.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 0;
    margin-bottom: 6px;
    text-align: right;
  }}

  .section-title-en {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-weight: 700;
    font-size: 10.5pt;
    color: #0f172a;
    direction: ltr;
    text-align: left;
    margin-bottom: 3px;
  }}

  .section-title-ar {{
    font-weight: 700;
    font-size: 10.5pt;
    color: #0f172a;
    margin-bottom: 10px;
    text-align: right;
  }}

  p {{
    font-size: 9.6pt;
    text-align: justify;
    text-justify: inter-word;
    margin-top: 0;
    margin-bottom: 7px;
    line-height: 1.42;
  }}

  .sub-heading-blue {{
    font-size: 11pt;
    font-weight: 700;
    color: #0284c7;
    margin-top: 6px;
    margin-bottom: 4px;
  }}

  .bold-item {{
    font-weight: 700;
    font-size: 9.6pt;
  }}

  ul {{
    margin-top: 2px;
    margin-bottom: 6px;
    padding-right: 20px;
  }}

  li {{
    font-size: 9.4pt;
    margin-bottom: 3px;
    line-height: 1.4;
  }}

  /* الجداول */
  table.custom-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 6px;
    margin-bottom: 10px;
    font-size: 9pt;
  }}

  table.custom-table th {{
    background-color: #1f4e79;
    color: #ffffff;
    padding: 6px 8px;
    font-weight: 700;
    border: 1px solid #1f4e79;
    text-align: center;
  }}

  table.custom-table td {{
    border: 1px solid #cbd5e1;
    padding: 5px 7px;
    vertical-align: middle;
  }}

  /* جدول جانت */
  table.gantt-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    margin-bottom: 16px;
    font-size: 8.5pt;
  }}

  table.gantt-table th {{
    background-color: #1f4e79;
    color: #fff;
    border: 1px solid #334155;
    padding: 5px 2px;
    text-align: center;
    font-weight: 700;
    white-space: nowrap;
  }}

  table.gantt-table td {{
    border: 1px solid #94a3b8;
    padding: 5px 2px;
    text-align: center;
    height: 22px;
  }}

  table.gantt-table td.task-name {{
    text-align: right;
    padding-right: 6px;
    font-weight: 600;
    font-size: 8.2pt;
    white-space: normal;
  }}

  .active-phase {{
    background-color: #70a0dc !important;
  }}

  /* المراجع */
  ol.ref-list {{
    margin: 0;
    padding-left: 22px;
    padding-right: 0;
    direction: ltr;
  }}

  ol.ref-list li {{
    font-size: 9.3pt;
    line-height: 1.55;
    margin-bottom: 12px;
    text-align: left;
    direction: ltr;
    font-family: 'Segoe UI', Arial, sans-serif;
  }}
</style>
</head>
<body>

<!-- ========================================================= -->
<!-- الصفحة 1: صفحة الغلاف (Cover Page)                        -->
<!-- ========================================================= -->
<div class="page">
  <div class="outer-border">
    <div class="inner-border">
      
      <!-- الترويسة والشعارات المتمركزة بدقة -->
      <table class="header-table">
        <tr>
          <td style="width: 46%; text-align: center; vertical-align: top;">
            <img src="data:image/png;base64,{yemen_logo_b64}" class="logo-img" style="margin: 0 auto 6px auto;" alt="شعار الجمهورية اليمنية">
            <div style="text-align: center; line-height: 1.45; font-size: 11pt; font-weight: 700;">
              الجمهورية اليمنية<br>
              وزارة التعليم العالي والبحث العلمي<br>
              جامعة إب
            </div>
          </td>
          <td style="width: 8%;"></td>
          <td style="width: 46%; text-align: center; vertical-align: top;">
            <img src="data:image/png;base64,{ibb_logo_b64}" class="logo-img" style="margin: 0 auto 6px auto;" alt="شعار جامعة إب">
            <div style="text-align: center; line-height: 1.45; font-size: 11pt; font-weight: 700;">
              كلية: الحاسبات والعلوم التطبيقية<br>
              القسم: علوم الحاسوب وتقنية المعلومات<br>
              مستوى: رابع
            </div>
          </td>
        </tr>
      </table>

      <!-- عنوان المقترح الرئيسي -->
      <div class="cover-proposal-title">
        مقترح مشروع مقرر التشفير - Cryptography Course Project Proposal
      </div>

      <!-- عنوان المشروع بالإنجليزية والعربية -->
      <div style="margin-top: 10mm; padding: 0 10px;">
        <div class="project-title-en-main">NeuroCrypt-Guard:</div>
        <div class="project-title-en-sub">
          An Adversarial Neural Cryptography Framework Resilient to Differential and Fault-Injection Attacks
        </div>
        <div class="project-title-ar">
          نيوروكربت-جارد: إطار تشفير عصبي تنافسي ذاتي التكيف مقاوم للهجمات التفاضلية وحقن الأخطاء
        </div>
      </div>

      <!-- تذييل الصفحة -->
      <div class="cover-footer">
        العام الجامعي: 2026/2027
      </div>

    </div>
  </div>
</div>


<!-- ========================================================= -->
<!-- الصفحة 2: عنوان المشروع، المشكلة، الأهداف                  -->
<!-- ========================================================= -->
<div class="page">
  <div class="outer-border">
    <div class="inner-border">
      
      <div class="section-h1">.1 عنوان المشروع</div>
      <div class="section-title-en">NeuroCrypt-Guard: An Adversarial Neural Cryptography Framework Resilient to Differential and Fault-Injection Attacks</div>
      <div class="section-title-ar">نيوروكربت-جارد: إطار تشفير عصبي تنافسي ذاتي التكيف مقاوم للهجمات التفاضلية وحقن الأخطاء</div>

      <div class="section-h1" style="margin-top: 10px;">.2 المشكلة (Problem Statement)</div>
      <p>
        تعتمد أنظمة التشفير المتناظر التقليدية بشكل أساسي على التحويلات الجبرية الصارمة وصناديق الاستبدال الثابتة (S-Boxes) كما في معيار التشفير المتقدم (AES) المقرّ من المعهد الوطني للمعايير والتقنية (Daemen &amp; Rijmen, 2002)، مما يمنحها أماناً حسابياً مصمتاً ولكنه يتسم بالجمود التكيفي. ومع التطور المتسارع في مجالات الذكاء الاصطناعي والحوسبة العصبية وإنترنت الأشياء (IoT)، برزت الحاجة لبروتوكولات حماية مرنة تتكيف ذاتياً مع تشويش القنوات المادية والبيئات غير المتجانسة.
      </p>
      <p>
        وقد ظهر مفهوم "التشفير العصبي التنافسي" (Adversarial Neural Cryptography - ANC) كأحد أهم التطبيقات الواعدة المستوحاة من شبكات التوليد التنافسية (GANs)، حيث تتدرب ثلاث شبكات عصبية (Alice, Bob, Eve) ذاتياً على التشفير وفك التشفير والتنصت في بيئة تنافسية (Abadi &amp; Andersen, 2016). وعلى الرغم من هذا الابتكار النظري، ما تزال هناك تحديات أمنية وهندسية جوهرية تحد من بناء أنظمة تشفير عصبية موثوقة وقابلة للتطبيق العملي، خصوصاً فيما يتعلق بتأثير الانهيار الصارم (SAC)، استقرار دوال الخسارة التنافسية، ومقاومة أعطال العتاد (Gräf &amp; Šíma, 2017; Webster &amp; Tavares, 1985).
      </p>
      <p>
        يهدف هذا المشروع إلى تطوير إطار تشفير عصبي متين ذاتي التكيف قادر على حماية البيانات بكفاءة تامة، مع إخضاعه لاختبارات كسر التشفير التفاضلي، ومعايير العشوائية الإحصائية الدولية (NIST SP 800-22)، وهجمات حقن الأخطاء العتادية لتقييم صموده ومقارنته مع أنظمة التشفير الكلاسيكية.
      </p>

      <div class="sub-heading-blue" style="color: #0f172a; margin-top: 6px;">المشكلة الرئيسية</div>
      <p>
        تواجه أنظمة التشفير العصبي التنافسي تحديات أمنية حرجة في تحقيق مبادئ الارتباك والانتشار (Confusion &amp; Diffusion)، والوقوع في ظاهرة "التشفير المعكوس" بسبب عدم انضباط دوال الخسارة، بالإضافة إلى افتقارها للمتانة أمام اضطرابات العتاد وغياب التقييم المعياري المقاس بمقاييس التشفير العالمية.
      </p>

      <div class="sub-heading-blue" style="color: #0f172a; margin-top: 6px;">المشاكل الفرعية</div>
      <p style="margin-bottom: 5px;">
        <span class="bold-item">المشكلة الأولى:</span> عجز الشبكات العصبية غير المهيأة عن تحقيق معيار تأثير الانهيار الصارم (SAC)، مما يؤدي لضعف تفاضلي يسرب ارتباطات خطية بين النص المشفر والمدخلات.
      </p>
      <p style="margin-bottom: 5px;">
        <span class="bold-item">المشكلة الثانية:</span> عدم استقرار التدريب التنافسي وظاهرة "التشفير المعكوس"؛ حيث يدفع انحراف دالة الخسارة شبكة إيف لتخمين عكس البتات بنسبة خطأ 100% مما يعني عملياً كسر التشفير، بدلاً من إجبارها على التخمين العشوائي الأعمى (50%) وفق نظرية شانون (Shannon, 1949).
      </p>
      <p style="margin-bottom: 10px;">
        <span class="bold-item">المشكلة الثالثة:</span> هشاشة النماذج العصبية المشفرة عند تشغيلها على أجهزة الحافة الطرفية المعرضة للضوضاء العتادية وهجمات حقن الأخطاء المتعمدة (Fault Injection)، مع غياب أدوات التقييم الإحصائي الموحدة (NIST SP 800-22).
      </p>

      <div class="section-h1" style="margin-top: 8px;">.3 أهداف المشروع (Objectives)</div>
      <p style="margin-bottom: 5px;">
        <span class="bold-item">الهدف الأول:</span> تصميم وبناء معمارية عصبية هجينة (Linear-1D-CNN) لـ Alice و Bob تدمج بين الخلط الكامل والانتشار المكاني، لتحقيق معيار تأثير الانهيار الصارم (SAC بنسبة تقارب 50%) لمقاومة كسر التشفير التفاضلي. (يعالج المشكلة الفرعية الأولى: ضعف الانتشار والتفاضل).
      </p>
      <p style="margin-bottom: 5px;">
        <span class="bold-item">الهدف الثاني:</span> صياغة دالة تكلفة مقيدة تربيعياً ومعدلة إحصائياً مع جدولة تدريب غير متناظرة (k-steps for Eve)، لضمان وصول دقة فك تشفير بوب إلى ~100% (BER &rarr; 0) مع تقييد إيف قسرياً عند التخمين الأعمى العشوائي (BER = 50%). (يعالج المشكلة الفرعية الثانية: استقرار التدريب ومنع التشفير المعكوس).
      </p>
      <p style="margin-bottom: 5px;">
        <span class="bold-item">الهدف الثالث:</span> تطوير جناح برمجي للتقييم الأمني واختبارات الإجهاد يخضع مخرجات النظام لمصفوفة اختبارات NIST SP 800-22 العشوائية، ويحاكي هجمات حقن الأخطاء واضطراب الأوزان، مع تقديم مقارنة معيارية شاملة في الأداء والسرعة مع AES-128. (يعالج المشكلة الفرعية الثالثة: المتانة العتادية والتقييم المعياري).
      </p>

    </div>
  </div>
</div>


<!-- ========================================================= -->
<!-- الصفحة 3: الأهمية، التقنيات، بداية الخطة الزمنية            -->
<!-- ========================================================= -->
<div class="page">
  <div class="outer-border">
    <div class="inner-border">
      
      <div class="section-h1">.4 أهمية المشروع (Project Significance)</div>
      <p>
        تكمن أهمية المشروع في استكشاف أحد الاتجاهات البحثية المتقدمة في تقاطع الذكاء الاصطناعي التنافسي مع أمن المعلومات، من خلال تطوير خوارزمية تشفير عصبية ذاتية التكيف ومحصنة أمنياً ومقاسة بأدوات التشفير القياسية.
      </p>

      <div class="sub-heading-blue">الأهمية العلمية</div>
      <ul>
        <li>تجسير الفجوة بين علوم التعلم العميق التنافسي وأسس أمن المعلومات ونظرية شانون للأمان التام.</li>
        <li>دراسة قدرة الشبكات العصبية على ابتكار تمثيلات مشفرة ذاتية دون الاعتماد على خوارزميات مسبقة الصنع.</li>
      </ul>

      <div class="sub-heading-blue">الأهمية التقنية</div>
      <ul>
        <li>دمج معالجة البتات الثنائية والالتفاف العصبي مع أدوات التقييم الأمني القياسية (NIST SP 800-22).</li>
        <li>معالجة الثغرات الرياضية في دوال الخسارة التنافسية وبناء نظام قابل للتوسع والتطوير مستقبلاً.</li>
      </ul>

      <div class="sub-heading-blue">التطبيقات المستقبلية</div>
      <ul>
        <li>تأمين قنوات الاتصال الذاتية لشبكات إنترنت الأشياء (IoT) والأنظمة الطرفية منخفضة الموارد.</li>
        <li>أنظمة إخفاء البيانات العصبي (Neural Steganography) لنقل البيانات الحساسة داخل الوسائط دون إثارة الشكوك.</li>
        <li>تطوير بروتوكولات حماية متكيفة ومقاومة لتشويش قنوات الاتصال المادية.</li>
      </ul>

      <div class="sub-heading-blue">مميزات المشروع</div>
      <ul>
        <li>تحقيق معدل استرجاع ممتاز للطرف الشرعي (&gt; 99.5%) مع حيرة تامة للمتنصت (~50%).</li>
        <li>مرونة المعمارية وتوافقها التام مع مسرعات الحوسبة العصبية (GPU/NPU).</li>
        <li>خضوع النظام لاختبارات الانهيار الصارم (SAC) وفحوصات حقن الأخطاء واختبارات NIST.</li>
        <li>يعتمد على بيئة برمجية متطورة وتقنيات مفتوحة المصدر بالكامل.</li>
      </ul>

      <div class="section-h1" style="margin-top: 10px;">.5 التقنيات والأدوات المقترحة (Technologies and Tools)</div>
      
      <table class="custom-table">
        <thead>
          <tr>
            <th style="width: 25%;">المحور</th>
            <th style="width: 75%;">الوصف / الأدوات المقترحة</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="font-weight: 700; text-align: center;">محرك الذكاء الاصطناعي (AI Core)</td>
            <td>مكتبة PyTorch 2.x لبناء معمارية النماذج العصبية (Alice, Bob, Eve)، وتخصيص دوال الخسارة المقيدة والتحكم بالتدرجات.</td>
          </tr>
          <tr>
            <td style="font-weight: 700; text-align: center;">التسريع العتادي والحوسبي</td>
            <td>حوسبة متوازية عبر منصة NVIDIA CUDA &amp; cuDNN لتسريع التدريب التنافسي وخفض استهلاك الذاكرة.</td>
          </tr>
          <tr>
            <td style="font-weight: 700; text-align: center;">محرك التقييم الأمني والإحصائي</td>
            <td>حزمة اختبارات العشوائية العالمية NIST SP 800-22 (sts-pylib) بالإضافة إلى مصفوفات التحليل التفاضلي عبر NumPy/SciPy.</td>
          </tr>
          <tr>
            <td style="font-weight: 700; text-align: center;">المرجعية المعيارية المقارنة</td>
            <td>مكتبة PyCryptodome / Cryptography لتوفير تطبيق معياري لـ AES-128 لقياس فروق الأداء والسرعة والإنتاجية.</td>
          </tr>
          <tr>
            <td style="font-weight: 700; text-align: center;">بيانات التدريب والاختبار</td>
            <td>مولد CSPRNG ديناميكي فائق الأمان، مع داتا سيت نصوص كلاسيكية حقيقية لاختبار كسر التكرار اللغوي.</td>
          </tr>
          <tr>
            <td style="font-weight: 700; text-align: center;">الواجهة الرسومية والتحكم</td>
            <td>لوحة تحكم تفاعلية (Interactive Dashboard) عبر Streamlit / FastAPI لعرض محاكاة التشفير، الخرائط الحرارية، وسلايدر حقن الأخطاء.</td>
          </tr>
        </tbody>
      </table>

      <div class="section-h1" style="margin-top: 8px;">.6 الخطة الزمنية المقترحة (Gantt Chart)</div>

    </div>
  </div>
</div>


<!-- ========================================================= -->
<!-- الصفحة 4: جدول جانت، أسماء أعضاء الفريق                    -->
<!-- ========================================================= -->
<div class="page">
  <div class="outer-border">
    <div class="inner-border">
      
      <!-- جدول جانت التفصيلي -->
      <table class="gantt-table">
        <thead>
          <tr>
            <th style="width: 52%;">النشاط</th>
            <th style="width: 6%;">2-1</th>
            <th style="width: 6%;">4-3</th>
            <th style="width: 6%;">6-5</th>
            <th style="width: 6%;">8-7</th>
            <th style="width: 6%;">10-9</th>
            <th style="width: 6%;">12-11</th>
            <th style="width: 6%;">14-13</th>
            <th style="width: 6%;">16-15</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="task-name">المرحلة الأولى: دراسة وتحليل المشكلة وتحديد معايير NIST ونظرية شانون</td>
            <td class="active-phase"></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة الثانية: تصميم معمارية النظام العصبية وصياغة دالة الخسارة المقيدة</td>
            <td></td>
            <td class="active-phase"></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة الثالثة: برمجة وتجهيز نماذج PyTorch لـ Alice و Bob و Eve</td>
            <td></td>
            <td></td>
            <td class="active-phase"></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة الرابعة: ضبط حلقة التدريب التنافسي غير المتناظر وحل التشفير المعكوس</td>
            <td></td>
            <td></td>
            <td></td>
            <td class="active-phase"></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة الخامسة: برمجة مصفوفة كسر التشفير التفاضلي وحساب معيار SAC</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="active-phase"></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة السادسة: تطبيق حزمة اختبارات العشوائية NIST SP 800-22 الإحصائية</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="active-phase"></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة السابعة: محاكاة هجمات حقن الأخطاء وإجهاد الأوزان والدمج مع AES</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="active-phase"></td>
            <td></td>
          </tr>
          <tr>
            <td class="task-name">المرحلة الثامنة: دمج لوحة التحكم، إعداد التقرير الأكاديمي النهائي والمناقشة</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td class="active-phase"></td>
          </tr>
        </tbody>
      </table>

      <!-- جدول أسماء أعضاء الفريق -->
      <div class="section-h1" style="margin-top: 35px; margin-bottom: 12px;">.7 أسماء أعضاء الفريق</div>
      
      <table class="custom-table" style="width: 100%; margin-top: 5px;">
        <thead>
          <tr>
            <th style="width: 15%;">الرقم</th>
            <th style="width: 85%;">الاسم</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="text-align: center; font-weight: 700;">1</td>
            <td style="padding-right: 15px; font-weight: 600;">يعقوب خالد محمد علي المهاجري</td>
          </tr>
          <tr>
            <td style="text-align: center; font-weight: 700;">2</td>
            <td style="padding-right: 15px; font-weight: 600;">سليمان صالح صالح العربي</td>
          </tr>
          <tr>
            <td style="text-align: center; font-weight: 700;">3</td>
            <td style="padding-right: 15px; font-weight: 600;">مالك عادل عبده جبران</td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</div>


<!-- ========================================================= -->
<!-- الصفحة 5: المراجع (References)                             -->
<!-- ========================================================= -->
<div class="page">
  <div class="outer-border">
    <div class="inner-border">
      
      <div class="section-h1" style="font-size: 15pt; color: #1e40af; margin-bottom: 20px;">
        المراجع (References)
      </div>

      <ol class="ref-list">
        <li>
          Abadi, M., &amp; Andersen, D. G. (2016). <em>Learning to protect communications with adversarial neural cryptography</em>. arXiv preprint arXiv:1610.06918. https://arxiv.org/abs/1610.06918
        </li>
        <li>
          Biham, E., &amp; Shamir, A. (1991). Differential cryptanalysis of DES-like cryptosystems. <em>Journal of Cryptology</em>, 4(1), 3–72. https://doi.org/10.1007/BF00630563
        </li>
        <li>
          Boneh, D., DeMillo, R. A., &amp; Lipton, R. J. (1997). On the importance of checking cryptographic protocols for faults. In W. Fumy (Ed.), <em>Advances in Cryptology — EUROCRYPT '97</em> (Lecture Notes in Computer Science, Vol. 1233, pp. 37–51). Springer. https://doi.org/10.1007/3-540-69053-0_4
        </li>
        <li>
          Coutinho, M., Neto, F. L., &amp; de Oliveira, R. M. (2018). Learning symmetric encryption with deep adversarial neural networks. <em>IEEE Latin America Transactions</em>, 16(8), 2248–2254. https://doi.org/10.1109/TLA.2018.8528245
        </li>
        <li>
          Daemen, J., &amp; Rijmen, V. (2002). <em>The design of Rijndael: AES - The Advanced Encryption Standard</em>. Springer-Verlag. https://doi.org/10.1007/978-3-662-04722-4
        </li>
        <li>
          Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B., Warde-Farley, D., Ozair, S., Courville, A., &amp; Bengio, Y. (2014). Generative adversarial nets. In <em>Advances in Neural Information Processing Systems</em> (Vol. 27, pp. 2672–2680).
        </li>
        <li>
          Gräf, J., &amp; Šíma, J. (2017). <em>Analysis and cracking of adversarial neural cryptography</em>. arXiv preprint arXiv:1705.03458. https://arxiv.org/abs/1705.03458
        </li>
        <li>
          International Organization for Standardization. (2016). <em>Information technology — Security techniques — Testing methods for the mitigation of non-invasive attack classes on cryptographic modules</em> (ISO/IEC Standard No. 17825:2016).
        </li>
        <li>
          Rukhin, A., Soto, J., Nechvatal, J., Smid, M., Barker, E., Leigh, S., Levenson, M., Vangel, M., Banks, D., Heckert, A., Dray, J., &amp; Vo, S. (2010). <em>A statistical test suite for random and pseudorandom number generators for cryptographic applications</em> (NIST Special Publication 800-22, Rev. 1a). National Institute of Standards and Technology.
        </li>
        <li>
          Shannon, C. E. (1949). Communication theory of secrecy systems. <em>Bell System Technical Journal</em>, 28(4), 656–715. https://doi.org/10.1002/j.1538-7305.1949.tb00928.x
        </li>
        <li>
          Webster, A. F., &amp; Tavares, S. E. (1985). On the design of S-boxes. In H. C. Williams (Ed.), <em>Advances in Cryptology — CRYPTO '85 Proceedings</em> (Lecture Notes in Computer Science, Vol. 218, pp. 523–534). Springer. https://doi.org/10.1007/3-540-39799-X_41
        </li>
      </ol>

    </div>
  </div>
</div>

</body>
</html>
"""
    html_path = os.path.join(BASE_DIR, "proposal_template.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[✓] تم توليد ملف قالب الـ HTML المطابق: {html_path}")
    return html_path

def compile_to_pdf(html_path):
    pdf_out = os.path.join(BASE_DIR, "المقترح_NeuroCrypt_Guard_نهائي.pdf")
    
    # البحث عن Edge أو Chrome
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    browser_bin = None
    for p in edge_paths:
        if os.path.exists(p):
            browser_bin = p
            break
            
    if not browser_bin:
        print("[-] لم يتم العثور على مسار المتصفح لتحويل الـ PDF.")
        return False

    print(f"[*] جاري تصدير PDF عبر محرك المتصفح عالي الدقة: {browser_bin}")
    cmd = [
        browser_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_out}",
        html_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_out) and os.path.getsize(pdf_out) > 5000:
        print(f"[✓] تم توليد ملف الـ PDF المطابق بنجاح تام! الحجم: {os.path.getsize(pdf_out):,} بايت.")
        print(f"    المسار: {pdf_out}")
        return True
    else:
        print(f"[-] خطأ في تصدير PDF: {res.stderr}")
        return False

def generate_latex():
    tex_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage[top=2cm, bottom=2cm, left=2cm, right=2cm]{geometry}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage[numerals=maghrib]{arabic}
\setotherlanguage{english}

% تعيين خطوط عربية متوافقة
\newfontfamily\arabicfont[Script=Arabic]{Amiri}
\newfontfamily\arabicfontsf[Script=Arabic]{Cairo}
\setmainfont{Times New Roman}

\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tabularx}
\usepackage{colortbl}
\usepackage{hyperref}

\definecolor{navyblue}{RGB}{31, 78, 121}
\definecolor{lightblue}{RGB}{112, 160, 220}

\begin{document}

% ------------------ الصفحة 1: الغلاف ------------------
\thispagestyle{empty}
\begin{center}
\begin{tabularx}{\textwidth}{XrX}
\begin{center}
\includegraphics[width=2.2cm]{assets/logo_ibb_clean.png}\\
\textbf{كلية: الحاسبات والعلوم التطبيقية}\\
\textbf{القسم: علوم الحاسوب وتقنية المعلومات}\\
\textbf{مستوى: رابع}
\end{center}
& &
\begin{center}
\includegraphics[width=2.5cm]{assets/logo_yemen_clean.png}\\
\textbf{الجمهورية اليمنية}\\
\textbf{وزارة التعليم العالي والبحث العلمي}\\
\textbf{جامعة إب}
\end{center}
\end{tabularx}

\vspace{4cm}
{\Large\bfseries\color{navyblue} مقترح مشروع مقرر التشفير - Cryptography Course Project Proposal}

\vspace{2cm}
\begin{english}
\begin{flushleft}
{\LARGE\bfseries\color{navyblue} NeuroCrypt-Guard:}\\
\vspace{0.2cm}
{\large\bfseries\color{navyblue} An Adversarial Neural Cryptography Framework Resilient to Differential and Fault-Injection Attacks}
\end{flushleft}
\end{english}

\vspace{0.5cm}
{\Large\bfseries\color{navyblue} نيوروكربت-جارد: إطار تشفير عصبي تنافسي ذاتي التكيف مقاوم للهجمات التفاضلية وحقن الأخطاء}

\vfill
{\large\bfseries العام الجامعي: 2026/2027}
\end{center}

\newpage

% ------------------ الصفحة 2: المشكلة والأهداف ------------------
\section*{1. عنوان المشروع}
\begin{english}
\textbf{NeuroCrypt-Guard: An Adversarial Neural Cryptography Framework Resilient to Differential and Fault-Injection Attacks}
\end{english}\\
\textbf{نيوروكربت-جارد: إطار تشفير عصبي تنافسي ذاتي التكيف مقاوم للهجمات التفاضلية وحقن الأخطاء}

\section*{2. المشكلة (Problem Statement)}
تعتمد أنظمة التشفير المتناظر التقليدية بشكل أساسي على التحويلات الجبرية الصارمة وصناديق الاستبدال الثابتة (S-Boxes) كما في معيار التشفير المتقدم (AES) المقرّ من المعهد الوطني للمعايير والتقنية (Daemen \& Rijmen, 2002)، مما يمنحها أماناً حسابياً مصمتاً ولكنه يتسم بالجمود التكيفي.

\subsection*{المشكلة الرئيسية}
تواجه أنظمة التشفير العصبي التنافسي تحديات أمنية حرجة في تحقيق مبادئ الارتباك والانتشار، والوقوع في ظاهرة "التشفير المعكوس" بسبب عدم انضباط دوال الخسارة، بالإضافة إلى افتقارها للمتانة أمام اضطرابات العتاد.

\subsection*{المشاكل الفرعية}
\textbf{المشكلة الأولى:} عجز الشبكات العصبية غير المهيأة عن تحقيق معيار تأثير الانهيار الصارم (SAC).\\
\textbf{المشكلة الثانية:} عدم استقرار التدريب التنافسي وظاهرة "التشفير المعكوس".\\
\textbf{المشكلة الثالثة:} هشاشة النماذج العصبية المشفرة أمام هجمات حقن الأخطاء (Fault Injection).

\section*{3. أهداف المشروع (Objectives)}
\textbf{الهدف الأول:} تصميم وبناء معمارية عصبية هجينة تحقق معيار SAC بنسبة تقارب 50\%.\\
\textbf{الهدف الثاني:} صياغة دالة تكلفة مقيدة تربيعياً لضمان فك تشفير سليم ومنع التشفير المعكوس.\\
\textbf{الهدف الثالث:} تطوير جناح برمجي للتقييم الأمني بمقاييس NIST SP 800-22 وحقن الأخطاء ومقارنة AES-128.

\newpage

% ------------------ الصفحة 3: الأهمية والتقنيات ------------------
\section*{4. أهمية المشروع (Project Significance)}
\subsection*{\color{navyblue}الأهمية العلمية}
\begin{itemize}
\item تجسير الفجوة بين التعلم العميق التنافسي ونظرية شانون للأمان التام.
\item دراسة تمثيلات التشفير العصبية التكيفية.
\end{itemize}

\subsection*{\color{navyblue}الأهمية التقنية}
\begin{itemize}
\item دمج معالجة البتات مع حزمة اختبارات NIST SP 800-22.
\item بناء نظام قابل للتوسع والتطوير مستقبلاً.
\end{itemize}

\section*{5. التقنيات والأدوات المقترحة (Technologies and Tools)}
\begin{tabularx}{\textwidth}{|l|X|}
\hline
\rowcolor{navyblue} \color{white}\textbf{المحور} & \color{white}\textbf{الوصف / الأدوات المقترحة} \\
\hline
محرك الذكاء الاصطناعي & مكتبة PyTorch 2.x لبناء معمارية النماذج العصبية. \\
\hline
التسريع العتادي & حوسبة متوازية عبر منصة NVIDIA CUDA \& cuDNN. \\
\hline
التقييم الأمني والإحصائي & حزمة اختبارات العشوائية العالمية NIST SP 800-22 ومصفوفات SAC. \\
\hline
المرجعية المعيارية المقارنة & تطبيق معياري لـ AES-128 عبر مكتبة PyCryptodome. \\
\hline
البيانات والداتا سيت & مولد CSPRNG ديناميكي وداتا سيت نصوص حقيقية. \\
\hline
واجهة التحكم & لوحة تحكم تفاعلية عبر Streamlit / FastAPI. \\
\hline
\end{tabularx}

\section*{6. الخطة الزمنية المقترحة (Gantt Chart)}

\newpage

% ------------------ الصفحة 4: جدول جانت وأعضاء الفريق ------------------
\section*{مخطط جانت الزمني (Gantt Chart)}
\begin{center}
\begin{tabular}{|l|c|c|c|c|c|c|c|c|}
\hline
\rowcolor{navyblue} \color{white}\textbf{النشاط} & \color{white}\textbf{2-1} & \color{white}\textbf{4-3} & \color{white}\textbf{6-5} & \color{white}\textbf{8-7} & \color{white}\textbf{10-9} & \color{white}\textbf{12-11} & \color{white}\textbf{14-13} & \color{white}\textbf{16-15} \\
\hline
المرحلة 1: دراسة وتحليل المشكلة & \cellcolor{lightblue} & & & & & & & \\
\hline
المرحلة 2: تصميم معمارية النظام & & \cellcolor{lightblue} & & & & & & \\
\hline
المرحلة 3: تطوير نماذج PyTorch & & & \cellcolor{lightblue} & & & & & \\
\hline
المرحلة 4: ضبط التدريب التنافسي & & & & \cellcolor{lightblue} & & & & \\
\hline
المرحلة 5: كسر التشفير ومصفوفة SAC & & & & & \cellcolor{lightblue} & & & \\
\hline
المرحلة 6: تطبيق اختبارات NIST & & & & & & \cellcolor{lightblue} & & \\
\hline
المرحلة 7: محاكاة حقن الأخطاء ومقارنة AES & & & & & & & \cellcolor{lightblue} & \\
\hline
المرحلة 8: إعداد التقرير والمناقشة & & & & & & & & \cellcolor{lightblue} \\
\hline
\end{tabular}
\end{center}

\vspace{1.5cm}
\section*{7. أسماء أعضاء الفريق}
\begin{center}
\begin{tabular}{|c|p{10cm}|}
\hline
\rowcolor{navyblue} \color{white}\textbf{الرقم} & \color{white}\textbf{الاسم} \\
\hline
1 & يعقوب خالد محمد علي المهاجري \\
\hline
2 & سليمان صالح صالح العربي \\
\hline
3 & مالك عادل عبده جبران \\
\hline
\end{tabular}
\end{center}

\newpage

% ------------------ الصفحة 5: المراجع ------------------
\section*{المراجع (References)}
\begin{english}
\begin{enumerate}
\item Abadi, M., \& Andersen, D. G. (2016). \textit{Learning to protect communications with adversarial neural cryptography}. arXiv preprint arXiv:1610.06918.
\item Biham, E., \& Shamir, A. (1991). Differential cryptanalysis of DES-like cryptosystems. \textit{Journal of Cryptology}, 4(1), 3–72.
\item Boneh, D., DeMillo, R. A., \& Lipton, R. J. (1997). On the importance of checking cryptographic protocols for faults. \textit{Advances in Cryptology — EUROCRYPT '97}, 37–51.
\item Daemen, J., \& Rijmen, V. (2002). \textit{The design of Rijndael: AES - The Advanced Encryption Standard}. Springer-Verlag.
\item Goodfellow, I., et al. (2014). Generative adversarial nets. \textit{Advances in Neural Information Processing Systems}, 27, 2672–2680.
\item Gräf, J., \& Šíma, J. (2017). \textit{Analysis and cracking of adversarial neural cryptography}. arXiv preprint arXiv:1705.03458.
\item Rukhin, A., et al. (2010). \textit{A statistical test suite for random and pseudorandom number generators for cryptographic applications} (NIST SP 800-22, Rev. 1a).
\item Shannon, C. E. (1949). Communication theory of secrecy systems. \textit{Bell System Technical Journal}, 28(4), 656–715.
\item Webster, A. F., \& Tavares, S. E. (1985). On the design of S-boxes. \textit{Advances in Cryptology — CRYPTO '85}, 523–534.
\end{enumerate}
\end{english}

\end{document}
"""
    tex_path = os.path.join(BASE_DIR, "proposal.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"[✓] تم توليد كود LaTeX المصدري لـ Overleaf: {tex_path}")

def generate_docx():
    doc = docx.Document()
    
    # ضبط الهوامش إلى 2 سم
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # الغلاف
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_h = p_header.add_run("الجمهورية اليمنية - وزارة التعليم العالي والبحث العلمي - جامعة إب\nكلية الحاسبات والعلوم التطبيقية - قسم علوم الحاسوب وتقنية المعلومات - مستوى رابع\n")
    run_h.bold = True
    run_h.font.size = Pt(11)

    p_prop = doc.add_paragraph()
    p_prop.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_prop = p_prop.add_run("\n\nمقترح مشروع مقرر التشفير - Cryptography Course Project Proposal\n\n")
    run_prop.bold = True
    run_prop.font.size = Pt(20)
    run_prop.font.color.rgb = RGBColor(30, 64, 175)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_t1 = p_title.add_run("NeuroCrypt-Guard:\n")
    run_t1.bold = True
    run_t1.font.size = Pt(22)
    run_t1.font.color.rgb = RGBColor(30, 64, 175)
    
    run_t2 = p_title.add_run("An Adversarial Neural Cryptography Framework Resilient to Differential and Fault-Injection Attacks\n\n")
    run_t2.bold = True
    run_t2.font.size = Pt(13)
    run_t2.font.color.rgb = RGBColor(30, 64, 175)

    p_ar_title = doc.add_paragraph()
    p_ar_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tar = p_ar_title.add_run("نيوروكربت-جارد: إطار تشفير عصبي تنافسي ذاتي التكيف مقاوم للهجمات التفاضلية وحقن الأخطاء\n\n\n\n")
    run_tar.bold = True
    run_tar.font.size = Pt(14)
    run_tar.font.color.rgb = RGBColor(30, 64, 175)

    p_year = doc.add_paragraph()
    p_year.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_y = p_year.add_run("العام الجامعي: 2026/2027")
    run_y.bold = True
    run_y.font.size = Pt(12)

    doc.add_page_break()

    # الأقسام
    doc.add_heading("1. عنوان المشروع", level=1)
    p = doc.add_paragraph()
    p.add_run("NeuroCrypt-Guard: An Adversarial Neural Cryptography Framework Resilient to Differential and Fault-Injection Attacks\n").bold = True
    p.add_run("نيوروكربت-جارد: إطار تشفير عصبي تنافسي ذاتي التكيف مقاوم للهجمات التفاضلية وحقن الأخطاء").bold = True

    doc.add_heading("2. المشكلة (Problem Statement)", level=1)
    doc.add_paragraph("تعتمد أنظمة التشفير المتناظر التقليدية بشكل أساسي على التحويلات الجبرية الصارمة وصناديق الاستبدال الثابتة (S-Boxes) كما في معيار التشفير المتقدم (AES)، مما يمنحها أماناً حسابياً مصمتاً ولكنه يتسم بالجمود التكيفي.")
    doc.add_paragraph("وقد ظهر مفهوم التشفير العصبي التنافسي (ANC) كأحد أهم التطبيقات الواعدة المستوحاة من شبكات GANs حيث تتدرب شبكات (Alice, Bob, Eve) ذاتياً.")
    
    doc.add_heading("المشكلة الرئيسية", level=2)
    doc.add_paragraph("تواجه أنظمة التشفير العصبي التنافسي تحديات أمنية حرجة في تحقيق مبادئ الارتباك والانتشار، والوقوع في ظاهرة التشفير المعكوس، بالإضافة إلى هشاشتها أمام أعطال واضطرابات العتاد.")

    doc.add_heading("المشاكل الفرعية", level=2)
    doc.add_paragraph("المشكلة الأولى: عجز الشبكات العصبية غير المهيأة عن تحقيق معيار تأثير الانهيار الصارم (SAC).")
    doc.add_paragraph("المشكلة الثانية: عدم استقرار التدريب التنافسي وظاهرة التشفير المعكوس عند انحراف دالة الخسارة.")
    doc.add_paragraph("المشكلة الثالثة: هشاشة النماذج العصبية المشفرة أمام هجمات حقن الأخطاء (Fault Injection).")

    doc.add_heading("3. أهداف المشروع (Objectives)", level=1)
    doc.add_paragraph("الهدف الأول: تصميم وبناء معمارية عصبية هجينة تحقق معيار SAC بنسبة تقارب 50% لمقاومة الكسر التفاضلي.")
    doc.add_paragraph("الهدف الثاني: صياغة دالة تكلفة مقيدة تربيعياً لضمان فك تشفير سليم (> 99.5%) وحصر إيف عند التخمين الأعمى.")
    doc.add_paragraph("الهدف الثالث: تطوير جناح برمجي للتقييم الأمني بمقاييس NIST SP 800-22 وحقن الأخطاء ومقارنة AES-128.")

    doc.add_page_break()

    # الأهمية والتقنيات
    doc.add_heading("4. أهمية المشروع (Project Significance)", level=1)
    doc.add_paragraph("تكمن أهمية المشروع في استكشاف الاتجاهات الحديثة لتأمين الاتصالات عبر الذكاء الاصطناعي التنافسي.")
    
    doc.add_heading("5. التقنيات والأدوات المقترحة (Technologies and Tools)", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "المحور"
    hdr_cells[1].text = "الوصف / الأدوات المقترحة"
    
    tools = [
        ("محرك الذكاء الاصطناعي", "مكتبة PyTorch 2.x لبناء معمارية النماذج العصبية (Alice, Bob, Eve)."),
        ("التسريع العتادي", "منصة NVIDIA CUDA & cuDNN لتسريع التدريب التنافسي."),
        ("التقييم الأمني والإحصائي", "حزمة اختبارات العشوائية العالمية NIST SP 800-22 ومصفوفة SAC."),
        ("المرجعية المعيارية", "خوارزمية AES-128 عبر مكتبة PyCryptodome."),
        ("البيانات", "مولد CSPRNG ديناميكي وداتا سيت نصوص كلاسيكية حقيقية."),
        ("واجهة التحكم", "لوحة تحكم تفاعلية عبر Streamlit / FastAPI.")
    ]
    for m, d in tools:
        row_cells = table.add_row().cells
        row_cells[0].text = m
        row_cells[1].text = d

    doc.add_page_break()

    # أعضاء الفريق
    doc.add_heading("7. أسماء أعضاء الفريق", level=1)
    team_table = doc.add_table(rows=1, cols=2)
    th_cells = team_table.rows[0].cells
    th_cells[0].text = "الرقم"
    th_cells[1].text = "الاسم"
    
    team = [
        ("1", "يعقوب خالد محمد علي المهاجري"),
        ("2", "سليمان صالح صالح العربي"),
        ("3", "مالك عادل عبده جبران")
    ]
    for r, name in team:
        c = team_table.add_row().cells
        c[0].text = r
        c[1].text = name

    doc.add_page_break()

    # المراجع
    doc.add_heading("المراجع (References)", level=1)
    refs = [
        "Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with adversarial neural cryptography. arXiv:1610.06918.",
        "Biham, E., & Shamir, A. (1991). Differential cryptanalysis of DES-like cryptosystems. Journal of Cryptology, 4(1), 3–72.",
        "Boneh, D., DeMillo, R. A., & Lipton, R. J. (1997). On the importance of checking cryptographic protocols for faults. EUROCRYPT '97, 37–51.",
        "Daemen, J., & Rijmen, V. (2002). The design of Rijndael: AES - The Advanced Encryption Standard. Springer-Verlag.",
        "Gräf, J., & Šíma, J. (2017). Analysis and cracking of adversarial neural cryptography. arXiv:1705.03458.",
        "Rukhin, A., et al. (2010). A statistical test suite for random and pseudorandom number generators for cryptographic applications (NIST SP 800-22, Rev. 1a).",
        "Shannon, C. E. (1949). Communication theory of secrecy systems. Bell System Technical Journal, 28(4), 656–715.",
        "Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. CRYPTO '85, 523–534."
    ]
    for ref in refs:
        doc.add_paragraph(ref, style='List Number')

    docx_path = os.path.join(BASE_DIR, "المقترح_NeuroCrypt_Guard_نهائي.docx")
    doc.save(docx_path)
    print(f"[✓] تم توليد ملف ميكروسوفت وورد Word القابل للتحرير: {docx_path}")

def main():
    print("=" * 65)
    print("  بدء بناء وثائق المقترح النهائي المطابق لقالب جامعة إب")
    print("=" * 65)
    
    html_path = generate_html()
    compile_to_pdf(html_path)
    generate_docx()
    generate_latex()
    
    print("\n" + "=" * 65)
    print("  [✓] اكتملت بنجاح عملية توليد جميع الصيغ (PDF + Word + LaTeX)!")
    print("=" * 65)

if __name__ == "__main__":
    main()
