---

## estimate.py

تعداد توکن و هزینهٔ یک فایل را قبل از ارسال به AI برآورد می‌کند.

### کاربرد

    python tools/estimate.py bundle.txt
    python tools/estimate.py bundle.txt --model deepseek-chat
    python tools/estimate.py bundle.txt --output-tokens 3000

### نکات

اگر `tiktoken` نصب باشد، برای شمارش دقیق توکن از آن استفاده می‌شود؛ در غیر این صورت از روش تقریبی چهار نویسه به‌ازای هر توکن استفاده می‌شود. قیمت‌ها به‌صورت ثابت در کد تعریف شده‌اند و ممکن است با تغییر قیمت ارائه‌دهندگان نیاز به به‌روزرسانی داشته باشند.

---

## watch.py

پروژه را زیر نظر می‌گیرد و هنگام تغییر فایل‌ها، به‌طور خودکار `codemerge diff` را اجرا می‌کند.

### کاربرد

    python tools/watch.py
    python tools/watch.py --interval 5
    python tools/watch.py -o .ai/changes.txt
    python tools/watch.py -q

### نکات

در ابتدا بلافاصله یک diff اجرا می‌کند و سپس هر `--interval` ثانیه پروژه را بررسی می‌کند. برای توقف، Ctrl+C را بفشارید.

---

## log_metrics.py

متریک‌های گردش‌کار AI را برای هر نشست ثبت می‌کند.

### کاربرد

    python tools/log_metrics.py --task "feature" --files-changed 5 \
        --slop-count 1 --time-saved 45
    python tools/log_metrics.py --show
    python tools/log_metrics.py --show --last 20
    python tools/log_metrics.py --reset

### نکات

متریک‌ها در `.ai/metrics.json` ذخیره می‌شوند. پس از چند هفته، `--show` نشان می‌دهد کدام تسک‌ها بیشترین Slop را ایجاد کرده‌اند و چه مقدار زمان ذخیره شده است.

---

## setup_profile.ps1

تابع‌های میانبر PowerShell را برای گردش‌کار AI نصب می‌کند.

### کاربرد

    .\tools\setup_profile.ps1
    . $PROFILE        # بارگذاری دوبارهٔ profile

پس از این کار، میانبرهای زیر در دسترس هستند:

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
