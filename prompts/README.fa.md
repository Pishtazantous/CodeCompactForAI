# خلاصهٔ فارسی پوشهٔ `prompts/`

## خلاصهٔ برنامه

`CodeCompactForAI` یک ابزار خط فرمان محلی برای آماده‌سازی کدبیس جهت گفت‌وگو با مدل‌های هوش مصنوعی است. هدف آن ارسال کل پروژه نیست؛ بلکه با یک گردش کار «زمینهٔ کمینه» حجم context، هزینه و احتمال برداشت نادرست را کاهش می‌دهد:

- `manifest`: نقشه‌ای فشرده از مسیر، زبان، اندازه، hash، importها و symbolهای فایل‌ها تولید می‌کند.
- `fetch`: محتوای کامل فایل‌هایی را که مدل مشخصاً درخواست کرده است در یک bundle قرار می‌دهد.
- `diff`: با نگهداری state، در اجرای اول محتوای کامل و در اجراهای بعد فقط فایل‌های افزوده، تغییرکرده یا حذف‌شده را می‌سازد.
- `search`: محل نمادها و الگوهای متنی یا regex را پیدا می‌کند.
- `langs`: زبان‌های قابل تشخیص را فهرست می‌کند.

کشف فایل با Git یا پیمایش filesystem انجام می‌شود و فایل‌های تولیدی، باینری، حساس، lockfile، فایل minified یا بیش از حد بزرگ معمولاً کنار گذاشته می‌شوند. `.codemergeignore`، فیلتر زبان، globهای include/exclude و محدودیت اندازه نیز دامنه خروجی را کنترل می‌کنند.

## نقش `prompts/` در برنامه

پوشهٔ `prompts/` یک کتابخانهٔ قواعد و قالب‌های متنی برای هدایت مدل در این گردش کار است؛ خودش بخشی از منطق اجرایی `codemerge.py` نیست. برنامهٔ پایتون فایل‌های prompt را نمی‌خواند، `depends_on` را resolve نمی‌کند و promptها را خودکار concatenate نمی‌کند. کاربر یا عامل AI باید فایل‌های مرتبط را به‌صورت دستی انتخاب و همراه manifest یا bundle ارسال کند.

در وضعیت فعلی، این پوشه شامل ۸۹ فایل Markdown است: ۸۶ فایل تکمیل‌شده و ۲ فایل project template که هنوز بخش‌های `<!-- FILL IN -->` دارند. مجموع ۸۶ فایل تکمیل‌شده شامل ۳ فایل Universal، ۱۳ فایل task، ۶۹ فایل Domain، ۱ فایل UI و فایل حاضر است. همهٔ promptهای اجرایی با `lang: en` علامت‌گذاری شده‌اند؛ `README.fa.md` توضیح فارسی کتابخانه است و prompt اجرایی محسوب نمی‌شود.

هر ۵۴ فایل Domain تکمیل‌شده از محدودهٔ عملیاتی پیروی می‌کنند: frontmatter معتبر، وابستگی به لایهٔ Universal، قواعد شماره‌گذاری‌شده، بخش تخصصی `Domain-Specific Anti-Patterns` با مثال‌های واقعی `BAD:`/`GOOD:` و بخش پایانی `Response to Violation`. این promptها همچنان برای ترکیب دستی طراحی شده‌اند و `codemerge.py` آن‌ها را خودکار نمی‌خواند.

## ساختار و منطق لایه‌ها

| مسیر | تعداد | نقش |
|---|---:|---|
| `_universal/` | ۳ | نقش مدل، پروتکل ابزار و قواعد جهانی ضد-slop |
| `tasks/` | ۱۳ | ورود manifest، کار اصلی، کنترل lifecycle و quality gate |
| `domains/delivery/` | ۱۸ | قوانین متناسب با نوع محصول یا سامانه |
| `domains/framework/` | ۳۲ | معماری عمومی و رفتار frameworkهای مشخص |
| `domains/language/` | ۱۲ | idiom، semantics و خطاهای رایج زبان‌ها |
| `domains/concern/` | ۷ | لایه‌های شرطی کیفیت، امنیت و عملیات |
| `ui/` | ۱ | design system، مؤلفه‌های UI و دسترس‌پذیری پایه |
| `projects/` | ۲ | دانش و قراردادهای خاص هر repository |

منطق اصلی، **لایه‌بندی از کلی به اختصاصی** است:

1. لایهٔ جهانی invariantهایی مانند صداقت، ایمنی و minimal diff را تعیین می‌کند.
2. لایهٔ delivery نوع محصول را مشخص می‌کند؛ مثلاً frontend، backend، mobile، CLI، LLM system یا data pipeline.
3. لایهٔ language معنا و شیوهٔ درست کار با زبان پروژه را اضافه می‌کند.
4. لایهٔ framework ابتدا معماری عمومی و سپس قواعد framework مشخص را اعمال می‌کند.
5. concernها فقط در صورت مرتبط‌بودن، مانند امنیت، performance، accessibility یا testing، افزوده می‌شوند.
6. لایهٔ UI فقط برای پروژه‌های دارای رابط کاربری استفاده می‌شود.
7. لایهٔ project واقعیت خاص همان مخزن را معرفی می‌کند و باید بر patternهای واقعی repository تکیه کند، نه توصیه‌های عمومی.

لایه‌های پایین نباید invariantهای لایهٔ بالا را تکرار یا لغو کنند؛ فقط جزئیات تخصصی بیشتری به آن‌ها اضافه می‌کنند. اگر توصیه عمومی با معماری واقعی پروژه تعارض داشته باشد، pattern موجود repository مقدم است و تعارض باید گزارش شود.

## نقش فایل‌های `_universal/`

- `00-master-anti-slop.md`: هستهٔ جهانی قواعد. مواردی مانند جعل نکردن API/import/path، نداشتن placeholder، ادعای اجرای تست بدون اجرای واقعی، پرهیز از YAGNI و وابستگی جدید، اعلام assumptionها، حفظ امنیت، ارائهٔ فایل کامل و self-audit را تعیین می‌کند.
- `01-system.md`: نقش AI و قرارداد کار با `codemerge.py` را تعریف می‌کند؛ نحوهٔ خواندن manifest، درخواست `fetch`/`search`/`diff`، محدودیت تعداد فایل و قالب پاسخ.
- `01-system-append-2.md`: قواعد ویرایش و rollback، ضرورت fetch کردن فایل پیش از ویرایش، کنترل اندازهٔ تغییر و قالب کامل `file:path` را به prompt نقش اضافه می‌کند.

پیشوندهای عددی بیشتر نقش یا ترتیب محلی دارند و یک شماره‌گذاری سراسری برای اجرای همهٔ فایل‌ها نیستند.

## نقش فایل‌های `tasks/`

- `02-manifest.md`: manifest را همراه یک خلاصهٔ کوتاه پروژه به مدل می‌دهد و در ابتدا درخواست فایل نمی‌کند.
- `03-bug-fix.md`: چارچوب تحلیل ریشهٔ باگ، محدودکردن fetch، اعلام rollback و جلوگیری از اصلاح مسائل نامرتبط.
- `04-feature.md`: تعریف دامنه، جست‌وجوی نمادهای مرتبط، تقسیم کار به فایل‌های ضروری و کنترل additions خارج از scope.
- `05-refactor.md`: حفظ رفتار، ترسیم dependency map، تأیید plan و استفاده از characterization test در صورت نبود تست.
- `06-code-review.md`: بررسی بدون ویرایش و گزارش یافته‌ها با مسیر، خط، شدت و راه اصلاح.
- `07-tests.md`: نوشتن تست happy path، خطا و edge case با تبعیت از سبک تست موجود؛ refactor منبع فقط پیشنهاد می‌شود.
- `08-explain-code.md`: تحلیل جریان ورودی تا خروجی، نقش فایل‌ها، تعامل بیرونی و نقاط ضعف بدون تغییر کد.
- `09-continue-session.md`: افزودن خلاصهٔ نشست قبلی و diff جدید؛ مدل باید وضعیت واقعی فایل‌ها را دوباره بررسی کند.
- `10-recovery.md`: بازگرداندن مدل به قراردادهای اصلی پس از انحراف از روال.
- `11-limit-files.md`: تقسیم درخواست‌های حجیم به گروه essential و auxiliary.
- `12-long-response.md` و `13-final-summary.md`: قالب جمع‌بندی پایان نشست، فایل‌های دریافت‌شده/تغییریافته، گام بعدی و درخواست‌های آینده.
- `14-checklist.md`: quality gate پایانی برای بررسی manifest، fetch، محدودیت فایل، کامل‌بودن خروجی، rollback، assumptions و نبود placeholder.

در هر نشست معمولاً فقط یک task اصلی از `03` تا `08` استفاده می‌شود؛ promptهای `09` تا `13` فقط هنگام occurrence استفاده می‌شوند و `14` در انتها قرار می‌گیرد.

## نقش لایه‌های تخصصی

### `domains/delivery/`

هر فایل نوع خروجی یا محیط اجرا را هدف می‌گیرد: frontend، backend، database، mobile، desktop، CLI، browser extension، CI/CD، DevOps، infra، realtime، library، game، ML/LLM system، data pipeline، blockchain و embedded. فایل frontend روی state، data fetching، rendering و frontend delivery تمرکز دارد؛ backend بر validation، auth، API، persistence و failure handling؛ database بر schema، transaction و query safety؛ و فایل‌های دیگر هر کدام قراردادهای متمایز همان حوزه را اضافه می‌کنند.

### `domains/framework/`

لایهٔ `02-architecture-anti-slop.md` مستقل از framework است و دربارهٔ لایه‌بندی، جهت dependency، مرز ماژول، ساختار پوشه، naming، configuration و ترکیب توضیح می‌دهد. فایل‌های دیگر همین اصول را برای React، Next.js، Vue، Nuxt، Svelte، Angular، Express، Fastify، NestJS، Django، FastAPI، .NET، Spring، Rails، Laravel، Phoenix، Go، Rust، Electron، Tauri، Flutter و موارد مشابه تخصصی می‌کنند. `02-state-anti-slop.md` و `02-api-data-anti-slop.md` نیز concerns عمومی state و API/data را جداگانه پوشش می‌دهند.

### `domains/language/`

این لایه تفاوت‌های معنادار زبان‌ها را اضافه می‌کند؛ برای نمونه محدودیت‌های TypeScript، مدل prototype و closure در JavaScript، dynamic typing در Python، ownership و borrowing در Rust، error handling در Go، type system در Java/Kotlin و قواعد زبان‌های Ruby، PHP، C#، C++، Swift و Elixir. لایهٔ عمومی نباید idiom خاص زبان را بازنویسی کند.

### `domains/concern/`

این فایل‌ها overlayهای شرطی هستند: تست، امنیت، refactoring، performance، observability، i18n و accessibility. برای نمونه، قوانین امنیتی در پروژه‌های مالی، auth، PII یا multi-tenant و قوانین performance در مسیرهایی که SLO یا metric مشخص دارند اهمیت بیشتری دارند. نباید همهٔ concernها فقط برای افزایش حجم prompt ارسال شوند.

### `ui/`

`04-ui-design-system.md` فقط برای پروژه‌های دارای UI استفاده می‌شود. منطق آن ابتدا استفاده از design token و primitive موجود، سپس تعریف variantهای محدود و typed، جداسازی منطق تجاری از component primitive، رعایت keyboard/focus/label، پرهیز از کلیشه‌های بصری، انیمیشن کنترل‌شده و چیدمان RTL است. این فایل دربارهٔ UI صحبت می‌کند، نه data fetching یا state.

### `projects/`

هر پوشهٔ project قرار است دانش محلی همان repository را ثبت کند: ابزارها و نسخه‌ها، routing، state، data fetching، فرم، styling، test، naming، import، folder layout، response shape، anti-patternهای قدیمی، محدودیت‌های compliance و ترتیب دقیق خواندن فایل‌ها. دو فایل فعلی برای `banking-frontend` و `banking-backend` هستند و هنوز template محسوب می‌شوند؛ استفاده از آن‌ها فقط پس از تکمیل بخش‌های `FILL IN` معتبر است.

## ترتیب پیشنهادی ترکیب

ترکیب promptها یک پروتکل انسانی/مدل‌محور است، نه عملیات خودکار برنامه:

1. `01-system.md` و `01-system-append-2.md`
2. `02-manifest.md` همراه خروجی واقعی `codemerge.py manifest`
3. `00-master-anti-slop.md`
4. یک delivery layer متناسب
5. یک language layer و در صورت نیاز JavaScript/TypeScript precedence
6. `02-architecture-anti-slop.md` و سپس frameworkهای واقعاً استفاده‌شده
7. concernهای قابل‌اعمال
8. لایهٔ UI در صورت وجود رابط کاربری
9. project layer تکمیل‌شدهٔ همان repository
10. فقط یک task اصلی
11. promptهای lifecycle در صورت نیاز
12. checklist پیش از ارسال پاسخ

پس از manifest، مدل باید ابتدا مسیرها را از خود manifest انتخاب کند، برای نماد نامطمئن `search` کند و پیش از ویرایش محتوای واقعی فایل را با `fetch` بگیرد. خود manifest جایگزین محتوای فایل نیست.

## نکات وضعیت فعلی

- فایل‌های `domains/delivery/` و `domains/framework/` تکمیل شده‌اند؛ تنها دو فایل `projects/` هنوز template هستند و نباید به‌عنوان دانش نهایی repository استفاده شوند.
- مسیرهای prompt در بخشی از `README.md` و `docs/CHEATSHEET.md` قدیمی‌اند؛ ساختار فعلی همان پوشه‌های `prompts/_universal`، `prompts/tasks`، `prompts/domains`، `prompts/ui` و `prompts/projects` است.
- `tasks/12-long-response.md` عملاً تکرار `13-final-summary.md` است و `id` اشتباه `13-final-summary` دارد.
- فایل‌های قدیمی `domains/framework/02-react-anti-slop.md` و `domains/concern/02-accessibility-critical-anti-slop.md` همچنان خارج از مجموعهٔ ۵۴ فایل بازتولیدشده‌اند و opener صحیح `---` ندارند؛ آن‌ها فقط پس از بازبینی کامل و جداگانه استاندارد کن.
- هر دو project فایل `id: 00-anti-slop-core` دارند؛ این id فقط در محدودهٔ project معنا دارد و نباید سراسری فرض شود.
- metadataهای `depends_on` راهنمای declarative هستند و تا زمانی که resolver خودکاری وجود نداشته باشد، ترتیب واقعی ترکیب بر عهدهٔ کاربر است.

در نتیجه، `prompts/` یک stack رفتاری قابل‌ترکیب برای کاهش hallucination، scope creep و کد بی‌کیفیت است؛ در کنار `codemerge.py` قرار می‌گیرد، اما خودش ابزار اجرایی جداگانه‌ای نیست.
