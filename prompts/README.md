file:prompts/README.md
# پرامپت‌های codemerge

این پوشه شامل پرامپت‌های آماده برای استفاده از دستیار هوش مصنوعی با ابزار `codemerge.py` است.

## ترتیب استفاده

### در نشست اول

1. `01-system.md` — یک بار در ابتدای نشست
2. `01-system-append-2.md` — قواعد ویرایش و خروجی (همیشه همراه قبلی)
3. `02-manifest.md` — بعد از آن، همراه با محتوای manifest
4. `Anti-AI-Slop/00-master-anti-slop.md` — لایهٔ ضد-Slop عمومی
5. `Expertise and Experience/00-anti-slop-core.md` — لایهٔ ضد-Slop پروژه
6. یکی از فایل‌های تخصص (`Expertise and Experience/XX-*.md`) — حداکثر یکی
7. یکی از فایل‌های تسک (`03-bug-fix.md` تا `08-explain-code.md`) — بسته به تسک

### در نشست‌های بعدی

1. `01-system.md` + `01-system-append-2.md` — دوباره اگر دستیار جدیدی استفاده می‌کنید
2. `09-continue-session.md` — برای ادامه

### پرامپت‌های کمکی (در صورت نیاز)

- `10-recovery.md` — وقتی AI از مسیر خارج شده
- `11-limit-files.md` — وقتی AI فایل زیادی درخواست می‌کند
- `12-long-response.md` — وقتی پاسخ AI طولانی است
- `13-final-summary.md` — برای گرفتن خلاصهٔ پایانی
- `14-checklist.md` — چک‌لیست داخلی AI

## نمونهٔ جریان کامل

```bash
# 1. ساخت manifest
python codemerge.py manifest --format md -o .ai/manifest.md

# 2. کپی محتوای 01-system.md و 01-system-append-2.md و ارسال به AI
# 3. کپی محتوای 02-manifest.md + محتوای manifest و ارسال به AI

# 4. انتخاب تسک و ارسال (مثلاً 03-bug-fix.md)

# 5. AI درخواست فایل‌ها را می‌دهد با فرمت codemerge-fetch
# 6. اجرای درخواست AI
python codemerge.py fetch lib/api/auth.ts lib/api/client.ts -o bundle.txt

# 7. ارسال bundle.txt به AI

# 8. اعمال تغییرات پیشنهادی AI

# 9. ذخیرهٔ state برای diff
python codemerge.py diff -o changes.txt

# 10. در نشست بعدی
#     کپی محتوای 09-continue-session.md + محتوای changes.txt و ارسال به AI
```

## نکات مهم

- **پرامپت ۰۱ و ۰۱-append را همیشه اول بفرستید** — بدون آن‌ها AI نمی‌داند با چه ابزاری کار می‌کند و چه فرمتی باید بدهد.
- **پرامپت ۰۲ را بلافاصله بعد از آن‌ها بفرستید** — همراه با محتوای manifest.
- **در هر تسک، یک پرامپت تسک بفرستید** — نه چند تسک در یک پیام.
- **در پایان نشست، پرامپت ۱۳ را بفرستید** — تا خلاصهٔ آماده برای نشست بعد داشته باشید.
- **در نشست بعدی، از پرامپت ۰۹ استفاده کنید** — همراه با خلاصهٔ نشست قبل و خروجی diff.