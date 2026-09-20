# CodeCompactForAI

**مطالعه به:** [English](README.md) · [فارسی](README.fa.md)

ابزار خط فرمان برای آماده‌سازی پروژه‌های نرم‌افزاری جهت ارسال به مدل‌های هوش مصنوعی — بدون فرستادن کل پروژه.

به جای ارسال کل کدبیس، یک **نقشهٔ فشرده** ارسال می‌کنید و هوش مصنوعی خودش تصمیم می‌گیرد کدام فایل‌ها را لازم دارد. نتیجه: **کاهش ۱۰ تا ۵۰ برابری** حجم ارسال، هزینه کمتر و پاسخ دقیق‌تر.

## فهرست

- [پیش‌نیازها](#پیشنیازها)
- [شروع سریع](#شروع-سریع)
- [تولید خروجی از کل پروژه](#تولید-خروجی-از-کل-پروژه)
- [گردش کار کامل با AI](#گردش-کار-کامل-با-ai)
- [دستورات](#دستورات)
- [گزینه‌های مشترک](#گزینههای-مشترک)
- [فایل ignore](#فایل-ignore)
- [فایل‌های حساس](#فایلهای-حساس)
- [ساختار promptها](#ساختار-promptها)
- [ابزارهای کمکی](#ابزارهای-کمکی)
- [تست](#تست)
- [عیب‌یابی](#عیبیابی)
- [ساختار پروژه](#ساختار-پروژه)
- [مجوز](#مجوز)
- [سازگاری](#سازگاری)

## پیش‌نیازها

- **Python 3.9 یا بالاتر** (3.11+ توصیه می‌شود)
- **Git** (اختیاری، ولی توصیه می‌شود)
- **tiktoken** (اختیاری، برای شمارش دقیق توکن)

```bash
pip install tiktoken    # اختیاری
```

## شروع سریع

هیچ نصب لازم نیست. کافیست پروژه را کپی کنید و دستورات را اجرا کنید.

```bash
# بررسی سلامت ابزار
python codemerge.py --help
python codemerge.py langs

# ساخت نقشهٔ فشردهٔ پروژه
python codemerge.py manifest --format md -o .ai/manifest.md

# ارسال .ai/manifest.md به AI همراه با promptهای مربوطه
# بعد از درخواست فایل توسط AI، دریافت محتوای آن‌ها
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

سپس `.ai/bundle.txt` را به AI بفرستید.

## تولید خروجی از کل پروژه

در بعضی موارد نیاز دارید کل پروژه در یک فایل باشد: بارگذاری اولیه برای AI، backup یا بررسی آفلاین. `codemerge.py` **چهار روش** برای این کار دارد.

### روش ۱ — فقط نقشه (مسیرها + نمادها)

ساختار پروژه را بدون محتوای فایل‌ها ارسال می‌کند.

```bash
# متن
python codemerge.py manifest --all-files -o .ai/manifest-full.txt

# Markdown
python codemerge.py manifest --all-files --format md -o .ai/manifest-full.md

# JSON
python codemerge.py manifest --all-files --format json -o .ai/manifest-full.json

# بدون نمادها و imports
python codemerge.py manifest --all-files --no-symbols --no-imports -o .ai/files-list.txt
```

`--all-files` فیلتر زبان را نادیده می‌گیرد.

اندازه معمول: برای ۲۰۰ فایل، حدود ۱۰ تا ۳۰ کیلوبایت.

### روش ۲ — bundle کامل محتوا

متن همهٔ فایل‌های انتخاب‌شده را شامل می‌شود.

```bash
# اجرای اول — diff برابر کل پروژه است
python codemerge.py diff -o .ai/full_project.txt

# اگر قبلاً diff اجرا کرده‌اید و می‌خواهید دوباره کل پروژه را بگیرید
python codemerge.py diff --full --reset-state -o .ai/full_project.txt

# بدون هدر (فقط محتوای فایل‌ها)
python codemerge.py diff --full --reset-state --no-header -o .ai/full_project.txt
```

`fetch` نیاز به لیست صریح فایل‌ها دارد، بنابراین برای «کل پروژه» مناسب نیست. `diff --full` به‌طور خودکار همه فایل‌ها را انتخاب می‌کند.

### روش ۳ — bundle با فیلتر زبان

برای پروژه‌های چندزبانه که می‌خواهید فقط یک زبان را داشته باشید.

```bash
# فقط TypeScript / JavaScript
python codemerge.py diff --full --reset-state -l typescript,javascript -o .ai/ts-only.txt

# فقط Python
python codemerge.py diff --full --reset-state -l python -o .ai/backend.txt

# فقط Markdown
python codemerge.py diff --full --reset-state -l markdown -o .ai/docs.txt
```

### روش ۴ — لیست سفارشی

برای مواردی که لیست دقیق فایل‌ها را دارید (مثل `md-list.txt`).

```bash
# از فایل لیست
python codemerge.py fetch --files-from md-list.txt -o .ai/bundle-custom.txt

# از stdin
Get-Content md-list.txt | python codemerge.py fetch --from-stdin -o .ai/bundle-custom.txt
```

### هشدارها

خروجی‌های بزرگ می‌توانند از پنجرهٔ context AI عبور کنند. اکثر مدل‌های فعلی حدود ۱۲۸K توکن limit دارند و یک پروژهٔ Node.js می‌تواند ۱۰۰K+ توکن باشد. همچنین هر bundle بزرگ هزینهٔ ورودی API را چند برابر می‌کند. به عنوان قاعدهٔ عملی، اگر bundle از ۳۰,۰۰۰ توکن بیشتر شد، آن را به قسمت‌های کوچک‌تر تقسیم کنید.

فلگ `--allow-sensitive` فایل‌های `.env`، کلیدهای خصوصی و سایر اعتبارنامه‌ها را در bundle قرار می‌دهد. فقط زمانی استفاده کنید که مطمئن باشید خروجی به طرف ثالثی ارسال نمی‌شود.

### تخمین حجم و هزینه

قبل از تولید bundle کامل، پیش‌نمایش کنید که کدام فایل‌ها وارد خروجی می‌شوند:

```bash
python codemerge.py diff --dry-run --full
```

نمونه خروجی:

```text
[full] Would merge 47 file(s) into .ai/full_project.txt:
  codemerge.py  (60,234 bytes)
  docs/CHEATSHEET.md  (3,412 bytes)
  ...
Total changed size: 342,891 bytes
```

بعد از تولید، توکن و هزینه را تخمین بزنید:

```bash
python tools/estimate.py .ai/full_project.txt
python tools/estimate.py .ai/full_project.txt --model deepseek-chat
python tools/estimate.py .ai/full_project.txt --model gpt-4o
```

### توصیه‌ها

| سناریو | روش |
|---|---|
| پروژه کوچک (کمتر از ۳۰ فایل) | روش ۲ (`diff --full`) |
| پروژه متوسط (۳۰ تا ۱۰۰ فایل) | روش ۱، سپس روش ۴ |
| پروژه بزرگ (بیش از ۱۰۰ فایل) | روش ۱، یا روش ۳ |
| پروژه چندزبانه | روش ۳، یک زبان در هر بار |
| آرشیو یا backup | روش ۲ یا ۴ |
| ارسال اولیه به AI | روش ۱، سپس روش ۴ |

### ترکیب با `.codemergeignore`

قواعد `.codemergeignore` روی **همهٔ روش‌ها** اعمال می‌شود. برای نادیده گرفتن آن‌ها:

```bash
python codemerge.py diff --full --reset-state --no-ignore-file -o .ai/everything.txt
```

ترکیب `--no-ignore-file` با `--allow-sensitive` همهٔ فایل‌های پروژه، شامل اعتبارنامه‌ها را وارد bundle می‌کند. این کار باید اجتناب شود.

### فایل‌هایی که همیشه حذف می‌شوند

حتی با `--all-files`، این‌ها هرگز وارد bundle نمی‌شوند:

| دسته | مثال‌ها |
|---|---|
| پوشه‌های سیستمی | `.git`, `node_modules`, `__pycache__`, `dist`, `build` |
| فایل‌های قفل | `package-lock.json`, `yarn.lock`, `poetry.lock` |
| فایل‌های minified | `*.min.js`, `*.min.css`, `*.map` |
| فایل‌های باینری | تصاویر، فونت‌ها، آرشیوها |
| فایل‌های حساس | `.env`, `*.pem`, `*.key`, `id_rsa` |
| فایل‌های بزرگ | بیشتر از `--max-size` (پیش‌فرض: ۱۰۰ مگابایت) |

برای شامل کردن فایل‌های حساس از `--allow-sensitive` استفاده کنید. فایل‌های باینری به‌طور عمدی قابل شامل نیستند. فایل‌های قفل را می‌توان با `--include package-lock.json` وارد کرد.

## گردش کار کامل با AI

### گام ۱ — آماده‌سازی

```powershell
# اختیاری، ولی توصیه می‌شود: snapshot قبل از شروع
python tools/snapshot.py --label before-session

# ساخت نقشه
python codemerge.py manifest --format md -o .ai/manifest.md
```

### گام ۲ — ارسال promptها به AI

در این ترتیب promptها را ارسال کنید:

1. `prompts/01-system.md` — قواعد پایه
2. `prompts/01-system-append-2.md` — قواعد ویرایش و فرمت خروجی
3. `prompts/02-manifest.md` به همراه محتوای `.ai/manifest.md`
4. `prompts/Anti-AI-Slop/00-master-anti-slop.md` — قواعد ضد-Slop عمومی
5. `prompts/Expertise and Experience/00-anti-slop-core.md` — قواعد ضد-Slop پروژه
6. **حداکثر یکی** از `prompts/Expertise and Experience/XX-*.md`
7. یک prompt تسک: `prompts/03-bug-fix.md` تا `prompts/08-explain-code.md`

در هر نشست فقط از یک فایل تخصص استفاده کنید. ترکیب دو فایل تخصص می‌تواند باعث شود AI راهنمایی ناسازگار دریافت کند.

### گام ۳ — دریافت درخواست فایل از AI

AI پاسخ می‌دهد:

```
```codemerge-fetch
lib/api/auth.ts
lib/api/client.ts
store/authStore.ts
```
```

اجرا کنید:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts store/authStore.ts -o .ai/bundle.txt

# یا از فایل
python codemerge.py fetch --files-from requested.txt -o .ai/bundle.txt
```

### گام ۴ — ارسال bundle به AI

محتوای `.ai/bundle.txt` را در گفتگو پیست کنید.

### گام ۵ — اعمال تغییرات AI

پاسخ AI را در `ai_response.md` ذخیره کنید، سپس:

```powershell
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md
.\tools\verify.ps1
```

### گام ۶ — پایان نشست

```powershell
python codemerge.py diff -o .ai/changes.txt
python tools/session_summary.py --last 1
```

### گام ۷ — نشست بعدی

```powershell
python codemerge.py diff -o .ai/changes.txt
```

همراه با `prompts/09-continue-session.md` ارسال کنید.

## دستورات

### manifest — نقشهٔ پروژه

```bash
python codemerge.py manifest [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `--format {text,md,json}` | فرمت خروجی (پیش‌فرض: text) |
| `--no-symbols` | حذف توابع و کلاس‌ها |
| `--no-imports` | حذف imports |
| `--max-tokens N` | سقف نرم توکن |

نمونه‌ها:

```bash
python codemerge.py manifest -o .ai/manifest.txt
python codemerge.py manifest -l typescript -o .ai/manifest.txt
python codemerge.py manifest --format md -o .ai/manifest.md
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt
```

### fetch — دریافت محتوای فایل‌ها

```bash
python codemerge.py fetch FILES... [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `FILES ...` | مسیر فایل‌ها نسبت به ریشهٔ پروژه |
| `--files-from FILE` | خواندن مسیرها از فایل |
| `--from-stdin` | خواندن مسیرها از stdin |

نمونه‌ها:

```bash
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
python codemerge.py fetch --files-from requested.txt -o .ai/bundle.txt
Get-Content requested.txt | python codemerge.py fetch --from-stdin -o .ai/bundle.txt
```

### diff — فقط تغییرات

```bash
python codemerge.py diff [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `--state-file PATH` | مسیر فایل state (پیش‌فرض: `<output>.state.json`) |
| `--full` | اجبار به ادغام کامل |
| `--reset-state` | حذف فایل state قبل از اجرا |
| `--dry-run` | نمایش تغییرات بدون نوشتن |

رفتار:

| سناریو | نتیجه |
|---|---|
| اجرای اول | حالت کامل (full) |
| بدون تغییر | پیام `No changes since last run.` |
| فایل تغییر کرده | فقط همان فایل |
| فایل حذف شده | در هدر گزارش می‌شود |
| `.codemergeignore` تغییر کرد | به‌طور خودکار به حالت full سوییچ می‌کند |

### search — جستجوی نماد

```bash
python codemerge.py search PATTERN [OPTIONS]
```

| گزینه | توضیح |
|---|---|
| `PATTERN` | regex یا متن ساده |
| `--max-hits N` | حداکثر نتیجه (پیش‌فرض: ۵۰۰) |

نمونه‌ها:

```bash
python codemerge.py search "handleLogin"
python codemerge.py search "function handle.*Login" -l typescript
python codemerge.py search UserRepository --output hits.txt
```

### langs — فهرست زبان‌ها

```bash
python codemerge.py langs
```

## گزینه‌های مشترک

این گزینه‌ها در `manifest`, `fetch`, `diff` و `search` کار می‌کنند:

| گزینه | توضیح |
|---|---|
| `-l`, `--lang LANG [LANG ...]` | فیلتر زبان |
| `-o`, `--output FILE` | فایل خروجی |
| `-r`, `--root DIR` | ریشهٔ پروژه |
| `--max-size MB` | حداکثر حجم فایل (پیش‌فرض: ۱۰۰) |
| `--no-git` | نادیده گرفتن Git |
| `--include PATTERN [...]` | الگوهای glob برای شامل کردن اجباری |
| `--exclude PATTERN [...]` | الگوهای glob برای حذف |
| `--allow-sensitive` | شامل کردن فایل‌های حساس |
| `--all-files` | نادیده گرفتن فیلتر زبان |
| `--no-header` | بدون هدر در خروجی |
| `-q`, `--quiet` | عدم نمایش خلاصه |
| `--ignore-file PATH` | فایل ignore سفارشی |
| `--no-ignore-file` | نادیده گرفتن فایل‌های ignore |

## فایل ignore

فایل `.codemergeignore` در ریشهٔ پروژه با نحو gitignore کار می‌کند:

```gitignore
# محتوای بلاگ
content/posts/
content/authors/

# فایل‌های پشتیبان
*.bak
*.tsbuildinfo

# خروجی‌های codemerge
manifest*.txt
project_source*.txt
codemerge.state.json

# استثنا
!content/README.md
```

الگوهای پشتیبانی‌شده:

| الگو | معنی |
|---|---|
| `docs/` | پوشه در هر عمق |
| `/config.json` | فقط در ریشه |
| `*.min.js` | glob |
| `**/snapshots/` | پوشه در هر عمق |
| `!docs/README.md` | استثنا |
| `# comment` | کامنت |

## فایل‌های حساس

این فایل‌ها **هرگز** در خروجی قرار نمی‌گیرند (مگر با `--allow-sensitive`):

- `.env` و نسخه‌هایش، به‌جز `.env.example`، `.env.sample`، `.env.template`، `.env.dist`
- `id_rsa`، `id_dsa`، `id_ecdsa`، `id_ed25519`
- `credentials.json`، `secrets.json`، `service-account.json`
- `*.pem`، `*.key`، `*.p12`، `*.pfx`، `*.jks`، `*.keystore`، `*.ppk`، `*.secret`، `*.crt`
- `.netrc`، `.pypirc`، `.htpasswd`، `.pgpass`

## ساختار promptها

```
prompts/
├── 01-system.md                    base rules (Persian)
├── 01-system-append-2.md           editing rules (English)
├── 02-manifest.md                  used with the manifest
├── 03-bug-fix.md                   task: bug fix
├── 04-feature.md                   task: add feature
├── 05-refactor.md                  task: refactor
├── 06-code-review.md               task: code review
├── 07-tests.md                     task: write tests
├── 08-explain-code.md              task: explain code
├── 09-continue-session.md          continue session
├── 10-recovery.md                  recovery when the AI goes off track
├── 11-limit-files.md               limit request scope
├── 12-long-response.md             manage long responses
├── 13-final-summary.md             final summary
├── 14-checklist.md                 checklist
├── Anti-AI-Slop/
│   └── 00-master-anti-slop.md      general anti-slop rules
├── Expertise and Experience/       expertise files (English)
│   ├── 00-anti-slop-core.md
│   ├── 01-frontend-architecture.md
│   ├── 02-typescript.md
│   └── ...
└── Expertise and Experience-FA/    expertise files (Persian)
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

## ابزارهای کمکی

اسکریپت‌های پوشه `tools/`:

| ابزار | توضیح |
|---|---|
| `snapshot.py` | عکس کامل پروژه قبل از ویرایش‌های بزرگ |
| `apply_ai_output.py` | اعمال بلوک‌های `file:` AI روی دیسک |
| `verify.ps1` / `verify.sh` | اجرای type-check، lint، تست و build |
| `new_session.py` | ساخت فایل session جدید |
| `session_summary.py` | چاپ خلاصهٔ sessionهای اخیر |
| `estimate.py` | تخمین توکن و هزینه |
| `watch.py` | اجرای خودکار `diff` با تغییر فایل‌ها |
| `log_metrics.py` | ثبت متریک‌های گردش کار AI |
| `setup_profile.ps1` | نصب میانبرهای PowerShell |
| `add_frontmatter.py` | افزودن YAML frontmatter به promptها |
| `fix_frontmatter_lang.py` | تصحیح `lang` در frontmatter |
| `diagnose_cheatsheet.py` | تشخیص نبود فایل در bundle |

نمونه‌های استفاده:

```powershell
# Snapshot
python tools/snapshot.py --label before-ai
python tools/snapshot.py --list
python tools/snapshot.py --restore before-ai

# اعمال خروجی AI
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md

# بررسی سلامت
.\tools\verify.ps1
.\tools\verify.ps1 -SkipTests
.\tools\verify.ps1 -Only "type-check","lint"

# Session
python tools/new_session.py "auth refactor" --prev 02
python tools/session_summary.py --last 3

# تخمین هزینه
python tools/estimate.py .ai/bundle.txt --model deepseek-chat
```

## تست

```bash
# کتابخانه استاندارد
python -m unittest discover -s tests -v
python tests/test_codemerge.py

# با pytest (توصیه می‌شود)
pip install pytest
pytest tests/ -v
```

تست‌های پوشش داده شده: `is_sensitive`، `IgnoreMatcher`، `extract_python`، `_extract_js`، `write_bundle`، `compute_delta` و `detect_lang`.

## عیب‌یابی

### No source files found

- زبان انتخابی را با `python codemerge.py langs` بررسی کنید.
- همه فایل‌ها در `.codemergeignore` هستند → `--no-ignore-file` را امتحان کنید.
- `--all-files` را امتحان کنید.

### Unknown language: xxx

`python codemerge.py langs` را اجرا کنید.

### File exists in manifest but fetch rejects it

فایل احتمالاً باینری است، یا حجمش از `--max-size` بیشتر است، یا مسیر را نسبت به ریشه اشتباه داده‌اید.

### diff always produces full output

فایل state قابل نوشتن نیست، یا `--root` بین دو اجرا تغییر کرده.

### Output is too large

```bash
python codemerge.py manifest --no-symbols --no-imports -o .ai/files.txt
python codemerge.py manifest --max-tokens 8000 -o .ai/manifest.txt
python codemerge.py diff --full -l typescript -o .ai/ts.txt
```

### Token count is inaccurate

```bash
pip install tiktoken
```

### grep does not work in PowerShell

از `Select-String` استفاده کنید:

```powershell
Select-String -Path .ai/manifest.txt -Pattern "apiGet"
(Select-String -Path .ai/manifest.txt -Pattern "^  function ").Count
```

### Persian text is garbled in PowerShell

PowerShell 5.1 به‌طور پیش‌فرض UTF-8 نمی‌خواند.

```powershell
Get-Content prompts/01-system.md -Encoding UTF8
```

یا PowerShell 7 یا بالاتر نصب کنید.

## ساختار پروژه

```
CodeCompactForAI/
├── codemerge.py
├── README.md
├── README.fa.md
├── md-list.txt
├── .codemergeignore
│
├── docs/
│   ├── CHEATSHEET.md
│   └── codemerge.md
│
├── prompts/
│   ├── 01-system.md
│   ├── 01-system-append-2.md
│   ├── 02-manifest.md
│   ├── 03-bug-fix.md through 08-explain-code.md
│   ├── 09-continue-session.md through 14-checklist.md
│   ├── Anti-AI-Slop/
│   ├── Expertise and Experience/
│   └── Expertise and Experience-FA/
│
├── tools/
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

## مجوز

MIT

## سازگاری

- Python 3.9 یا بالاتر
- ویندوز، macOS، لینوکس
- Bash، PowerShell، cmd
