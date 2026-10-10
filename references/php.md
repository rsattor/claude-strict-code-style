# PHP, Laravel, Symfony

Bu fayl SKILL.md'dagi qoidalarning PHP, Laravel va Symfony uchun aniq qo'llanmasi.

## Mundarija

1. Standartlar va loyiha tuzilishi
2. Izohlar va doc-comment
3. Satr qurish
4. Massivlarni birlashtirish
5. Shartlar, null va standart qiymatlar
6. Tiplash
7. Testlar
8. To'liq misol

## 1. Standartlar va loyiha tuzilishi

| Muhit | Standartlar |
| --- | --- |
| PHP | PSR-1, PER Coding Style (PSR-12 davomi), PSR-4 autoload, PHPDoc |
| Laravel | Laravel hujjatlaridagi nomlash qoidalari, standart skeleton, Laravel Pint |
| Symfony | Symfony Coding Standards, Symfony Best Practices, standart skeleton, PHP-CS-Fixer `@Symfony` to'plami |

Tuzilish:

- **Laravel:** `app/`, `bootstrap/`, `config/`, `database/`, `routes/`, `resources/`, `tests/Feature`, `tests/Unit`. Biznes mantiq kattalashsa, `app/` ichida domen bo'yicha ajrat, masalan `app/Billing/`, `app/Orders/`. Controller'larni yupqa tut, mantiqni Action, Service yoki domen class'lariga chiqar. Kirish ma'lumotlari uchun Form Request ishlat.
- **Symfony:** `src/`, `config/`, `templates/`, `migrations/`, `tests/`. `src/` ichida domen yoki bounded context bo'yicha ajrat.
- **Kutubxona:** `src/`, `tests/`, `composer.json` (PSR-4), `phpunit.xml.dist`, `phpstan.neon.dist`.
- **Fayl va class nomlari:** class fayllari `PascalCase.php`, bitta faylda bitta class, namespace papka yo'liga mos.

Laravel Pint yoki PHP-CS-Fixer sozlamasida `logical_operators` qoidasi yoqilgan bo'lsa, u `or` ni avtomatik `||` ga aylantiradi. Bunday holda konfiguratsiyani o'zing o'zgartirma, bu qoidani o'chirishni foydalanuvchiga taklif qil.

## 2. Izohlar va doc-comment

`//`, `#` va `/* */` izohlar yozilmaydi. `#[...]` attribute'lari izoh emas va ular ishlatilaveradi.

Har bir class, interface, trait, enum, metod, property va konstantaga PHPDoc yoziladi:

```php
/**
 * Applies the coupon to the order and returns the discounted total.
 *
 * The discount is not applied when the coupon has expired or when the
 * order total is below the coupon's minimum amount.
 *
 * @param Order  $order  The order the discount is applied to.
 * @param Coupon $coupon The coupon entered by the customer.
 *
 * @return Money The final total after the discount.
 *
 * @throws ExpiredCouponException When the coupon has expired.
 * @throws MinimumAmountNotReachedException When the order total is below the coupon minimum.
 */
public function apply(Order $order, Coupon $coupon): Money
```

Constructor'da e'lon qilingan property'lar uchun constructor'ning PHPDoc'ida har bir parametrni `@param` bilan tavsifla.

## 3. Satr qurish

Taqiqlangan: `.` va `.=` bilan ulash, `"Hello $name"` va `"{$user->name}"` interpolatsiyasi, heredoc ichidagi o'zgaruvchilar, `implode()`, `join()`, `collect()->implode()`.

| Vazifa | Laravel | Symfony | Toza PHP |
| --- | --- | --- | --- |
| Shablon bo'yicha satr | `sprintf()` | `sprintf()` | `sprintf()`, `vsprintf()` |
| Oxiriga yoki boshiga qo'shish | `Str::of($slug)->append('.pdf')->toString()`, `->prepend()`, `Str::finish($path, '/')`, `Str::start($path, '/')`, `Str::wrap($value, '"')` | `u($slug)->append('.pdf')->toString()`, `->prepend()`, `->ensureEnd('/')`, `->ensureStart('/')` | `sprintf('%s.pdf', $slug)` |
| Ro'yxatni satrga aylantirish | `Arr::join($names, ', ')`, `Arr::join($names, ', ', ' and ')` | `u(', ')->join($names)->toString()` | Symfony String component'ni o'rnat |
| Foydalanuvchiga ko'rinadigan matn | `__('orders.shipped', ['number' => $order->number])` | `$translator->trans('orders.shipped', ['%number%' => $order->number])` | `sprintf()` |
| Log | `Log::info('Order shipped.', ['order_id' => $order->id])` | `$logger->info('Order {id} shipped.', ['id' => $order->id])` | PSR-3 kontekst massivi |
| URL va yo'l | `route('orders.show', $order)`, `url()`, `storage_path('reports')` | `$urlGenerator->generate()`, `Path::join()` (Filesystem component) | `sprintf()` |
| SQL | Query Builder, Eloquent | Doctrine Query Builder, DQL parametrlari | PDO prepared statement |

Symfony String funksiyasi `use function Symfony\Component\String\u;` bilan import qilinadi. `Str::of()` va `u()` string obyekt qaytaradi, `string` tipi kerak bo'lganda `->toString()` chaqir.

## 4. Massivlarni birlashtirish

`$a + $b` va `$a += $b` taqiqlangan, chunki takroriy kalitlar jimgina tashlab yuboriladi.

| Vazifa | Ishlat |
| --- | --- |
| Ro'yxatlarni ulash | `array_merge($first, $second)`, `[...$first, ...$second]`, Laravel'da `collect($first)->concat($second)` |
| Sozlamalarni ustiga yozish | `array_replace($defaults, $options)`, Laravel'da `collect($defaults)->merge($options)` |
| Ichma-ich ro'yxatlarni tekislash | `Arr::collapse($groups)`, `collect($groups)->flatten(1)` |

## 5. Shartlar, null va standart qiymatlar

Taqiqlangan: `? :`, `?:`, `??`, `??=`, `?->`, `||`.

`||` o'rniga `or` ishlat. PHP'da `or` ning ustuvorligi `=` dan past, shuning uchun uni `if`, `while` va `return` ichida ishlat, o'zgaruvchiga yozganda esa qavsga ol. `&&` bilan birga kelsa, guruhlarni qavs bilan ajrat:

```php
if ($user->isAdmin() or $user->owns($post)) {
    return true;
}

$canEdit = ($user->isAdmin() or $user->owns($post));

if (($order->isPaid() && $order->isShippable()) or $user->isAdmin()) {
    $this->ship($order);
}
```

Qiymat tanlash uchun ternary o'rniga `match` ishlat:

```php
$label = match ($user->role) {
    Role::Admin => 'Administrator',
    Role::Editor => 'Editor',
    Role::Viewer => 'Viewer',
};
```

Standart qiymat bilan olish:

| Muhit | Ishlat |
| --- | --- |
| Laravel | `Arr::get($data, 'user.city', 'unknown')`, `data_get($user, 'profile.city', 'unknown')`, `$request->input('sort', 'id')`, `$request->integer('limit', 10)`, `$request->boolean('active')`, `$request->enum('status', Status::class)`, `config('app.name', 'App')`, `$collection->get('key', 'default')` |
| Symfony | `$request->query->get('sort', 'id')`, `$request->query->getInt('limit', 10)`, `$request->query->getBoolean('active')`, `$request->query->getEnum('status', Status::class)`, `$request->attributes->get('key', 'default')` |
| Toza PHP | `array_key_exists()` yoki `isset()` bilan ochiq tekshirib, `if` orqali standart qiymat berish |

Nullsafe o'rniga null'ni ochiq tekshir:

```php
$profile = $user->profile;

if ($profile === null) {
    return 'unknown';
}

return $profile->city;
```

Undan ham yaxshisi, null'ning o'zidan qoch: majburiy relation, constructor'da talab qilinadigan qiymat, `withDefault()` bilan relation, null o'rniga bo'sh collection.

## 6. Tiplash

- **Qat'iy rejim:** har bir faylning boshida `declare(strict_types=1);` bo'lsin.
- **Statik tahlil:** PHPStan `level: max` darajada ishlasin, Laravel'da Larastan bilan.
- **Native tiplar:** har bir parametr, return va property'ga native tip yoz. Constructor promotion va `readonly` property'lar ishlat.
- **Ota class'dan meros property:** framework'ning tipsiz property'sini qayta e'lon qilganda native tip qo'yib bo'lmaydi, PHP buni fatal xato deb hisoblaydi. Bunga Eloquent'dagi `$fillable`, `$casts`, `$hidden` va `$table` misol bo'ladi. Bunday property'ning tipini PHPDoc'da `@var list<string>` kabi aniq ko'rsat. Tekshiruv skripti ham shu holatni qabul qiladi.
- **Taqiqlangan:** `mixed`, tipsiz parametr va property, ichi ko'rsatilmagan `array`, `object`, `@phpstan-ignore`, `@var` bilan tipni majburlash.
- **Massiv shakllari:** massivlar PHPDoc'da aniq ko'rsatilsin: `list<User>`, `array<string, int>`, `non-empty-list<Order>`, `array{id: int, name: string}`.
- **Generic'lar:** collection'lar uchun `Collection<int, User>`, generic class'lar uchun `@template`.
- **Domen tiplari:** sehrli satrlar o'rniga backed `enum` ishlat. Massivlar o'rniga `final readonly class` DTO va value object ishlat.
- **Tashqi ma'lumot:** Laravel'da Form Request va undan DTO'ga o'tkazish, Symfony'da `#[MapRequestPayload]`, `#[MapQueryString]` va Validator ishlat.

## 7. Testlar

| Muhit | Vositalar |
| --- | --- |
| Laravel | PHPUnit yoki Pest (loyihada qaysi biri bo'lsa), model factory'lar, `RefreshDatabase`, `Http::fake()`, `Mail::fake()`, `Queue::fake()`, `Event::fake()`, `$this->travelTo()` |
| Symfony | PHPUnit, `KernelTestCase`, `WebTestCase`, `MockHttpClient`, `MockClock`, Foundry factory'lari |
| Kutubxona | PHPUnit 10+ |

- **Attribute'lar:** PHPUnit 10+ attribute'larini ishlat: `#[Test]`, `#[DataProvider('expiredCoupons')]`, `#[CoversClass(CouponService::class)]`.
- **Assertion:** `assertSame` ishlat, `assertEquals` emas. Istisnoni `expectException(ExpiredCouponException::class)` bilan tekshir.
- **Joylashuv:** `tests/Unit` va `tests/Feature` ichidagi joylashuv `app/` yoki `src/` tuzilishini takrorlasin.
- **Nomlar:** test metodi nomi xatti-harakatni aytsin: `expired_coupon_is_rejected` yoki `testExpiredCouponIsRejected`. Loyihada qaysi uslub bo'lsa, o'shani ishlat.

## 8. To'liq misol

```php
<?php

declare(strict_types=1);

namespace App\Billing;

use App\Billing\Exceptions\ExpiredCouponException;
use App\Models\Coupon;
use App\Models\Order;
use Illuminate\Support\Arr;

/**
 * Applies discount coupons to orders and describes the applied discounts.
 */
final readonly class CouponService
{
    /**
     * Creates the service with the clock used to validate coupon expiry.
     *
     * @param Clock $clock Source of the current time.
     */
    public function __construct(private Clock $clock)
    {
    }

    /**
     * Returns the order total after applying the coupon discount.
     *
     * @param Order  $order  The order the discount is applied to.
     * @param Coupon $coupon The coupon entered by the customer.
     *
     * @return int The discounted total in minor currency units.
     *
     * @throws ExpiredCouponException When the coupon has expired.
     */
    public function apply(Order $order, Coupon $coupon): int
    {
        if ($coupon->expiresAt() < $this->clock->now()) {
            throw ExpiredCouponException::forCoupon($coupon);
        }

        return match ($coupon->type) {
            CouponType::Percent => intdiv($order->total * (100 - $coupon->value), 100),
            CouponType::Fixed => max(0, $order->total - $coupon->value),
        };
    }

    /**
     * Builds a human readable summary of the coupon codes used on an order.
     *
     * @param list<string> $codes Coupon codes in the order they were applied.
     *
     * @return string Summary such as "Coupons: SPRING, VIP".
     */
    public function summary(array $codes): string
    {
        return sprintf('Coupons: %s', Arr::join($codes, ', '));
    }
}
```

```php
<?php

declare(strict_types=1);

namespace Tests\Unit\Billing;

use App\Billing\CouponService;
use App\Billing\Exceptions\ExpiredCouponException;
use App\Models\Coupon;
use App\Models\Order;
use PHPUnit\Framework\Attributes\CoversClass;
use PHPUnit\Framework\Attributes\Test;
use Tests\TestCase;

/**
 * Covers the coupon rules enforced by CouponService.
 */
#[CoversClass(CouponService::class)]
final class CouponServiceTest extends TestCase
{
    /**
     * Ensures a percent coupon reduces the order total by its percentage.
     */
    #[Test]
    public function percent_coupon_reduces_order_total(): void
    {
        $order = Order::factory()->make(['total' => 10_000]);
        $coupon = Coupon::factory()->percent(10)->make();

        $total = $this->service()->apply($order, $coupon);

        $this->assertSame(9_000, $total);
    }

    /**
     * Ensures an expired coupon is rejected with a dedicated exception.
     */
    #[Test]
    public function expired_coupon_is_rejected(): void
    {
        $order = Order::factory()->make();
        $coupon = Coupon::factory()->expired()->make();

        $this->expectException(ExpiredCouponException::class);

        $this->service()->apply($order, $coupon);
    }

    /**
     * Resolves the service under test from the container.
     */
    private function service(): CouponService
    {
        return $this->app->make(CouponService::class);
    }
}
```
