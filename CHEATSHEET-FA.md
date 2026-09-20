# برگهٔ تقلب گردش‌کار codemerge

مرجع یک‌صفحه‌ای برای گردش‌کار کمک‌گرفته از هوش مصنوعی.

## قبل از هر نشست

```powershell
python tools/snapshot.py --label before-session
python tools/new_session.py "عنوان کوتاه تسک" --prev 0N
python codemerge.py manifest --format md -o .ai/manifest.md
```

## ترتیب پرامپت‌ها (در گفتگوی AI پیست کنید)

1. `prompts/01-system.md`
2. `prompts/02-manifest.md` + محتوای `.ai/manifest.md`
3. `prompts/Anti-AI-Slop/00-master-anti-slop.md`
4. `prompts/Expertise and Experience/00-anti-slop-core.md`
5. `prompts/Expertise and Experience/XX-topic.md` (اختیاری، فقط یکی)
6. `prompts/03-bug-fix.md` یا پرامپت مرتبط با تسک

## وقتی AI درخواست فایل می‌کند

خروجی AI به این شکل است:

    ```codemerge-fetch
    lib/api/auth.ts
    lib/api/client.ts
    ```

اجرا کنید:

```powershell
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o .ai/bundle.txt
```

سپس `.ai/bundle.txt` را در گفتگو پیست کنید.

## پس از پاسخ AI

```powershell
# ۱. پاسخ را در یک فایل ذخیره کنید (در ai_response.md پیست کنید)

# ۲. برآورد هزینه (اختیاری)
python tools/estimate.py ai_response.md

# ۳. پیش‌نمایش تغییرات
python tools/apply_ai_output.py ai_response.md --dry-run

# ۴. اعمال تغییرات
python tools/apply_ai_output.py ai_response.md

# ۵. بررسی پروژه
.\tools\verify.ps1
```

## اگر چیزی خراب شد

```powershell
python tools/snapshot.py --list
python tools/snapshot.py --restore before-session
```

## پایان نشست

```powershell
# ۱. بخش "Summary for Next Session" را در فایل زیر تکمیل کنید
#    .ai/sessions/<NN>-<slug>.md

# ۲. خلاصه را برای مراجعه بعدی چاپ کنید
python tools/session_summary.py --last 1

# ۳. متریک‌ها را ثبت کنید (اختیاری)
python tools/log_metrics.py --task "feature" --files-changed 5 \
    --slop-count 1 --time-saved 45
```

## نشست بعدی

```powershell
python codemerge.py diff -o .ai/changes.txt
python tools/session_summary.py --last 2
```

سپس هر دو فایل را همراه `prompts/09-continue-session.md` ارسال کنید.

## دستورات رایج codemerge

| وظیفه | دستور |
|---|---|
| Manifest کامل | `python codemerge.py manifest -o manifest.txt` |
| فقط TypeScript | `python codemerge.py manifest -l typescript -o manifest.txt` |
| Manifest فشرده | `python codemerge.py manifest --no-symbols --no-imports -o files.txt` |
| دریافت فایل‌ها | `python codemerge.py fetch f1.ts f2.ts -o bundle.txt` |
| دریافت از فایل لیست | `python codemerge.py fetch --files-from list.txt -o bundle.txt` |
| Diff | `python codemerge.py diff -o changes.txt` |
| پیش‌نمایش diff | `python codemerge.py diff --dry-run` |
| جستجوی نماد | `python codemerge.py search "functionName"` |
| فهرست زبان‌ها | `python codemerge.py langs` |

## بودجهٔ توکن (تقریبی)

| محتوا | توکن |
|---|---|
| Manifest کامل (۲۰۰ فایل) | حدود ۱۸٬۰۰۰ |
| Manifest فشرده | حدود ۴٬۰۰۰ |
| دریافت ۵ فایل | حدود ۵٬۰۰۰ تا ۲۰٬۰۰۰ |
| Diff برای ۱۰ فایل تغییرکرده | حدود ۱٬۰۰۰ تا ۵٬۰۰۰ |

**قاعدهٔ کلی:** اگر bundle از ۳۰٬۰۰۰ توکن بیشتر شد، تسک را به بخش‌های کوچک‌تر تقسیم کنید.

## مرجع سریع ابزارها

| ابزار | کاربرد |
|---|---|
| `tools/snapshot.py` | گرفتن snapshot کامل پروژه قبل از ویرایش |
| `tools/apply_ai_output.py` | اعمال بلاک‌های `file:` خروجی AI روی دیسک |
| `tools/verify.ps1` / `.sh` | اجرای type-check، lint، تست و build |
| `tools/new_session.py` | ایجاد فایل نشست جدید |
| `tools/session_summary.py` | چاپ خلاصهٔ نشست‌های اخیر |
| `tools/estimate.py` | برآورد تعداد توکن و هزینه |
| `tools/watch.py` | اجرای خودکار diff هنگام تغییر فایل‌ها |
| `tools/log_metrics.py` | پایش متریک‌های گردش‌کار AI |

## عیب‌یابی

| نشانه | راه‌حل |
|---|---|
| `No source files found` | مقدار `--lang` را بررسی کنید؛ `--all-files` را امتحان کنید |
| AI فایل‌های زیادی درخواست می‌کند | `prompts/11-limit-files.md` را ارسال کنید |
| AI قالب را فراموش می‌کند | `prompts/10-recovery.md` را ارسال کنید |
| `diff` همیشه full است | قابلیت نوشتن `.ai/state.json` را بررسی کنید |
| Bundle خیلی بزرگ است | از `--no-symbols --no-imports` استفاده کنید |
| نیاز به بازگشت دارید | `python tools/snapshot.py --restore <name>` |
