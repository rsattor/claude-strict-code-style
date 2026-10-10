# TypeScript, JavaScript

Bu fayl SKILL.md'dagi qoidalarning TypeScript va JavaScript uchun aniq qo'llanmasi. Yangi kod TypeScript'da yoziladi. Toza JavaScript faqat loyiha shuni talab qilsa ishlatiladi.

## Mundarija

1. Standartlar va loyiha tuzilishi
2. Izohlar va TSDoc
3. Satr qurish
4. Massiv va obyektlarni birlashtirish
5. Shartlar, null va standart qiymatlar
6. Tiplash
7. Testlar
8. To'liq misol

## 1. Standartlar va loyiha tuzilishi

- **Standartlar:** TypeScript Handbook va framework'ning rasmiy hujjatlari (React, Next.js, Vue, Angular Style Guide, NestJS).
- **Asboblar:** ESLint (`typescript-eslint` ning `strict-type-checked` to'plami) va Prettier.
- **Linter bilan ziddiyat:** `typescript-eslint` dagi `prefer-nullish-coalescing` va `prefer-optional-chain` qoidalari shu skill qoidalariga zid. Ular yoqilgan bo'lsa, o'chirishni foydalanuvchiga taklif qil.
- **Node.js kutubxona yoki CLI tuzilishi:**

```text
project/
├── package.json
├── tsconfig.json
├── eslint.config.js
├── vitest.config.ts
├── src/
│   ├── index.ts
│   ├── github/
│   │   ├── client.ts
│   │   └── schemas.ts
│   └── reports/
│       └── language-report.ts
└── tests/
    ├── github/
    │   └── client.test.ts
    └── reports/
        └── language-report.test.ts
```

- **Framework loyihalari:** framework'ning rasmiy papka tuzilishiga amal qil, masalan Next.js'da `app/` router.
- **Nomlar:** fayl nomlari `kebab-case.ts`. React komponentlari loyihada qaysi uslub bo'lsa, o'shanda: `PascalCase.tsx` yoki `kebab-case.tsx`.

## 2. Izohlar va TSDoc

`//` va `/* */` izohlar yozilmaydi. `// eslint-disable-next-line` faqat haqiqatan kerak bo'lsa ishlatiladi. `@ts-ignore`, `@ts-expect-error` va `@ts-nocheck` taqiqlangan.

Har bir funksiya, class, metod, property, interface va uning a'zolari, type alias va eksport qilinadigan konstantaga TSDoc yoziladi:

```ts
/**
 * Fetches the public repositories of a GitHub user.
 *
 * @param username - GitHub login of the user.
 * @returns Repositories in the order returned by the API.
 * @throws {GitHubRequestError} When the API responds with a non-success status.
 */
export async function fetchRepositories(username: string): Promise<readonly Repository[]> {
```

## 3. Satr qurish

Taqiqlangan: `${}` bilan template literal, `+` va `+=` bilan satr ulash, `Array.prototype.join()`, `String.prototype.concat()`.

| Vazifa | Ishlat |
| --- | --- |
| Shablon bo'yicha satr (Node.js) | `format('%s: %d repositories', language, count)` (`node:util` dan) |
| Foydalanuvchiga ko'rinadigan matn | i18n kutubxonasi: `t('repos.summary', { language, count })` |
| Ro'yxatni satrga aylantirish | `new Intl.ListFormat('en', { style: 'short', type: 'unit' }).format(names)`, "and" bilan: `type: 'conjunction'` |
| Son, sana va valyuta | `Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat` |
| URL | `new URL('/users/octocat/repos', 'https://api.github.com')`, `url.searchParams.set('per_page', '100')` |
| Fayl yo'li | `path.join()` va `path.resolve()` (`node:path` dan). Bular satr ulash emas, yo'l API'si |
| Ko'p qatorli chiqish | Qatorlar massivini (`readonly string[]`) qaytar va ularni `for...of` ichida `console.log()` bilan birma-bir chiqar |

Ichida `${}` bo'lmagan backtick satr ham kerak emas. Oddiy tirnoq ishlat.

## 4. Massiv va obyektlarni birlashtirish

| Vazifa | Ishlat |
| --- | --- |
| Massivlarni ulash | `[...first, ...second]` |
| Obyektlarni ulash | `{ ...defaults, ...options }` |
| Massivni kengaytirish | `items.push(...more)` |

`first.concat(second)` taqiqlangan.

## 5. Shartlar, null va standart qiymatlar

Taqiqlangan: `? :`, `??`, `??=`, `?.`, `||`, `||=`. JavaScript'da `or` kalit so'zi yo'q, shuning uchun `||` o'rniga quyidagilarni ishlat:

```ts
/**
 * Roles that may edit any post.
 */
const ADMIN_ROLES: ReadonlySet<Role> = new Set(['owner', 'admin']);

/**
 * Tells whether the user may edit the given post.
 *
 * @param user - The user requesting the edit.
 * @param post - The post being edited.
 * @returns True for administrators and for the post author.
 */
function canEdit(user: User, post: Post): boolean {
    if (ADMIN_ROLES.has(user.role)) {
        return true;
    }

    return post.authorId === user.id;
}
```

- **Bir nechta qiymat bilan solishtirish:** `['draft', 'archived'].includes(status)` yoki `Set.has()`.
- **Bir nechta shartdan birortasi:** `conditions.some(Boolean)` yoki erta qaytishlar.
- **Qiymat tanlash:** `Record` lug'ati yoki `switch`:

```ts
/**
 * Display labels for every account status.
 */
const STATUS_LABELS: Readonly<Record<Status, string>> = {
    active: 'Active',
    suspended: 'Suspended',
};
```

Standart qiymatlar:

| Vazifa | Ishlat |
| --- | --- |
| Funksiya parametri | `function paginate(limit = 10): Page` |
| Obyektdan olish | `const { limit = 10, sort = 'name' } = options;` |
| `Map` dan olish | `if (!cache.has(key)) { ... }` va undan keyin `cache.get(key)` ni tekshirish |
| `undefined` yoki `null` | `if (value === undefined) { return fallback; }` va undan keyin tip toraygan qiymat bilan ishlash |

Optional chaining o'rniga qiymatni ochiq tekshir yoki tipni shunday loyihalaki, maydon majburiy bo'lsin.

## 6. Tiplash

`tsconfig.json` minimal talablari:

```json
{
    "compilerOptions": {
        "strict": true,
        "noUncheckedIndexedAccess": true,
        "exactOptionalPropertyTypes": true,
        "noImplicitOverride": true,
        "noImplicitReturns": true,
        "noFallthroughCasesInSwitch": true,
        "noPropertyAccessFromIndexSignature": true,
        "useUnknownInCatchVariables": true
    }
}
```

- **Taqiqlangan:** `any`, `unknown`, `object`, `{}`, `Function`, `as any`, `as unknown as T`, non-null assertion `value!`, yashirin `any`.
- **To'liq annotatsiya:** har bir funksiya parametri va return tipini ochiq yoz.
- **Domen tiplari:** `interface`, `type`, `readonly` maydonlar, `readonly T[]`, `ReadonlyMap`, discriminated union, literal tiplar, `as const` va `satisfies`.
- **Tashqi ma'lumot:** `fetch().json()`, `JSON.parse()` va `process.env` qiymatlari darhol `zod` yoki `valibot` schema'si orqali aniq tipga aylantirilsin. Natijaning tipi `z.infer<typeof Schema>` bo'ladi, shuning uchun kodda `unknown` yozish kerak bo'lmaydi.
- **`catch` bloki:** `catch (error)` ga tip yozma. Xatoni `instanceof` bilan aniq class'ga toraytir.

```ts
/**
 * Shape of a repository returned by the GitHub API.
 */
const RepositorySchema = z.object({
    name: z.string(),
    language: z.string().nullable(),
    stargazers_count: z.number().int().nonnegative(),
});

/**
 * Shape of the repository list returned by the GitHub API.
 */
const RepositoryListSchema = z.array(RepositorySchema);

/**
 * A validated GitHub repository.
 */
type Repository = z.infer<typeof RepositorySchema>;
```

## 7. Testlar

| Vazifa | Vosita |
| --- | --- |
| Test framework | Vitest (loyihada Jest bo'lsa, Jest) |
| React komponentlari | Testing Library |
| HTTP | `msw` yoki `vi.stubGlobal('fetch', ...)` |
| Vaqt | `vi.useFakeTimers()` va `vi.setSystemTime()` |
| Bir nechta holat | `it.each` |
| E2E | Playwright |

- **Nomlar:** `describe` modul yoki funksiya nomini, `it` esa xatti-harakatni aytsin: `it('groups repositories by language')`.
- **Assertion:** `toStrictEqual` ishlat, istisnoni `rejects.toThrow(GitHubRequestError)` bilan tekshir.
- **Yordamchilar:** test faylidagi yordamchi funksiyalarga ham TSDoc yoz.

## 8. To'liq misol

```ts
import { format } from 'node:util';

import type { Repository } from '../github/schemas.js';

/**
 * Repositories that share the same primary language.
 */
export interface LanguageGroup {
    /** Primary language of the repositories. */
    readonly language: string;
    /** Names of the repositories, sorted alphabetically. */
    readonly repositories: readonly string[];
}

/**
 * Label used for repositories that have no detected language.
 */
export const UNKNOWN_LANGUAGE = 'Unknown';

/**
 * Groups repositories by their primary language.
 *
 * @param repositories - Repositories to group.
 * @returns Groups sorted by language name.
 */
export function groupByLanguage(repositories: readonly Repository[]): readonly LanguageGroup[] {
    const groups = new Map<string, string[]>();

    for (const repository of repositories) {
        const language = languageOf(repository);
        const names = groups.get(language);

        if (names === undefined) {
            groups.set(language, [repository.name]);
            continue;
        }

        names.push(repository.name);
    }

    return [...groups.entries()]
        .map(([language, names]) => ({ language, repositories: names.toSorted() }))
        .sort((left, right) => left.language.localeCompare(right.language));
}

/**
 * Formats one report line per language group.
 *
 * @param groups - Language groups to describe.
 * @returns Lines such as "TypeScript: api, web".
 */
export function reportLines(groups: readonly LanguageGroup[]): readonly string[] {
    const list = new Intl.ListFormat('en', { style: 'short', type: 'unit' });

    return groups.map((group) => format('%s: %s', group.language, list.format(group.repositories)));
}

/**
 * Returns the primary language of a repository or the unknown label.
 *
 * @param repository - Repository to inspect.
 * @returns The language name.
 */
function languageOf(repository: Repository): string {
    if (repository.language === null) {
        return UNKNOWN_LANGUAGE;
    }

    return repository.language;
}
```

```ts
import { describe, expect, it } from 'vitest';

import { groupByLanguage, reportLines } from '../../src/reports/language-report.js';
import { aRepository } from '../factories/repository.js';

describe('groupByLanguage', () => {
    it('groups repositories by language', () => {
        const repositories = [
            aRepository({ name: 'web', language: 'TypeScript' }),
            aRepository({ name: 'api', language: 'TypeScript' }),
        ];

        const groups = groupByLanguage(repositories);

        expect(groups).toStrictEqual([{ language: 'TypeScript', repositories: ['api', 'web'] }]);
    });

    it('puts repositories without a language into the unknown group', () => {
        const repositories = [aRepository({ name: 'notes', language: null })];

        const groups = groupByLanguage(repositories);

        expect(groups).toStrictEqual([{ language: 'Unknown', repositories: ['notes'] }]);
    });
});

describe('reportLines', () => {
    it('formats one line per language', () => {
        const groups = [{ language: 'Go', repositories: ['cli', 'server'] }];

        const lines = reportLines(groups);

        expect(lines).toStrictEqual(['Go: cli, server']);
    });
});
```
