# tools/

اسکریپت‌های کمکی کوچک برای گردش کار با هوش مصنوعی.

## apply_ai_output.py

پارس و اعمال بلوک‌های فایل تولیدشده توسط AI. هر بلوک باید از این فرمت استفاده کند:

    ```file:path/to/file.ts
    <محتوای کامل فایل>
    ```

### روش استفاده

    python tools/apply_ai_output.py ai_response.md --dry-run
    python tools/apply_ai_output.py ai_response.md
    python tools/apply_ai_output.py ai_response.md --force
    cat ai_response.md | python tools/apply_ai_output.py --from-stdin

فایل‌های موجود قبل از بازنویسی در `.ai/backups/<timestamp>/` پشتیبان‌گیری می‌شوند. فایل‌های جدید فقط با `--force` ایجاد می‌شوند.

---

## snapshot.py

عکس‌های کامل از فایل‌های منبع پروژه. مفید قبل از ویرایش‌های بزرگ AI.

### روش استفاده

    python tools/snapshot.py --label before-ai-edit
    python tools/snapshot.py --list
    python tools/snapshot.py --restore before-ai-edit
    python tools/snapshot.py --clean

اسنپ‌شات‌ها در `.ai/snapshots/<timestamp>[-label]/` ذخیره می‌شوند. فقط ۱۰ اسنپ‌شات آخر بعد از `--clean` حفظ می‌شوند.

---

## verify.ps1 / verify.sh

اجرای بررسی‌های پروژه بعد از ویرایش‌های AI: type-check، lint، تست، build.

### روش استفاده (ویندوز)

    .\tools\verify.ps1
    .\tools\verify.ps1 -SkipTests
    .\tools\verify.ps1 -Only "type-check","lint"

### روش استفاده (لینوکس / مک)

    chmod +x tools/verify.sh
    ./tools/verify.sh
    ./tools/verify.sh --skip-tests
    ./tools/verify.sh --only type-check,lint

در صورت شکست، اسکریپت بازگردانی اسنپ‌شات را پیشنهاد می‌دهد.

---

## new_session.py

ساخت یک نشست جدید AI.

### روش استفاده

    python tools/new_session.py "auth refactor"
    python tools/new_session.py "payment bug" --prev 02

فایل‌های `.ai/sessions/<NN>-<slug>.md` را ایجاد می‌کند و `.ai/sessions/index.json` را به‌روز می‌کند.

---

## session_summary.py

چاپ خلاصه‌های نشست‌های اخیر.

### روش استفاده

    python tools/session_summary.py
    python tools/session_summary.py --last 3
    python tools/session_summary.py --list
    python tools/session_summary.py -v

---

## گردش کار کامل از ابتدا تا انتها

```bash
# شروع یک نشست جدید
python tools/snapshot.py --label before-session
python tools/new_session.py "task title" --prev 0N
python codemerge.py manifest -o .ai/manifest.md

# بعد از پاسخ AI، پاسخ را در ai_response.md ذخیره کنید
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md
.\tools\verify.ps1

# اگر verify شکست خورد
python tools/snapshot.py --restore before-session

# پایان نشست: پر کردن Summary در .ai/sessions/<NN>-*.md
python tools/session_summary.py --last 1
```

---

## estimate.py

تخمین توکن و هزینه یک فایل قبل از ارسال به AI.

### روش استفاده

    python tools/estimate.py bundle.txt
    python tools/estimate.py bundle.txt --model deepseek-chat
    python tools/estimate.py bundle.txt --output-tokens 3000

### نکات

اگر `tiktoken` نصب باشد برای شمارش دقیق توکن استفاده می‌کند، در غیر این صورت از معیار ۴-کاراکتر-پرتوکن استفاده می‌کند. قیمت‌ها کدنویزی شده‌اند و ممکن است با تغییر ارائه‌دهندگان نیاز به به‌روزرسانی داشته باشند.

---

## watch.py

پیگیری پروژه و اجرای خودکار `codemerge diff` هنگام تغییر فایل‌ها.

### روش استفاده

    python tools/watch.py
    python tools/watch.py --interval 5
    python tools/watch.py -o .ai/changes.txt
    python tools/watch.py -q

### نکات

یک diff اولیه را فوراً اجرا می‌کند، سپس هر `--interval` ثانیه polling می‌کند. برای توقف Ctrl+C را فشار دهید.

---

## log_metrics.py

ثبت متریک‌های گردش کار AI به ازای هر نشست.

### روش استفاده

    python tools/log_metrics.py --task "feature" --files-changed 5 \
        --slop-count 1 --time-saved 45
    python tools/log_metrics.py --show
    python tools/log_metrics.py --show --last 20
    python tools/log_metrics.py --reset

### نکات

متریک‌ها در `.ai/metrics.json` ذخیره می‌شوند. بعد از چند هفته، `--show` نشان می‌دهد کدام تسک‌ها بیشترین اسلپ را تولید می‌کنند و چقدر زمان صرفه‌جویی شده است.

---

## setup_profile.ps1

نصب توابع میانبر PowerShell برای گردش کار AI.

### روش استفاده

    .\tools\setup_profile.ps1
    . $PROFILE        # reload the profile

بعد از این، میانبرهای زیر در دسترس هستند:

| میانبر | اجرا می‌کند |
|---|---|
| `cm-manifest` | `python codemerge.py manifest -o .ai/manifest.md` |
| `cm-fetch` | `python codemerge.py fetch @args -o .ai/bundle.txt` |
| `cm-diff` | `python codemerge.py diff -o .ai/changes.txt` |
| `cm-search` | `python codemerge.py search @args` |
| `cm-snapshot` | `python tools/snapshot.py @args` |
| `cm-apply` | `python tools/apply_ai_output.py @args` |
| `cm-verify` | `.\tools\verify.ps1 @args` |
| `cm-newsession` | `python tools/new_session.py @args` |
| `cm-summary` | `python tools/session_summary.py @args` |
| `cm-estimate` | `python tools/estimate.py @args` |
| `cm-metrics` | `python tools/log_metrics.py @args` |
| `cm-watch` | `python tools/watch.py @args` |
