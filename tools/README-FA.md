# ابزارهای گردش‌کار AI

این پوشه شامل اسکریپت‌های کمکی برای مدیریت نشست‌های هوش مصنوعی، اعمال خروجی کد، گرفتن snapshot و اجرای بررسی‌های پروژه است.

## `apply_ai_output.py`

خروجی AI را می‌خواند و بلاک‌های فایل را استخراج و اعمال می‌کند. هر بلاک باید این قالب را داشته باشد:

````markdown
```file:path/to/file.ts
<محتوای کامل فایل>
```
````

### کاربرد

```bash
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md
python tools/apply_ai_output.py ai_response.md --force
cat ai_response.md | python tools/apply_ai_output.py --from-stdin
```

اگر فایل مقصد از قبل وجود داشته باشد، قبل از بازنویسی یک نسخهٔ پشتیبان در مسیر زیر ساخته می‌شود:

```text
.ai/backups/<timestamp>/
```

فایل‌های جدید فقط با گزینهٔ `--force` ساخته می‌شوند. با `--dry-run` هیچ تغییری نوشته نمی‌شود و فقط عملیات پیش‌بینی‌شده نمایش داده می‌شود.

---

## `snapshot.py`

از فایل‌های سورس پروژه snapshot زمانی‌دار می‌گیرد. این ابزار برای گرفتن نسخهٔ امن قبل از تغییرات بزرگ AI مناسب است.

### کاربرد

```bash
python tools/snapshot.py --label before-ai-edit
python tools/snapshot.py --list
python tools/snapshot.py --restore before-ai-edit
python tools/snapshot.py --clean
```

Snapshotها در مسیر زیر ذخیره می‌شوند:

```text
.ai/snapshots/<timestamp>[-label]/
```

پس از اجرای `--clean` فقط ۱۰ snapshot آخر نگهداری می‌شوند.

---

## `verify.ps1` / `verify.sh`

پس از تغییرات AI، بررسی‌های پروژه را اجرا می‌کنند: type-check، lint، تست‌ها و build.

### کاربرد در Windows

```powershell
.\tools\verify.ps1
.\tools\verify.ps1 -SkipTests
.\tools\verify.ps1 -SkipBuild
.\tools\verify.ps1 -Only "type-check","lint"
```

### کاربرد در Linux / macOS

ابتدا فایل را executable کنید:

```bash
chmod +x tools/verify.sh
```

سپس اجرا کنید:

```bash
./tools/verify.sh
./tools/verify.sh --skip-tests
./tools/verify.sh --skip-build
./tools/verify.sh --only type-check,lint
```

در صورت خطا، اسکریپت گزینهٔ بازگشت با snapshot را پیشنهاد می‌دهد.

---

## `new_session.py`

یک نشست جدید AI با قالب استاندارد می‌سازد.

### کاربرد

```bash
python tools/new_session.py "auth refactor"
python tools/new_session.py "payment bug" --prev 02
```

این ابزار فایل زیر را می‌سازد و فهرست نشست‌ها را به‌روزرسانی می‌کند:

```text
.ai/sessions/<NN>-<slug>.md
.ai/sessions/index.json
```

پس از ساخت نشست، بخش‌های `Goal` و `Context` را تکمیل کنید و در پایان، خلاصهٔ نشست را در بخش `Summary for Next Session` بنویسید.

---

## `session_summary.py`

خلاصهٔ نشست‌های اخیر را برای شروع گفتگوی بعدی چاپ می‌کند.

### کاربرد

```bash
python tools/session_summary.py
python tools/session_summary.py --last 3
python tools/session_summary.py --list
python tools/session_summary.py -v
```

گزینهٔ `-v` یا `--verbose` فهرست فایل‌های تغییرکرده را نیز نمایش می‌دهد.

---

## گردش کار کامل

```bash
# شروع نشست جدید
python tools/snapshot.py --label before-session
python tools/new_session.py "task title" --prev 0N
python codemerge.py manifest -o .ai/manifest.md

# پس از دریافت پاسخ AI، پاسخ را در ai_response.md ذخیره کنید
python tools/apply_ai_output.py ai_response.md --dry-run
python tools/apply_ai_output.py ai_response.md

# اجرای بررسی‌ها در Windows
.\tools\verify.ps1

# اجرای بررسی‌ها در Linux / macOS
./tools/verify.sh

# اگر بررسی‌ها ناموفق بودند
python tools/snapshot.py --restore before-session

# پایان نشست: بخش Summary را در فایل نشست تکمیل کنید
python tools/session_summary.py --last 1
```

## نکات مهم

- قبل از اعمال خروجی AI، همیشه ابتدا `--dry-run` را اجرا کنید.
- قبل از تغییرات گسترده، snapshot بگیرید.
- فایل‌های خروجی AI باید از قالب ` ```file:relative/path ``` ` استفاده کنند.
- اگر بررسی‌ها fail شدند، قبل از اصلاح دستی، snapshot را بررسی کنید.
- مسیر فایل‌ها باید نسبت به ریشهٔ پروژه باشند.
