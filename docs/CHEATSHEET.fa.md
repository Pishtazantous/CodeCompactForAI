# راهنمای سریع گردش کار codemerge

مرجع یک‌صفحه‌ای برای گردش کار با کمک هوش مصنوعی.

## قبل از هر نشست

```powershell
python tools/snapshot.py --label before-session
python tools/new_session.py "short task title" --prev 0N
python codemerge.py manifest --format md -o .ai/manifest.md
```

## ترتیب پرامپت (در چت AI پیست کنید)

1. `prompts/01-system.md`
2. `prompts/02-manifest.md` + محتوای `.ai/manifest.md`
3. `prompts/Anti-AI-Slop/00-master-anti-slop.md`
4. `prompts/Expertise and Experience/00-anti-slop-core.md`
5. `prompts/Expertise and Experience/XX-topic.md` (اختیاری، حداکثر یکی)
6. `prompts/03-bug-fix.md` یا پرامپت تسک مربوطه

## وقتی AI فایل‌ها را درخواست می‌کند

AI این خروجی را می‌دهد:

    ```codemerge-fetch
    lib/api/auth.ts
    lib/api/client.ts
    ```

اجرا کنید:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

سپس `.ai/bundle.txt` را در چت پیست کنید.

## بعد از پاسخ AI

```powershell
# 1. پاسخ را در یک فایل ذخیره کنید (در ai_response.md پیست کنید)

# 2. تخمین هزینه (اختیاری)
python tools/estimate.py ai_response.md

# 3. پیش‌نمایش تغییرات
python tools/apply_ai_output.py ai_response.md --dry-run

# 4. اعمال
python tools/apply_ai_output.py ai_response.md

# 5. بررسی سلامت
.\tools\verify.ps1
```

## اگر چیزی خراب شد

```powershell
python tools/snapshot.py --list
python tools/snapshot.py --restore before-session
```

## پایان نشست

```powershell
# 1. بخش "Summary for Next Session" را در
#    .ai/sessions/<NN>-<slug>.md پر کنید

# 2. خلاصه را برای مرجع چاپ کنید
python tools/session_summary.py --last 1

# 3. ثبت متریک (اختیاری)
python tools/log_metrics.py --task "feature" --files-changed 5 \
    --slop-count 1 --time-saved 45
```

## نشست بعدی

```powershell
python codemerge.py diff -o .ai/changes.txt
python tools/session_summary.py --last 2
```

سپس هر دو فایل را با `prompts/09-continue-session.md` ارسال کنید.

## دستورات رایج codemerge

| کار | دستور |
|---|---|
| manifest کامل | `python codemerge.py manifest -o manifest.txt` |
| فقط TS | `python codemerge.py manifest -l typescript -o manifest.txt` |
| manifest فشرده | `python codemerge.py manifest --no-symbols --no-imports -o files.txt` |
| Fetch فایل‌ها | `python codemerge.py fetch f1.ts f2.ts -o bundle.txt` |
| Fetch از لیست | `python codemerge.py fetch --files-from list.txt -o bundle.txt` |
| Diff | `python codemerge.py diff -o changes.txt` |
| Diff پیش‌نمایش | `python codemerge.py diff --dry-run` |
| جستجوی نماد | `python codemerge.py search "functionName"` |
| فهرست زبان‌ها | `python codemerge.py langs` |

## بودجه توکن (تقریبی)

| محتوا | توکن |
|---|---|
| manifest کامل (200 فایل) | ~۱۸,۰۰۰ |
| manifest فشرده | ~۴,۰۰۰ |
| Fetch ۵ فایل | ~۵,۰۰۰–۲۰,۰۰۰ |
| Diff ۱۰ فایل تغییر یافته | ~۱,۰۰۰–۵,۰۰۰ |

**قاعدهٔ عملی:** اگر bundle بالای ۳۰,۰۰۰ توکن باشد، تسک را تقسیم کنید.

## مرجع سریع ابزارها

| ابزار | هدف |
|---|---|
| `tools/snapshot.py` | عکس کامل پروژه قبل از ویرایش‌ها |
| `tools/apply_ai_output.py` | اعمال بلوک‌های `file:` AI روی دیسک |
| `tools/verify.ps1` / `.sh` | اجرای type-check، lint، test، build |
| `tools/new_session.py` | شروع یک فایل نشست جدید |
| `tools/session_summary.py` | چاپ خلاصه‌های نشست‌های اخیر |
| `tools/estimate.py` | تخمین توکن و هزینه |
| `tools/watch.py` | اجرای خودکار diff هنگام تغییر فایل‌ها |
| `tools/log_metrics.py` | ثبت متریک‌های گردش کار AI |

## عیب‌یابی

| علت | راه‌حل |
|---|---|
| `No source files found` | `--lang` را بررسی کنید؛ `--all-files` را امتحان کنید |
| AI فایل‌های زیادی درخواست می‌کند | `prompts/11-limit-files.md` را ارسال کنید |
| AI فرمت را فراموش کرده | `prompts/10-recovery.md` را ارسال کنید |
| `diff` همیشه full است | قابلیت نوشتن `.ai/state.json` را بررسی کنید |
| Bundle خیلی بزرگ است | از `--no-symbols --no-imports` استفاده کنید |
| نیاز به بازگردانی | `python tools/snapshot.py --restore <name>` |
