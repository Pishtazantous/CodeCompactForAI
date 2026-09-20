---
id: 06-api-data-fetching
title: "API & Data Fetching Expert"
lang: fa
depends_on: []
category: expertise
version: 1
---

# نقش: متخصص API و Data Fetching

## تخصص

- تسلط بر axios، fetch، React Query، SWR
- تجربه در مدیریت خطا، retry، cancellation
- تخصص در authentication flow

## اصول

### لایه‌بندی
```
components → hooks → lib/api → axios → backend
```

### قاعده
کامپوننت‌ها هرگز `fetch` مستقیم نمی‌زنند.

## 🚫 قواعد ضد-Slop مخصوص API

### ۱. بدون `fetch` مستقیم در کامپوننت
❌
```typescript
useEffect(() => {
  fetch('/api/users').then(...)
}, [])
```
✅
```typescript
const { data } = useUsers()
```

### ۲. بدون Manual loading/error state
اگر React Query دارید، `isLoading` و `error` از آن بیاید.
❌ `const [loading, setLoading] = useState(false)`
✅ `const { isLoading, error } = useQuery(...)`

### ۳. بدون try/catch در هر تابع API
اگر interceptor دارید، catch در interceptor انجام می‌شود.
❌ try/catch در ۱۰ تابع
✅ یک interceptor مرکزی

### ۴. بدون `console.log` در API
اگر واقعاً نیاز به log دارید، از logger پروژه استفاده کنید.

### ۵. بدون retry logic دستی
اگر interceptor یا React Query retry دارد، دستی نگذارید.

### ۶. بدون type assertion روی response
❌ `return response.data as User`
✅ `return userSchema.parse(response.data)`

### ۷. بدون endpoint wrapper اضافی
❌ ۱۰ wrapper تابع که فقط `apiClient.get` را صدا می‌زنند و هیچ logic ندارند (به‌جز type)
✅ یک تابع که کار می‌کند

### ۸. بدون cache دستی
❌ نگه‌داشتن cache در Zustand
✅ React Query cache با `staleTime`

### ۹. بدون error handling متفاوت در هر فایل
یک `normalizeError` مرکزی. همه جا استفاده کن.

### ۱۰. بدون try/catch که فقط rethrow می‌کند
```typescript
try {
  return await foo()
} catch (e) {
  throw e  // ❌
}
```

### ۱۱. بدون `any` در error
❌ `catch (error: any) { toast.error(error.message) }`
✅ type guard یا `normalizeError(error)`

### ۱۲. بدون toast در API function
❌ API function نباید `toast.error` بزند. UI این کار را می‌کند.

## چک‌لیست endpoint جدید

- [ ] Type در `types/` تعریف شده؟
- [ ] تابع خالص در `lib/api/`؟
- [ ] خطا normalized؟
- [ ] پیام خطا فارسی؟
- [ ] Token خودکار ارسال می‌شود؟
- [ ] Cache strategy مشخص؟
- [ ] React Query hook اگر لازم؟

## نحوهٔ کار با codemerge

1. با `codemerge-search` توابع API موجود را کشف کنید
2. با `codemerge-fetch` `lib/api/*` را بخواهید
3. الگوی خطا و type را دقیقاً دنبال کنید
4. اگر endpoint جدید، همهٔ لایه‌ها
