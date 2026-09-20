# راهنمای کامل `codemerge.py`

## نسخهٔ نهایی با پشتیبانی کامل از TypeScript، Object Literal، Generic Types و `.codemergeignore`

---

## فهرست

1. [معرفی](#معرفی)
2. [نصب و پیش‌نیازها](#نصب-و-پیشنیازها)
3. [گردش کار با هوش مصنوعی](#گردش-کار-با-هوش-مصنوعی)
4. [دستورات](#دستورات)
5. [گزینه‌های مشترک](#گزینههای-مشترک)
6. [پشتیبانی زبان‌ها](#پشتیبانی-زبانها)
7. [فایل `.codemergeignore`](#فایل-codemergeignore)
8. [فایل‌های حساس](#فایلهای-حساس)
9. [نمونه‌های کامل](#نمونههای-کامل)
10. [عیب‌یابی](#عیبیابی)
11. [پرامپت‌های آماده برای AI](#پرامپتهای-آماده-برای-ai)

---

## معرفی

`codemerge.py` ابزاری خط فرمان است که پروژه‌های نرم‌افزاری را برای ارسال به مدل‌های هوش مصنوعی (DeepSeek، ChatGPT، Claude و ...) آماده می‌کند. به جای فرستادن کل پروژه، ابتدا یک **نقشهٔ فشرده** از ساختار پروژه می‌فرستید، سپس هوش مصنوعی خودش تصمیم می‌گیرد کدام فایل‌ها را بخواهد.

### مزایا
- **کاهش ۱۰ تا ۵۰ برابری** حجم ارسال نسبت به فرستادن کل پروژه
- **استخراج دقیق نمادها** برای TypeScript/JavaScript (شامل generic، arrow، object literal)
- **پشتیبانی از ۴۰+ زبان برنامه‌نویسی**
- **بدون وابستگی خارجی** (فقط Python 3.8+)
- **چهار دستور مجزا**: manifest، fetch، diff، search
- **پشتیبانی از `.codemergeignore`** برای کنترل دقیق فایل‌ها

---

## نصب و پیش‌نیازها

### پیش‌نیازها
- Python 3.8 یا بالاتر
- (اختیاری) Git
- (اختیاری) `pip install tiktoken` برای شمارش دقیق توکن

### نصب
فقط فایل `codemerge.py` را در ریشهٔ پروژه قرار دهید. نیازی به نصب پکیج نیست.

```bash
# بررسی نصب
python codemerge.py --help
```

---

## گردش کار با هوش مصنوعی

```
┌──────────────────────────────────────────────────────────────┐
│  گام ۱: ساخت Manifest                                        │
│    python codemerge.py manifest -o manifest.txt              │
│                                                              │
│  گام ۲: ارسال manifest.txt به هوش مصنوعی                    │
│                                                              │
│  گام ۳: AI پاسخ می‌دهد: «auth/login.py و lib/api.ts را بفرست» │
│                                                              │
│  گام ۴: ساخت Bundle با فایل‌های درخواستی                     │
│    python codemerge.py fetch auth/login.py lib/api.ts \      │
│        -o bundle.txt                                         │
│                                                              │
│  گام ۵: ارسال bundle.txt به هوش مصنوعی                      │
│                                                              │
│  گام ۶: در نشست بعدی، فقط تغییرات                            │
│    python codemerge.py diff -o bundle.txt                    │
└──────────────────────────────────────────────────────────────┘
```

---

## دستورات

### ۱. `manifest` — ساخت نقشهٔ پروژه

```bash
python codemerge.py manifest [OPTIONS]
```

خروجی شامل مسیر، زبان، تعداد خطوط، اندازه، sha، imports و لیست توابع/کلاس‌ها است.

**گزینه‌های اختصاصی:**

| گزینه | توضیح |
|---|---|
| `--format {text,md,json}` | فرمت خروجی (پیش‌فرض: `text`). |
| `--no-symbols` | فقط لیست فایل‌ها بدون توابع/کلاس‌ها. |
| `--no-imports` | بدون نمایش importها. |
| `--max-tokens N` | سقف نرم توکن. اگر از سقف رد شود، symbols حذف می‌شوند. |

**نمونه‌ها:**

```bash
# manifest کامل در فرمت متن
python codemerge.py manifest -o manifest.txt

# فقط TypeScript/JavaScript
python codemerge.py manifest -l typescript,javascript -o manifest_ts.txt

# فرمت Markdown (مناسب برای ارسال به AI)
python codemerge.py manifest --format md -o manifest.md

# فرمت JSON (مناسب برای ابزارهای خودکار)
python codemerge.py manifest --format json -o manifest.json

# فشرده‌ترین حالت
python codemerge.py manifest --no-symbols --no-imports -o files.txt

# با محدودیت توکن
python codemerge.py manifest --max-tokens 8000 -o manifest.txt
```

**نمونهٔ خروجی `text`:**

```
# Project Manifest
# Generated: 2026-09-19T23:08:22
# Root: /home/user/myproject
# Files: 208
# ------------------------------------------------------------

=== nextjs-banking/lib/api/auth.ts  [typescript 1222L 33.3K sha=7a2a7b2a] ===
  imports: axios, ./client
  function parseJwt<T = any>(token: string): T | null
  function getTokenExpiry(token: string): number | null
  function loginUser(email: string, password: string): Promise<LoginResponse>
  function registerUser(email: string, password: string, fullName: string, username: string, mobile: string): Promise<RegisterResponse>
  interface LoginResponse
  interface LoginRequest
  ...

=== nextjs-banking/lib/admin/auth.ts  [typescript 31L 1007B sha=26a31a5c] ===
  imports: ./api, @/types/admin
  object adminAuthApi
    . login(data: LoginRequest)
    . logout()
    . register(data: RegisterAdminRequest)
    . activate(adminId: string)
    . revokeAdminTokens(adminId: string)

=== nextjs-banking/app/admin/page.tsx  [typescript 431L 18.7K sha=b663eb9f] ===
  imports: react, next/link, @/lib/admin/reports, lucide-react, sonner, recharts
  function fmtNum(value: number)
  function StatCard({ label, value, icon, accent, href, trend, sub }: ...)
  function QuickActionCard({ title, description, href, icon, accent }: ...)
  function AdminDashboardPage()
    . fetchMonthly()
```

---

### ۲. `fetch` — ارسال فایل‌های درخواستی

```bash
python codemerge.py fetch [FILES ...] [OPTIONS]
```

**گزینه‌های اختصاصی:**

| گزینه | توضیح |
|---|---|
| `FILES ...` | مسیر فایل‌ها (نسبت به ریشهٔ پروژه). |
| `--files-from FILE` | خواندن لیست از فایل (هر خط یک مسیر، `#` کامنت). |
| `--from-stdin` | خواندن لیست از ورودی استاندارد. |

**نمونه‌ها:**

```bash
# مستقیم با آرگومان
python codemerge.py fetch auth/login.py lib/api/auth.ts -o bundle.txt

# از فایل لیست
python codemerge.py fetch --files-from requested.txt -o bundle.txt

# از STDIN
echo "auth/login.py
lib/api/auth.ts" | python codemerge.py fetch --from-stdin -o bundle.txt
```

**نمونهٔ `requested.txt`:**

```
# پاسخ AI:
auth/login.py
lib/api/auth.ts
lib/api/client.ts
store/authStore.ts
```

---

### ۳. `diff` — فقط تغییرات از آخرین اجرا

```bash
python codemerge.py diff [OPTIONS]
```

اولین اجرا مثل `fetch` روی کل پروژه عمل می‌کند و یک state می‌سازد. اجراهای بعدی فقط فایل‌های تغییر یافته، اضافه‌شده و حذف‌شده را گزارش می‌دهد.

**گزینه‌های اختصاصی:**

| گزینه | توضیح |
|---|---|
| `--state-file PATH` | مسیر دلخواه برای state. پیش‌فرض: `<output>.state.json`. |
| `--full` | ادغام کامل (state را به‌روز می‌کند). |
| `--reset-state` | حذف state قبل از اجرا. |
| `--dry-run` | فقط نمایش فایل‌های تغییر یافته. |

**نمونه‌ها:**

```bash
# اجرای اول
python codemerge.py diff -o bundle.txt

# اجرای بعدی: فقط تغییرات
python codemerge.py diff -o bundle.txt

# اجبار به full
python codemerge.py diff --full -o bundle.txt

# پیش‌نمایش
python codemerge.py diff --dry-run
```

**رفتار در سناریوها:**

| سناریو | نتیجه |
|---|---|
| اجرای اول (بدون state) | حالت `full` — کل پروژه. |
| بدون تغییر | پیام `No changes since last run.` |
| فایل `a.py` تغییر کرده | فقط `a.py` در خروجی. |
| فایل `b.py` حذف شده | در هدر گزارش می‌شود. |
| فایل `c.py` اضافه شده | در خروجی نوشته می‌شود. |
| `.codemergeignore` تغییر کند | خودکار به `full` سوییچ می‌کند. |

---

### ۴. `search` — جستجوی یک نماد

```bash
python codemerge.py search PATTERN [OPTIONS]
```

**گزینه‌های اختصاصی:**

| گزینه | توضیح |
|---|---|
| `PATTERN` | الگوی regex یا متن ساده. |
| `--max-hits N` | حداکثر نتیجه (پیش‌فرض: 500). |

**نمونه‌ها:**

```bash
python codemerge.py search verify_password
python codemerge.py search "function handle.*Login" -l typescript
python codemerge.py search UserRepository --output hits.txt
```

---

### ۵. `langs` — فهرست زبان‌های پشتیبانی‌شده

```bash
python codemerge.py langs
```

---

## گزینه‌های مشترک

این گزینه‌ها در همهٔ دستورات (به‌جز `langs`) قابل استفاده‌اند:

| گزینه | توضیح |
|---|---|
| `-l`, `--lang LANG [LANG ...]` | انتخاب زبان(ها). با کاما یا فاصله. |
| `-o`, `--output FILE` | نام فایل خروجی. |
| `-r`, `--root DIR` | ریشهٔ پروژه. |
| `--max-size MB` | حداکثر حجم هر فایل (پیش‌فرض: 100). |
| `--no-git` | نادیده گرفتن Git و پیمایش مستقیم. |
| `--include PATTERN [...]` | الگوهای glob برای اجبار به شامل کردن. |
| `--exclude PATTERN [...]` | الگوهای glob برای حذف. |
| `--allow-sensitive` | شامل کردن فایل‌های حساس. |
| `--all-files` | نادیده گرفتن فیلتر زبان. |
| `--no-header` | بدون هدر در خروجی. |
| `-q`, `--quiet` | عدم چاپ خلاصهٔ نهایی. |
| `--ignore-file PATH` | فایل ignore سفارشی. |
| `--no-ignore-file` | نادیده گرفتن همهٔ فایل‌های ignore. |

---

## پشتیبانی زبان‌ها

### کیفیت استخراج

| زبان | کلاس | تابع | متد | imports | کیفیت |
|---|---|---|---|---|---|
| **Python** | ✅ AST | ✅ AST | ✅ AST | ✅ | عالی |
| **TypeScript** | ✅ | ✅ | ✅ | ✅ | عالی |
| **JavaScript** | ✅ | ✅ | ✅ | ✅ | عالی |
| **Vue / Svelte** | ✅ | ✅ | ✅ | ✅ | عالی |
| **Java** | ✅ | ✅ | ✅ | ✅ | خوب |
| **C#** | ✅ | ✅ | ✅ | ✅ | خوب |
| **C++ / C** | ✅ | ✅ | ✅ | ✅ | خوب |
| **Go** | ✅ | ✅ | ✅ | ✅ | عالی |
| **Rust** | ✅ | ✅ | ✅ | ✅ | عالی |
| **Ruby** | ✅ | ✅ | ✅ | ✅ | خوب |
| **PHP** | ✅ | ✅ | ✅ | ✅ | خوب |
| **Kotlin** | ✅ | ✅ | ✅ | ✅ | خوب |
| **Swift** | ✅ | ✅ | ✅ | ✅ | خوب |
| **Dart** | ✅ | ✅ | ✅ | ✅ | خوب |
| **Scala** | ✅ | ✅ | ✅ | ✅ | خوب |

### قابلیت‌های TypeScript/JavaScript

- ✅ توابع arrow با multi-statement body
- ✅ Type parameters (`function foo<T>(...)`)
- ✅ Return types (ساده و object literal)
- ✅ Multi-line signatures
- ✅ Balanced nested parens در params
- ✅ Object literals با متدها
- ✅ Scope tracking (توابع nested زیر parent)
- ✅ Interface/Enum/Type alias
- ✅ فیلتر خودکار hooks (`useState`, `useEffect` و... نویز نمی‌سازند)

---

## فایل `.codemergeignore`

فایل ignore در ریشهٔ پروژه قرار می‌گیرد و نحو gitignore دارد.

### نمونهٔ پیشنهادی برای پروژه‌های Next.js

```gitignore
# ============ .codemergeignore ============

# محتوای بلاگ (خواندنی)
content/posts/
content/authors/
content/categories/

# فایل‌های backup
*.bak
*.tsbuildinfo

# خروجی‌های codemerge
manifest*.txt
project_source*.txt
codemerge.state.json
check.ps1

# فایل‌های تولیدشده
public/sitemap*.xml
public/robots.txt
public/images/

# فایل‌های حجیم و عمومی
public/telegram-web-app.js

# اسکریپت‌های نصب سرور
scripts/install-*.sh

# فایل‌های config جانبی
next-sitemap.config.js
postcss.config.js
```

### نحو پشتیبانی‌شده

| الگو | توضیح |
|---|---|
| `docs/` | پوشه در هر عمق |
| `/config.json` | فقط در ریشه |
| `*.min.js` | الگو glob |
| `**/snapshots/` | پوشه در هر عمق |
| `!docs/README.md` | negation (استثنا) |
| `# comment` | کامنت |

### نمونه‌های پیچیده

```gitignore
# حذف همهٔ تست‌ها
tests/
**/*.spec.ts
**/*.test.ts

# استثنا
!tests/integration/api.spec.ts

# فایل‌های شخصی
*.local
TODO.private.md
```

---

## فایل‌های حساس

این فایل‌ها **هرگز** در خروجی قرار نمی‌گیرند (مگر با `--allow-sensitive`):

- `.env` و نسخه‌هایش (به‌جز `.env.example`, `.env.sample`, `.env.template`, `.env.dist`)
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `credentials.json`, `secrets.json`, `service-account.json`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.ppk`, `*.secret`, `*.crt`
- `.netrc`, `.pypirc`, `.htpasswd`, `.pgpass`

---

## نمونه‌های کامل

### سناریو ۱: شروع پروژهٔ جدید

```bash
# گام ۱: ساخت manifest برای AI
python codemerge.py manifest -l typescript,javascript -o manifest.txt

# گام ۲: AI می‌گوید این فایل‌ها را بفرست:
#   lib/api/auth.ts
#   lib/api/client.ts
#   store/authStore.ts

# گام ۳: ساخت bundle
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts store/authStore.ts -o bundle.txt

# گام ۴: ارسال bundle.txt
```

### سناریو ۲: ادامهٔ کار در نشست بعدی

```bash
# فقط تغییرات از آخرین اجرا
python codemerge.py diff -o changes.txt

# ارسال changes.txt که شامل فقط فایل‌های تغییر یافته است
```

### سناریو ۳: بررسی یک باگ خاص

```bash
# جستجوی تابع در کل پروژه
python codemerge.py search "handleLogin"

# نتیجه:
# lib/api/auth.ts:172: export const loginUser = async ...
# app/auth/login/page.tsx:45: const handleLogin = ...

# ارسال فایل‌های مرتبط
python codemerge.py fetch lib/api/auth.ts app/auth/login/page.tsx -o bundle.txt
```

### سناریو ۴: پروژهٔ چندزبانه

```bash
# فقط بک‌اند (Python)
python codemerge.py manifest -l python -o backend.txt

# فقط فرانت‌اند (TypeScript)
python codemerge.py manifest -l typescript -o frontend.txt
```

### سناریو ۵: ساختار پیشنهادی پوشه

```
.ai/
├── manifest.txt           # نقشهٔ پروژه
├── bundle.txt             # فایل‌های ارسالی به AI
├── bundle.state.json      # وضعیت diff
└── sessions/
    ├── 01-auth-refactor.md
    └── 02-payment-fix.md
```

برای این ساختار:

```bash
mkdir -p .ai
python codemerge.py manifest -o .ai/manifest.txt
python codemerge.py diff -o .ai/bundle.txt --state-file .ai/state.json
```

---

## عیب‌یابی

### `No source files found`
- زبان انتخابی اشتباه است. با `python codemerge.py langs` بررسی کنید.
- همهٔ فایل‌ها در `.codemergeignore` هستند.
- با `--all-files` امتحان کنید.

### `Unknown language: xxx`
نام زبان را با `python codemerge.py langs` چک کنید.

### فایل در manifest هست ولی در `fetch` رد می‌شود
- احتمالاً باینری است.
- یا حجمش از `--max-size` بیشتر است.
- یا مسیر را نسبت به ریشه اشتباه داده‌اید.

### `diff` همیشه full است
- state ذخیره نشده. مسیر نوشتن آن را بررسی کنید.
- یا `--root` بین دو اجرا تغییر کرده.

### خروجی خیلی بزرگ است
```bash
# manifest کوچک‌تر
python codemerge.py manifest --no-symbols --no-imports -o manifest.txt

# با محدودیت توکن
python codemerge.py manifest --max-tokens 8000 -o manifest.txt
```

### شمارش توکن دقیق نیست
```bash
pip install tiktoken
```

### در PowerShell دستور `grep` کار نمی‌کند
از `Select-String` استفاده کنید:
```powershell
Select-String -Path manifest.txt -Pattern "apiGet"
(Select-String -Path manifest.txt -Pattern "^  function ").Count
```

---

## پرامپت‌های آماده برای AI

### پرامپت ۱: شروع نشست

```
شما یک مهندس نرم‌افزار ارشد هستید که با ابزار codemerge.py کار می‌کنید.

این ابزار چهار دستور دارد:
- manifest: ساخت نقشهٔ فشرده پروژه
- fetch: دریافت محتوای لیست مشخصی از فایل‌ها
- diff: دریافت فقط فایل‌های تغییر یافته
- search: جستجوی یک نماد در پروژه

قواعد:
1. در ابتدا فقط manifest را دارید.
2. برای دریافت محتوای فایل، از فرمت زیر استفاده کنید:

```codemerge-fetch
path/to/file1.ts
path/to/file2.ts
```

3. برای جستجو:

```codemerge-search
symbol_name
```

4. هرگز نخواهید «کل پروژه» را بفرستد.

من الان manifest را می‌فرستم. تا دریافت آن، تأیید کنید.
```

### پرامپت ۲: ارسال manifest

```
manifest پروژه در ادامه آمده است. لطفاً:

1. یک خلاصهٔ ۵-۱۰ خطی از ساختار پروژه بدهید.
2. منتظر دستور من بمانید.

--- شروع manifest ---
[محتوا]
--- پایان manifest ---
```

### پرامپت ۳: رفع باگ

```
# تسک: رفع باگ

## شرح باگ
[توضیح مشکل]

## پیام خطا
[متن خطا]

## دستورالعمل
1. بر اساس manifest، حدس بزنید باگ کجاست.
2. فقط همان فایل‌ها را با codemerge-fetch درخواست کنید.
3. ریشهٔ باگ را تحلیل کنید.
4. راه‌حل را ارائه دهید.
```

### پرامپت ۴: ادامهٔ نشست

```
# ادامهٔ نشست

## خلاصهٔ نشست قبلی
[خلاصه]

## تغییرات اعمال‌شده
[توضیح]

## خروجی codemerge diff
[محتوای bundle.txt از diff]

## تسک فعلی
[تسک جدید]
```

### پرامپت ۵: بازیابی وقتی AI از مسیر خارج شده

```
لطفاً یک لحظه صبر کنید.

به یاد بیاورید:
1. برای دریافت فایل، از codemerge-fetch استفاده کنید.
2. برای جستجو، از codemerge-search استفاده کنید.
3. برای تغییرات، از codemerge-diff استفاده کنید.
4. هرگز نخواهید «کل پروژه» را بفرستد.

اکنون به تسک اصلی برگردیم:
[تسک]
```

---

## جمع‌بندی

| خواسته | وضعیت |
|---|---|
| Manifest با مسیر و توابع | ✅ |
| Fetch لیست فایل | ✅ |
| Diff از آخرین اجرا | ✅ |
| Search | ✅ |
| انتخاب زبان | ✅ |
| پشتیبانی از TypeScript + ۱۵ زبان | ✅ |
| Generic type parameters | ✅ |
| Object literals | ✅ |
| Scope tracking | ✅ |
| `.codemergeignore` | ✅ |
| فایل‌های حساس | ✅ |
| بدون وابستگی خارجی | ✅ |

با این ابزار، حجم ارسال به AI معمولاً **۱۰ تا ۵۰ برابر** کمتر از فرستادن کل پروژه می‌شود، در حالی که هوش مصنوعی دید کامل نسبت به ساختار پروژه دارد.

---

**نسخه:** ۱.۰ نهایی  
**مجوز:** MIT  
**سازگاری:** Python 3.8+