# Expertise and Experience with Anti-Slop

هر پرامپت در این پوشه، دو لایه دارد:

1. **لایهٔ تخصص** — چه اصولی، چه ابزارهایی، چه الگوهایی
2. **لایهٔ ضد-Slop** — چه دام‌هایی در این تخصص وجود دارد

## اصل حاکم

تخصص به AI می‌گوید «چه کاری انجام بده».
ضد-Slop به AI می‌گوید «چه کاری انجام نده».
هر دو با هم، کد بی‌کیفیت را از خروجی حذف می‌کنند.

## نحوهٔ استفاده

```
1. prompts/01-system.md                          (پایه)
2. prompts/02-manifest.md + manifest             (شروع)
3. prompts/Anti-AI-Slop/00-master-anti-slop.md   (لایهٔ ضد-Slop عمومی)
4. prompts/Expertise and Experience-FA/00-anti-slop-core.md  (لایهٔ ضد-Slop مخصوص پروژه)
5. prompts/Expertise and Experience-FA/XX-*.md   (تخصص مورد نیاز)
6. prompts/03-bug-fix.md                         (تسک)
```

## قاعدهٔ فولادی

**هرگز دو تخصص را در یک نشست ترکیب نکنید.** اگر تسک هم به TypeScript نیاز دارد و هم به Security، ابتدا پرامپت TypeScript را بفرستید، تسک را انجام دهید، سپس پرامپت Security را بفرستید.

## به‌روزرسانی

هر بار در code review یک الگوی جدید از Slop دیدید، آن را به بخش
«الگوهای ممنوع مخصوص این تخصص» در فایل مربوطه اضافه کنید.
