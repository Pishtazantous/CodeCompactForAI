

# CodeCompactForAI

ابزار خط فرمان برای آماده‌سازی پروژه‌های نرم‌افزاری جهت ارسال به مدل‌های هوش مصنوعی — بدون فرستادن کل پروژه.

با این ابزار، به‌جای ارسال کل کدبیس به AI، ابتدا یک **نقشهٔ فشرده** می‌فرستید و AI خودش تصمیم می‌گیرد کدام فایل‌ها را لازم دارد. نتیجه: **کاهش ۱۰ تا ۵۰ برابری** حجم ارسال، هزینهٔ کمتر، و پاسخ دقیق‌تر.

---

## فهرست

1. [معرفی کوتاه](#معرفی-کوتاه)
2. [پیش‌نیازها](#پیشنیازها)
3. [نصب](#نصب)
4. [شروع سریع](#شروع-سریع)
5. [تولید خروجی از کل پروژه](#تولید-خروجی-از-کل-پروژه)
6. [گردش کار کامل با AI](#گردش-کار-کامل-با-ai)
7. [دستورات codemerge.py](#دستورات-codemergepy)
8. [گزینه‌های مشترک](#گزینههای-مشترک)
9. [فایل ignore](#فایل-ignore)
10. [فایل‌های حساس](#فایلهای-حساس)
11. [ساختار promptها](#ساختار-promptها)
12. [ابزارهای کمکی](#ابزارهای-کمکی)
13. [تست](#تست)
14. [عیب‌یابی](#عیبیابی)
15. [ساختار پروژه](#ساختار-پروژه)

---

## معرفی کوتاه

`codemerge.py` یک اسکریپت تک‌فایل پایتون است که چهار کار انجام می‌دهد:

| دستور | کار |
|---|---|
| `manifest` | ساخت نقشهٔ فشردهٔ پروژه (مسیر + imports + توابع + کلاس‌ها) |
| `fetch` | دریافت محتوای کامل لیست مشخصی از فایل‌ها |
| `diff` | دریافت فقط فایل‌های تغییر یافته از آخرین اجرا |
| `search` | جستجوی یک نماد در کل پروژه |

به همراه این‌ها، مجموعه‌ای از ابزارهای جانبی در `tools/` برای snapshot، اعمال خروجی AI، verify، مدیریت session و... وجود دارد.

---

## پیش‌نیازها

- **Python 3.9+** (توصیه‌شده: 3.11+)
- **Git** (اختیاری، ولی توصیه می‌شود)
- **tiktoken** (اختیاری، برای شمارش دقیق توکن)

```bash
pip install tiktoken    # اختیاری
```

---

## نصب

هیچ نصبی لازم نیست. کل پروژه را کپی کنید و از دستورات استفاده کنید.

```bash
# بررسی سلامت
python codemerge.py --help
python codemerge.py langs
```

---

## شروع سریع

سه دستور برای شروع:

```bash
# ۱. ساخت نقشهٔ پروژه
python codemerge.py manifest --format md -o .ai/manifest.md

# ۲. ارسال .ai/manifest.md به AI
#    (به همراه promptهای مناسب — ببینید بخش «گردش کار کامل»)

# ۳. بعد از پاسخ AI، دریافت فایل‌های درخواستی
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

سپس `.ai/bundle.txt` را به AI بفرستید.

---

## تولید خروجی از کل پروژه

گاهی لازم است کل پروژه — نه فقط فایل‌های انتخابی — در یک فایل خروجی گرفته شود. مثلاً:

- بارگذاری اولیه برای AI که context کامل را ببیند (پروژه‌های کوچک)
- آرشیو یا backup قبل از تغییرات بزرگ
- بازبینی offline یا انتقال به سیستم دیگر
- ساخت bundle برای فایل‌های خاص (مثلاً فقط TypeScript)

`codemerge.py` چهار روش برای این کار دارد. هر روش برای سناریوی متفاوتی مناسب است.

### روش ۱ — نقشهٔ کامل پروژه (فقط فهرست + نمادها)

**مناسب برای:** ارسال سریع ساختار کل پروژه به AI بدون محتوای فایل‌ها.

```bash
# فرمت متن
python codemerge.py manifest --all-files -o .ai/manifest-full.txt

# فرمت Markdown (مناسب AI)
python codemerge.py manifest --all-files --format md -o .ai/manifest-full.md

# فرمت JSON (مناسب ابزارهای خودکار)
python codemerge.py manifest --all-files --format json -o .ai/manifest-full.json

# فشرده‌ترین حالت (بدون symbols و imports)
python codemerge.py manifest --all-files --no-symbols --no-imports -o .ai/files-list.txt
```

**نکته:** `--all-files` فیلتر زبان را نادیده می‌گیرد و همهٔ فایل‌های متنی را شامل می‌شود.

**اندازهٔ معمول:** برای پروژه‌ای با ۲۰۰ فایل، حدود ۱۰ تا ۳۰ کیلوبایت.

### روش ۲ — bundle کامل محتوای پروژه (شامل متن همهٔ فایل‌ها)

**مناسب برای:** پروژه‌های کوچک یا بارگذاری اولیه.

```bash
# اجرای اول diff = کل پروژه (بدون state قبلی)
python codemerge.py diff -o .ai/full_project.txt

# اگر قبلاً diff اجرا کرده‌اید و می‌خواهید دوباره کل پروژه را بگیرید:
python codemerge.py diff --full --reset-state -o .ai/full_project.txt

# بدون هدر (فقط محتوای فایل‌ها)
python codemerge.py diff --full --reset-state --no-header -o .ai/full_project.txt
```

**چرا `diff` و نه `fetch`؟** چون `fetch` نیاز به لیست صریح فایل‌ها دارد و برای «کل پروژه» باید لیست کامل ساخت. در حالی که `diff` با `--full` خودش همهٔ فایل‌ها را انتخاب می‌کند.

### روش ۳ — bundle کامل با فیلتر زبان

**مناسب برای:** پروژه‌های چندزبانه که می‌خواهید فقط یک زبان را داشته باشید.

```bash
# فقط TypeScript/JavaScript
python codemerge.py diff --full --reset-state -l typescript,javascript -o .ai/ts-only.txt

# فقط Python (بک‌اند)
python codemerge.py diff --full --reset-state -l python -o .ai/backend.txt

# فقط Markdown (مستندات)
python codemerge.py diff --full --reset-state -l markdown -o .ai/docs.txt
```

### روش ۴ — bundle کامل از لیست مشخص (لیست سفارشی)

**مناسب برای:** وقتی لیست دقیق فایل‌های موردنظر را دارید (مثل `md-list.txt`).

```bash
# از فایل لیست
python codemerge.py fetch --files-from md-list.txt -o .ai/bundle-custom.txt

# از stdin
Get-Content md-list.txt | python codemerge.py fetch --from-stdin -o .ai/bundle-custom.txt
```

این روش در پروژهٔ فعلی رایج‌ترین روش است، چون `md-list.txt` حاوی لیست دقیق ۴۷ فایل مهم پروژه است.

---

### هشدارها و محدودیت‌ها

> ⚠️ **خروجی می‌تواند بسیار بزرگ باشد.** برای پروژه‌های بالای ۵۰ فایل، خروجی ممکن است چند مگابایت شود.

> ⚠️ **از context window AI عبور می‌کند.** مدل‌های فعلی حدود ۱۲۸K توکن context دارند. یک پروژهٔ متوسط Node.js می‌تواند ۱۰۰K+ توکن باشد.

> ⚠️ **هزینهٔ API را زیاد می‌کند.** هر درخواست با bundle بزرگ، هزینهٔ ورودی را چند برابر می‌کند.

> ⚠️ **`--allow-sensitive` خطرناک است.** استفادهٔ نادرست از این فلگ باعث می‌شود `.env` و کلیدهای خصوصی وارد bundle شوند و برای AI فرستاده شوند.

**قاعدهٔ سرانگشتی:** اگر bundle بالای ۳۰,۰۰۰ توکن است، آن را به بخش‌های کوچک‌تر تقسیم کنید.

---

### تخمین حجم و هزینه قبل از تولید

**قبل از اینکه خروجی کامل بگیرید، اندازه را تخمین بزنید:**

```bash
# پیش‌نمایش لیست فایل‌هایی که وارد خروجی می‌شوند (بدون نوشتن فایل)
python codemerge.py diff --dry-run --full

# خروجی نمونه:
# [full] Would merge 47 file(s) into .ai/full_project.txt:
#   codemerge.py  (60,234 bytes)
#   docs/CHEATSHEET.md  (3,412 bytes)
#   ...
# Total changed size: 342,891 bytes
```

**بعد از تولید، توکن و هزینه را تخمین بزنید:**

```bash
# تخمین توکن (با tiktoken اگر نصب باشد)
python tools\estimate.py .ai/full_project.txt

# تخمین هزینه برای یک مدل خاص
python tools\estimate.py .ai/full_project.txt --model deepseek-chat
python tools\estimate.py .ai/full_project.txt --model gpt-4o
python tools\estimate.py .ai/full_project.txt --model claude-sonnet-4
```

---

### توصیه‌های عملی

| سناریو | روش پیشنهادی |
|---|---|
| پروژه کوچک (< ۳۰ فایل) | روش ۲ (`diff --full`) |
| پروژه متوسط (۳۰-۱۰۰ فایل) | روش ۱ (manifest) + روش ۴ (fetch انتخابی) |
| پروژه بزرگ (> ۱۰۰ فایل) | فقط روش ۱ (manifest) یا روش ۳ (فیلتر زبان) |
| پروژهٔ چندزبانه | روش ۳ (هر زبان جداگانه) |
| آرشیو یا backup | روش ۲ یا ۴ (بسته به نیاز) |
| ارسال اولیه به AI | روش ۱ (نقشه) → سپس درخواست AI → روش ۴ |

---

### ترکیب با `.codemergeignore`

قواعد `.codemergeignore` روی **همهٔ روش‌ها** اعمال می‌شود. مثلاً اگر `content/posts/` را ignore کرده باشید، در هیچ‌کدام از روش‌های بالا ظاهر نمی‌شود.

برای نادیده گرفتن قواعد ignore (مثلاً گرفتن bundle واقعاً کامل):

```bash
python codemerge.py diff --full --reset-state --no-ignore-file -o .ai/everything.txt
```

> ⚠️ استفاده از `--no-ignore-file` همراه با `--allow-sensitive` **بسیار خطرناک** است. فقط در محیط‌های بسیار کنترل‌شده استفاده کنید.

---

### چه چیزی همیشه حذف می‌شود (حتی در حالت full)

حتی با `--all-files`, این‌ها هرگز وارد bundle نمی‌شوند:

| دسته | مثال |
|---|---|
| پوشه‌های سیستمی | `.git`, `node_modules`, `__pycache__`, `dist`, `build` |
| lock files | `package-lock.json`, `yarn.lock`, `poetry.lock` |
| فایل‌های minified | `*.min.js`, `*.min.css`, `*.map` |
| فایل‌های باینری | تصاویر، فونت‌ها، فایل‌های فشرده |
| فایل‌های حساس | `.env`, `*.pem`, `*.key`, `id_rsa` |
| فایل‌های بزرگ | بالای `--max-size` (پیش‌فرض: 100 MB) |

برای شامل کردن فایل‌های حساس: `--allow-sensitive` (بسیار پرخطر).
برای فایل‌های باینری: هیچ راهی نیست — طراحی tool به‌عمد آن‌ها را حذف می‌کند.
برای lock files: `--include package-lock.json` (فقط force-include).

---

## گردش کار کامل با AI

### گام ۱ — آماده‌سازی

```powershell
# Snapshot قبل از شروع (اختیاری، ولی توصیه‌شده)
python tools\snapshot.py --label before-session

# ساخت manifest در فرمت Markdown
python codemerge.py manifest --format md -o .ai\manifest.md
```

### گام ۲ — ارسال promptها به AI

به ترتیب زیر promptها را کپی و به AI بفرستید:

1. `prompts/01-system.md` — قواعد پایه
2. `prompts/01-system-append-2.md` — قواعد ویرایش و فرمت خروجی
3. `prompts/02-manifest.md` + محتوای `.ai/manifest.md`
4. `prompts/Anti-AI-Slop/00-master-anti-slop.md` — قواعد ضد-Slop عمومی
5. `prompts/Expertise and Experience/00-anti-slop-core.md` — قواعد ضد-Slop پروژه
6. **حداکثر یکی** از `prompts/Expertise and Experience/XX-*.md` — تخصص موردنیاز
7. یکی از تسک‌ها: `prompts/03-bug-fix.md` تا `prompts/08-explain-code.md`

> **قاعدهٔ فولادی:** هرگز دو فایل تخصص را در یک نشست ترکیب نکنید.

### گام ۳ — دریافت درخواست AI

AI با این فرمت پاسخ می‌دهد:

````
```codemerge-fetch
lib/api/auth.ts
lib/api/client.ts
store/authStore.ts
```
````

شما این را با دستور زیر اجرا می‌کنید:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts store/authStore.ts -o .ai\bundle.txt
```

یا از فایل:

```powershell
# ذخیرهٔ لیست در requested.txt
python codemerge.py fetch --files-from requested.txt -o .ai\bundle.txt
```

### گام ۴ — ارسال bundle به AI

محتوای `.ai/bundle.txt` را در ادامهٔ گفتگو کپی کنید.

### گام ۵ — اعمال تغییرات AI

AI پاسخ را در این فرمت می‌دهد:

````
```file:lib/api/auth.ts
<محتوای کامل فایل>
```
````

پاسخ را در `ai_response.md` ذخیره کنید و:

```powershell
# پیش‌نمایش
python tools\apply_ai_output.py ai_response.md --dry-run

# اعمال
python tools\apply_ai_output.py ai_response.md

# بررسی سلامت
.\tools\verify.ps1
```

### گام ۶ — پایان نشست

```powershell
# ذخیرهٔ state برای diff آینده
python codemerge.py diff -o .ai\changes.txt

# خلاصهٔ نشست
python tools\session_summary.py --last 1
```

### گام ۷ — نشست بعدی

```powershell
# فقط تغییرات را به AI بفرستید
python codemerge.py diff -o .ai\changes.txt
```

همراه با `prompts/09-continue-session.md`.

---

## دستورات `codemerge.py`

### `manifest` — نقشهٔ پروژه

```bash
python codemerge.py manifest [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `--format {text,md,json}` | فرمت خروجی (پیش‌فرض: `text`) |
| `--no-symbols` | بدون توابع/کلاس‌ها |
| `--no-imports` | بدون imports |
| `--max-tokens N` | سقف نرم توکن |

**نمونه‌ها:**

```bash
# نقشهٔ کامل
python codemerge.py manifest -o .ai/manifest.txt

# فقط TypeScript
python codemerge.py manifest -l typescript -o .ai/manifest.txt

# فرمت Markdown (مناسب AI)
python codemerge.py manifest --format md -o .ai/manifest.md

# فشرده
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt
```

### `fetch` — دریافت محتوای فایل‌ها

```bash
python codemerge.py fetch FILES... [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `FILES ...` | مسیر فایل‌ها (نسبت به ریشه) |
| `--files-from FILE` | خواندن لیست از فایل |
| `--from-stdin` | خواندن لیست از stdin |

**نمونه‌ها:**

```bash
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt

python codemerge.py fetch --files-from requested.txt -o .ai/bundle.txt

Get-Content requested.txt | python codemerge.py fetch --from-stdin -o .ai/bundle.txt
```

### `diff` — فقط تغییرات

```bash
python codemerge.py diff [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `--state-file PATH` | مسیر state (پیش‌فرض: `<output>.state.json`) |
| `--full` | ادغام کامل |
| `--reset-state` | حذف state قبل از اجرا |
| `--dry-run` | فقط نمایش تغییرات |

**رفتار:**

| سناریو | نتیجه |
|---|---|
| اجرای اول | حالت `full` (کل پروژه) |
| بدون تغییر | `No changes since last run.` |
| فایل تغییر کرده | فقط همان فایل |
| فایل حذف شده | در هدر گزارش می‌شود |
| `.codemergeignore` تغییر کرد | خودکار به `full` سوییچ می‌کند |

### `search` — جستجوی نماد

```bash
python codemerge.py search PATTERN [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `PATTERN` | regex یا متن ساده |
| `--max-hits N` | حداکثر نتیجه (پیش‌فرض: 500) |

**نمونه:**

```bash
python codemerge.py search "handleLogin"
python codemerge.py search "function handle.*Login" -l typescript
python codemerge.py search UserRepository --output hits.txt
```

### `langs` — فهرست زبان‌ها

```bash
python codemerge.py langs
```

---

## گزینه‌های مشترک

همهٔ این‌ها در `manifest`, `fetch`, `diff`, `search` کار می‌کنند:

| گزینه | توضیح |
|---|---|
| `-l`, `--lang LANG [LANG ...]` | انتخاب زبان(ها) |
| `-o`, `--output FILE` | نام فایل خروجی |
| `-r`, `--root DIR` | ریشهٔ پروژه |
| `--max-size MB` | حداکثر حجم هر فایل (پیش‌فرض: 100) |
| `--no-git` | نادیده گرفتن Git |
| `--include PATTERN [...]` | الگوهای glob برای force-include |
| `--exclude PATTERN [...]` | الگوهای glob برای حذف |
| `--allow-sensitive` | شامل کردن فایل‌های حساس |
| `--all-files` | نادیده گرفتن فیلتر زبان |
| `--no-header` | بدون هدر در خروجی |
| `-q`, `--quiet` | عدم چاپ خلاصه |
| `--ignore-file PATH` | فایل ignore سفارشی |
| `--no-ignore-file` | نادیده گرفتن فایل‌های ignore |

---

## فایل ignore

فایل `.codemergeignore` در ریشهٔ پروژه با نحو gitignore:

```gitignore
# محتوای بلاگ
content/posts/
content/authors/

# فایل‌های backup
*.bak
*.tsbuildinfo

# خروجی‌های codemerge
manifest*.txt
project_source*.txt
codemerge.state.json

# استثنا
!content/README.md
```

**نحو پشتیبانی‌شده:**

| الگو | معنی |
|---|---|
| `docs/` | پوشه در هر عمق |
| `/config.json` | فقط در ریشه |
| `*.min.js` | glob |
| `**/snapshots/` | پوشه در هر عمق |
| `!docs/README.md` | استثنا |
| `# comment` | کامنت |

---

## فایل‌های حساس

این فایل‌ها **هرگز** در خروجی قرار نمی‌گیرند (مگر با `--allow-sensitive`):

- `.env` و نسخه‌هایش (به‌جز `.env.example`, `.env.sample`, `.env.template`, `.env.dist`)
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `credentials.json`, `secrets.json`, `service-account.json`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.ppk`, `*.secret`, `*.crt`
- `.netrc`, `.pypirc`, `.htpasswd`, `.pgpass`

---

## ساختار promptها

```
prompts/
├── 01-system.md                    ← قواعد پایه (فارسی)
├── 01-system-append-2.md           ← قواعد ویرایش (انگلیسی)
├── 02-manifest.md                  ← همراه با manifest
├── 03-bug-fix.md                   ← تسک: رفع باگ
├── 04-feature.md                   ← تسک: افزودن قابلیت
├── 05-refactor.md                  ← تسک: بازآرایی
├── 06-code-review.md               ← تسک: بررسی کد
├── 07-tests.md                     ← تسک: نوشتن تست
├── 08-explain-code.md              ← تسک: توضیح کد
├── 09-continue-session.md          ← ادامهٔ نشست
├── 10-recovery.md                  ← بازیابی وقتی AI از مسیر خارج شد
├── 11-limit-files.md               ← محدودسازی درخواست
├── 12-long-response.md             ← مدیریت پاسخ طولانی
├── 13-final-summary.md             ← خلاصهٔ پایانی
├── 14-checklist.md                 ← چک‌لیست
├── Anti-AI-Slop/
│   └── 00-master-anti-slop.md      ← قواعد ضد-Slop عمومی
├── Expertise and Experience/       ← تخصص‌ها (انگلیسی)
│   ├── 00-anti-slop-core.md
│   ├── 01-frontend-architecture.md
│   ├── 02-typescript.md
│   ├── ...
│   └── 12-accessibility.md
└── Expertise and Experience-FA/    ← تخصص‌ها (فارسی)
    └── (آینه‌سازی نسخهٔ انگلیسی)
```

هر فایل prompt با **YAML frontmatter** شروع می‌شود:

```yaml
---
id: 02-typescript
title: "TypeScript Expert"
lang: en
depends_on: []
category: expertise
version: 1
---
```

---

## ابزارهای کمکی

پوشهٔ `tools/` شامل این اسکریپت‌ها است:

| ابزار | کار |
|---|---|
| `snapshot.py` | Snapshot کامل پروژه قبل از ویرایش‌های بزرگ |
| `apply_ai_output.py` | اعمال خروجی AI (بلوک‌های `file:`) روی دیسک |
| `verify.ps1` / `verify.sh` | اجرای type-check، lint، تست، build |
| `new_session.py` | ساخت فایل session جدید |
| `session_summary.py` | چاپ خلاصهٔ sessionهای اخیر |
| `estimate.py` | تخمین توکن و هزینه |
| `watch.py` | اجرای خودکار `diff` با تغییر فایل |
| `log_metrics.py` | ثبت متریک گردش کار AI |
| `setup_profile.ps1` | نصب shortcutهای PowerShell |
| `add_frontmatter.py` | افزودن YAML frontmatter به promptها |
| `fix_frontmatter_lang.py` | تصحیح `lang` در frontmatter |
| `diagnose_cheatsheet.py` | تشخیص نبود فایل در bundle |

### نمونهٔ استفاده

```powershell
# Snapshot
python tools\snapshot.py --label before-ai
python tools\snapshot.py --list
python tools\snapshot.py --restore before-ai

# اعمال خروجی AI
python tools\apply_ai_output.py ai_response.md --dry-run
python tools\apply_ai_output.py ai_response.md

# Verify
.\tools\verify.ps1
.\tools\verify.ps1 -SkipTests
.\tools\verify.ps1 -Only "type-check","lint"

# Session
python tools\new_session.py "auth refactor" --prev 02
python tools\session_summary.py --last 3

# تخمین هزینه
python tools\estimate.py .ai\bundle.txt --model deepseek-chat
```

---

## تست

پروژه دارای تست واحد است:

```bash
# اجرای تست‌ها
python -m unittest discover -s tests -v

# یا مستقیم
python tests/test_codemerge.py

# یا با pytest (توصیه‌شده)
pip install pytest
pytest tests/ -v
```

پوشش تست‌ها:

- `is_sensitive` — تشخیص فایل‌های حساس
- `IgnoreMatcher` — الگوهای gitignore
- `extract_python` — استخراج نمادهای پایتون (AST)
- `_extract_js` — استخراج JS/TS (شامل generic سه‌سطحی، arrow با return object)
- `write_bundle` — نوشتن bundle با/بدون header
- `compute_delta` — محاسبهٔ تغییرات diff
- `detect_lang` — تشخیص زبان از extension

---

## عیب‌یابی

### `No source files found`

- زبان انتخابی اشتباه است → `python codemerge.py langs`
- همهٔ فایل‌ها در `.codemergeignore` → با `--no-ignore-file` امتحان کنید
- با `--all-files` امتحان کنید

### `Unknown language: xxx`

نام زبان را با `python codemerge.py langs` چک کنید.

### فایل در manifest هست ولی در fetch رد می‌شود

- احتمالاً باینری است
- یا حجمش از `--max-size` بیشتر است
- یا مسیر را نسبت به ریشه اشتباه داده‌اید

### `diff` همیشه full است

- state ذخیره نشده → مسیر نوشتن آن را بررسی کنید
- `--root` بین دو اجرا تغییر کرده

### خروجی خیلی بزرگ است

```bash
# manifest کوچک‌تر
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt

# با محدودیت توکن
python codemerge.py manifest --max-tokens 8000 -o .ai/manifest.txt

# فقط یک زبان
python codemerge.py diff --full -l typescript -o .ai/ts.txt
```

### شمارش توکن دقیق نیست

```bash
pip install tiktoken
```

### در PowerShell دستور `grep` کار نمی‌کند

از `Select-String` استفاده کنید:

```powershell
Select-String -Path .ai\manifest.txt -Pattern "apiGet"
(Select-String -Path .ai\manifest.txt -Pattern "^  function ").Count
```

### نمایش فارسی در PowerShell به‌هم‌ریخته است

PowerShell 5.1 به‌طور پیش‌فرض UTF-8 نمی‌خواند. از `-Encoding UTF8` استفاده کنید:

```powershell
Get-Content prompts\01-system.md -Encoding UTF8
```

یا PowerShell 7+ نصب کنید.

---

## ساختار پروژه

```
CodeCompactForAI/
├── codemerge.py                    ← ابزار اصلی
├── README.md                       ← همین فایل
├── md-list.txt                     ← لیست فایل‌های مهم
├── .codemergeignore                ← قواعد ignore
│
├── docs/
│   ├── CHEATSHEET.md
│   └── codemerge.md                ← راهنمای کامل فارسی
│
├── prompts/                        ← promptهای AI
│   ├── 01-system.md
│   ├── 01-system-append-2.md
│   ├── 02-manifest.md
│   ├── 03..08-*.md
│   ├── 09..14-*.md
│   ├── Anti-AI-Slop/
│   ├── Expertise and Experience/
│   └── Expertise and Experience-FA/
│
├── tools/                          ← ابزارهای کمکی
│   ├── snapshot.py
│   ├── apply_ai_output.py
│   ├── verify.ps1 / verify.sh
│   ├── new_session.py
│   ├── session_summary.py
│   ├── estimate.py
│   ├── watch.py
│   ├── log_metrics.py
│   ├── setup_profile.ps1
│   ├── add_frontmatter.py
│   ├── fix_frontmatter_lang.py
│   └── diagnose_cheatsheet.py
│
└── tests/
    └── test_codemerge.py
```

---

## مجوز

MIT

## سازگاری

- Python 3.9+
- ویندوز، macOS، Linux
- Bash، PowerShell، cmd
