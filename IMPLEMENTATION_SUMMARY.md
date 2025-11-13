# Документация по внедрению архитектуры Type (Вид)

## Обзор

Данный документ описывает комплексные изменения, внесенные в систему LAMIS для добавления сущности **Type (Вид)** и реструктуризации системы фильтрации с трех уровней до четырех.

**Период реализации**: ЭТАП 2-6
**Статус**: ✅ Завершено
**Версия**: 1.0

---

## Оглавление

1. [Архитектурные изменения](#архитектурные-изменения)
2. [ЭТАП 2: Backend - Добавление Type](#этап-2-backend---добавление-type)
3. [ЭТАП 3: Backend - SEO-friendly маршруты](#этап-3-backend---seo-friendly-маршруты)
4. [ЭТАП 4: Frontend - TypeScript и API](#этап-4-frontend---typescript-и-api)
5. [ЭТАП 5: Frontend - Компоненты](#этап-5-frontend---компоненты)
6. [Обратная совместимость](#обратная-совместимость)
7. [Использование API](#использование-api)
8. [Миграции базы данных](#миграции-базы-данных)

---

## Архитектурные изменения

### Старая структура (3 уровня)
```
Section (Секция) → Category (Категория) → Collection (Коллекция) → Products
```

### Новая структура (4 уровня)
```
Section (Секция) → Category (Категория) → Collection/Type (Коллекция/Вид) → Products
                                        ↓
                                    Level 3a: Collection
                                    Level 3b: Type (NEW)
```

### Ключевые принципы

1. **Collection и Type - параллельные классификации**
   - Collection используется для мебельных комплектов (например, коллекции ванной мебели)
   - Type используется для санитарной керамики (раковины, унитазы, биде и т.д.)

2. **Взаимоисключающие фильтры**
   - Пользователь может выбрать ИЛИ Collection ИЛИ Type, но не оба одновременно
   - Выбор одного автоматически сбрасывает другое

3. **Nullable поля**
   - `Product.collection` и `Product.type` - nullable ForeignKey
   - Продукт может иметь только одну из этих классификаций или ни одной

4. **Каскадное удаление**
   - При удалении Section/Category - все связанные Type удаляются (CASCADE)
   - При удалении Type - у продуктов поле type устанавливается в NULL (SET_NULL)

---

## ЭТАП 2: Backend - Добавление Type

### 2.1 Модель Type

**Файл**: `apps/products/models.py`

```python
class Type(models.Model):
    """
    Type Model (Вид) - классификация типов продуктов
    Используется для санитарной керамики (раковины, унитазы, биде и т.д.)
    """
    name = models.CharField(
        max_length=150,
        verbose_name="Название типа",
        db_index=True
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
        verbose_name="URL slug"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='types',
        verbose_name="Секция"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='types',
        verbose_name="Категория"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        db_table = 'types'
        ordering = ['section', 'category', 'name']
        unique_together = ('section', 'category', 'name')
        verbose_name = "Тип (Вид)"
        verbose_name_plural = "Типы (Виды)"
        indexes = [
            models.Index(fields=['section', 'category']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.name} ({self.section.name} - {self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### 2.2 Обновление Product модели

**Добавлено поле**:
```python
class Product(models.Model):
    # ... existing fields ...

    type = models.ForeignKey(
        Type,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Тип (Вид)"
    )
```

**Добавлены индексы**:
```python
class Meta:
    indexes = [
        models.Index(fields=['section', 'category', 'collection']),
        models.Index(fields=['section', 'category', 'type']),  # NEW
        models.Index(fields=['is_active', 'created_at']),
    ]
```

### 2.3 Serializer

**Файл**: `apps/products/serializers.py`

```python
class TypeSerializer(serializers.ModelSerializer):
    """Serializer для Type модели"""
    section_name = serializers.CharField(source='section.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Type
        fields = [
            'id',
            'name',
            'slug',
            'section',
            'section_name',
            'category',
            'category_name',
            'description',
            'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']
```

### 2.4 ViewSet

**Файл**: `apps/products/views.py`

```python
class TypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления типами (видами) продуктов

    Endpoints:
    - GET /api/v1/types/ - список всех типов
    - GET /api/v1/types/{id}/ - детали конкретного типа
    - POST /api/v1/types/ - создание нового типа (admin)
    - PUT/PATCH /api/v1/types/{id}/ - обновление типа (admin)
    - DELETE /api/v1/types/{id}/ - удаление типа (admin)

    Фильтры:
    - ?section_id=1 - фильтр по секции
    - ?category_id=2 - фильтр по категории
    - ?search=раковина - поиск по названию
    """
    queryset = Type.objects.select_related('section', 'category').all()
    serializer_class = TypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TypeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
```

### 2.5 Фильтры

**Файл**: `apps/products/filters.py`

```python
class TypeFilter(filters.FilterSet):
    """Фильтры для Type модели"""
    section_id = filters.NumberFilter(field_name='section__id')
    section_slug = filters.CharFilter(field_name='section__slug')
    category_id = filters.NumberFilter(field_name='category__id')
    category_slug = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Type
        fields = ['section_id', 'section_slug', 'category_id', 'category_slug']

# Обновлен ProductFilter
class ProductFilter(filters.FilterSet):
    # ... existing filters ...

    type_id = filters.CharFilter(method='filter_type')
    type_slug = filters.CharFilter(field_name='type__slug')

    def filter_type(self, queryset, name, value):
        """Фильтрация по ID или slug типа"""
        if value.isdigit():
            return queryset.filter(type__id=int(value))
        return queryset.filter(type__slug=value)
```

### 2.6 URL маршруты

**Файл**: `apps/products/urls.py`

```python
router.register(r'types', TypeViewSet, basename='type')
```

### 2.7 Django Admin

**Файл**: `apps/products/admin.py`

```python
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'category', 'slug', 'created_at']
    list_filter = ['section', 'category', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    ordering = ['section', 'category', 'name']
```

---

## ЭТАП 3: Backend - SEO-friendly маршруты

### 3.1 Структура URL

**Цель**: Создать человекочитаемые URL для навигации по каталогу

```
/api/v1/catalog/{section_slug}/
/api/v1/catalog/{section_slug}/{category_slug}/
/api/v1/catalog/{section_slug}/{category_slug}/{collection_or_type_slug}/
/api/v1/catalog/browse/
```

### 3.2 Catalog Views

**Файл**: `apps/products/catalog_views.py`

#### CatalogSectionView
```python
GET /api/v1/catalog/{section_slug}/

Возвращает:
- Информацию о секции
- Список категорий, доступных в этой секции

Пример:
GET /api/v1/catalog/lamis/

Response:
{
  "section": {
    "id": 1,
    "name": "Lamis",
    "slug": "lamis",
    "description": "..."
  },
  "categories": [
    {
      "id": 1,
      "name": "Ванная мебель",
      "slug": "bathroom-furniture"
    },
    {
      "id": 2,
      "name": "Санитарная керамика",
      "slug": "sanitary-ceramics"
    }
  ]
}
```

#### CatalogCategoryView
```python
GET /api/v1/catalog/{section_slug}/{category_slug}/

Возвращает:
- Информацию о секции
- Информацию о категории
- Список коллекций для этой секции+категории
- Список типов для этой секции+категории

Пример:
GET /api/v1/catalog/lamis/bathroom-furniture/

Response:
{
  "section": {...},
  "category": {...},
  "collections": [
    {"id": 1, "name": "Siena", "slug": "siena"},
    {"id": 2, "name": "Naples", "slug": "naples"}
  ],
  "types": []
}
```

#### CatalogProductsView
```python
GET /api/v1/catalog/{section_slug}/{category_slug}/{item_slug}/

Алгоритм:
1. Пытается найти Collection с указанным slug
2. Если не найдена, пытается найти Type с указанным slug
3. Если ни одна не найдена - возвращает 404

Возвращает:
- Информацию о секции
- Информацию о категории
- Информацию о коллекции ИЛИ типе
- Список продуктов

Пример (Collection):
GET /api/v1/catalog/lamis/bathroom-furniture/siena/

Response:
{
  "section": {...},
  "category": {...},
  "collection": {"id": 1, "name": "Siena", "slug": "siena"},
  "type": null,
  "products": [...]
}

Пример (Type):
GET /api/v1/catalog/lamis/sanitary-ceramics/sinks/

Response:
{
  "section": {...},
  "category": {...},
  "collection": null,
  "type": {"id": 1, "name": "Раковины", "slug": "sinks"},
  "products": [...]
}
```

#### CatalogBrowseView
```python
GET /api/v1/catalog/browse/

Возвращает:
- Полную структуру каталога для построения навигационных меню

Response:
{
  "catalog": [
    {
      "section": {"id": 1, "name": "Lamis", "slug": "lamis"},
      "categories": [
        {
          "category": {"id": 1, "name": "Ванная мебель"},
          "collections": [...],
          "types": []
        },
        {
          "category": {"id": 2, "name": "Санитарная керамика"},
          "collections": [],
          "types": [...]
        }
      ]
    }
  ]
}
```

### 3.3 URL Configuration

**Файл**: `apps/products/urls.py`

```python
from apps.products.catalog_views import (
    CatalogSectionView,
    CatalogCategoryView,
    CatalogProductsView,
    CatalogBrowseView,
)

urlpatterns = [
    # ... existing patterns ...

    # SEO-friendly catalog navigation
    path('catalog/browse/', CatalogBrowseView.as_view(), name='catalog-browse'),
    path('catalog/<slug:section_slug>/', CatalogSectionView.as_view(), name='catalog-section'),
    path('catalog/<slug:section_slug>/<slug:category_slug>/', CatalogCategoryView.as_view(), name='catalog-category'),
    path('catalog/<slug:section_slug>/<slug:category_slug>/<slug:item_slug>/', CatalogProductsView.as_view(), name='catalog-products'),
]
```

---

## ЭТАП 4: Frontend - TypeScript и API

### 4.1 Обновление Product Type

**Файл**: `types/product.ts`

```typescript
export interface Product {
  id: string | number;
  name: string;
  price: string;
  image: string;
  category: string;

  // UPDATED: Renamed from brandId
  section?: number;
  section_name?: string;

  category_name?: string;

  // Existing
  collection?: number | null;
  collection_name?: string | null;

  // NEW: Type support
  type?: number | null;
  type_name?: string | null;

  isNew?: boolean;
  is_new?: boolean;
  is_on_sale?: boolean;
  inStock?: boolean;
  slug?: string;
  sku?: string;
  description?: string;
  main_image_url?: string;
  hover_image_url?: string;

  // DEPRECATED (backward compatibility)
  brandId?: number; // Use 'section' instead
}
```

### 4.2 API Service Layer

**Файл**: `services/api/products.ts`

#### Type Interface
```typescript
export interface Type {
  id: number;
  name: string;
  slug: string;
  description?: string;
  section: number;
  category: number;
  section_name?: string;
  category_name?: string;
  created_at?: string;
}
```

#### Filters Interface
```typescript
export interface ProductsFilters {
  sectionId?: number | null; // RENAMED from brandId
  categoryId?: number | null;
  collectionId?: number | null;
  typeId?: number | null; // NEW
  sortBy?: string;
  page?: number;
  itemsPerPage?: number;
  inStock?: boolean;

  // DEPRECATED (backward compatibility)
  brandId?: number | null; // Use sectionId instead
}
```

#### Fetch Types Function
```typescript
/**
 * Получить все типы (опционально фильтрация по секции и категории)
 */
export async function fetchTypes(
  sectionId?: number | null,
  categoryId?: number | null
): Promise<Type[]> {
  const params = new URLSearchParams();

  if (sectionId !== null && sectionId !== undefined) {
    params.append('section_id', sectionId.toString());
  }
  if (categoryId !== null && categoryId !== undefined) {
    params.append('category_id', categoryId.toString());
  }

  const url = `${API_BASE_URL}/types/${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch types: ${response.statusText}`);
  }

  const data: DjangoPage<Type> = await response.json();
  return data.results;
}
```

#### Updated fetchProducts
```typescript
export async function fetchProducts(
  filters: ProductsFilters = {}
): Promise<PaginatedResponse<Product>> {
  const params = new URLSearchParams();

  // Support both sectionId (new) and brandId (deprecated)
  const sectionId = filters.sectionId ?? filters.brandId;
  if (sectionId !== null && sectionId !== undefined) {
    params.append('section_id', sectionId.toString());
  }

  if (filters.categoryId !== null && filters.categoryId !== undefined) {
    params.append('category_id', filters.categoryId.toString());
  }

  if (filters.collectionId !== null && filters.collectionId !== undefined) {
    params.append('collection_id', filters.collectionId.toString());
  }

  // NEW: Type filter
  if (filters.typeId !== null && filters.typeId !== undefined) {
    params.append('type_id', filters.typeId.toString());
  }

  // ... rest of implementation
}
```

### 4.3 Zustand Store Update

**Файл**: `store/filtersStore.ts`

#### State Interface
```typescript
interface FiltersState {
  // ===== ЧЕТЫРЕХУРОВНЕВОЕ СОСТОЯНИЕ =====
  selectedSectionId: number | null; // Level 1 (renamed from selectedBrandId)
  selectedCategoryId: number | null; // Level 2
  selectedCollectionId: number | null; // Level 3a
  selectedTypeId: number | null; // Level 3b - NEW

  // Доступные опции для каждого уровня
  availableCategories: Category[];
  availableCollections: Collection[];
  availableTypes: Type[]; // NEW

  // Loading states
  categoriesLoading: boolean;
  collectionsLoading: boolean;
  typesLoading: boolean; // NEW

  // Дополнительные фильтры
  sortBy: string;
  selectedColors: string[];

  // ===== ДЕЙСТВИЯ =====
  setSectionId: (sectionId: number | null) => Promise<void>;
  setCategoryId: (categoryId: number | null) => Promise<void>;
  setCollectionId: (collectionId: number | null) => void;
  setTypeId: (typeId: number | null) => void; // NEW

  loadCategories: (sectionId: number | null) => Promise<void>;
  loadCollections: (sectionId: number | null, categoryId: number | null) => Promise<void>;
  loadTypes: (sectionId: number | null, categoryId: number | null) => Promise<void>; // NEW

  // ... other actions
}
```

#### Load Types Action
```typescript
loadTypes: async (sectionId: number | null, categoryId: number | null) => {
  console.log('🔄 loadTypes for section:', sectionId, 'category:', categoryId);
  set({ typesLoading: true });

  try {
    const types = await fetchTypes(sectionId, categoryId);
    console.log('✓ Loaded types:', types);
    set({ availableTypes: types });
  } catch (error) {
    console.error('❌ Failed to load types:', error);
    set({ availableTypes: [] });
  } finally {
    set({ typesLoading: false });
  }
}
```

#### Set Type Action (with mutual exclusivity)
```typescript
setTypeId: (typeId: number | null) => {
  console.log('🔹 [Level 3b] setTypeId:', typeId);

  // Если выбираем тип, сбрасываем коллекцию (взаимоисключающие)
  set({
    selectedTypeId: typeId,
    selectedCollectionId: typeId !== null ? null : get().selectedCollectionId
  });
}
```

#### Set Collection Action (with mutual exclusivity)
```typescript
setCollectionId: (collectionId: number | null) => {
  console.log('🔹 [Level 3a] setCollectionId:', collectionId);

  // Если выбираем коллекцию, сбрасываем тип (взаимоисключающие)
  set({
    selectedCollectionId: collectionId,
    selectedTypeId: collectionId !== null ? null : get().selectedTypeId
  });
}
```

#### Updated Set Category Action
```typescript
setCategoryId: async (categoryId: number | null) => {
  console.log('🔹 [Level 2] setCategoryId:', categoryId);

  const state = get();

  // Сбрасываем коллекцию и тип
  set({
    selectedCategoryId: categoryId,
    selectedCollectionId: null,
    selectedTypeId: null,
  });

  // Загружаем коллекции И типы для выбранной секции и категории
  if (categoryId !== null && state.selectedSectionId !== null) {
    await Promise.all([
      get().loadCollections(state.selectedSectionId, categoryId),
      get().loadTypes(state.selectedSectionId, categoryId), // NEW
    ]);
  } else {
    set({ availableCollections: [], availableTypes: [] });
  }
}
```

---

## ЭТАП 5: Frontend - Компоненты

### 5.1 Catalog Component Updates

**Файл**: `components/catalog/index.tsx`

#### State Management
```typescript
const Catalog: FC = () => {
  const {
    // Четырехуровневая система
    selectedSectionId,     // Level 1 (renamed from selectedBrandId)
    selectedCategoryId,    // Level 2
    selectedCollectionId,  // Level 3a
    selectedTypeId,        // Level 3b - NEW
    availableCategories,
    availableCollections,
    availableTypes,        // NEW
    setSectionId,
    setCategoryId,
    setCollectionId,
    setTypeId,             // NEW
    sortBy,
    setSortBy,
  } = useFiltersStore();

  // ... rest of component
}
```

#### URL Parameters Handling
```typescript
const searchParams = useSearchParams();

// Support both old and new parameter names
const sectionIdFromUrl = searchParams.get('sectionId') || searchParams.get('brandId');
const categoryIdFromUrl = searchParams.get('categoryId');
const collectionIdFromUrl = searchParams.get('collectionId');
const typeIdFromUrl = searchParams.get('typeId'); // NEW
```

#### Filter Initialization
```typescript
useEffect(() => {
  const initializeFilters = async () => {
    // Level 1: Section
    if (sectionIdFromUrl) {
      const sectionId = parseInt(sectionIdFromUrl, 10);
      if (!isNaN(sectionId)) {
        await setSectionId(sectionId);
      }
    } else {
      await setSectionId(null);
    }

    // Level 2: Category
    if (categoryIdFromUrl && sectionIdFromUrl) {
      const categoryId = parseInt(categoryIdFromUrl, 10);
      if (!isNaN(categoryId)) {
        await setCategoryId(categoryId);
      }
    }

    // Level 3a: Collection
    if (collectionIdFromUrl) {
      const collectionId = parseInt(collectionIdFromUrl, 10);
      if (!isNaN(collectionId)) {
        setCollectionId(collectionId);
      }
    } else {
      setCollectionId(null);
    }

    // Level 3b: Type - NEW
    if (typeIdFromUrl) {
      const typeId = parseInt(typeIdFromUrl, 10);
      if (!isNaN(typeId)) {
        setTypeId(typeId);
      }
    } else {
      setTypeId(null);
    }

    setCurrentPage(1);
  };

  initializeFilters();
}, [sectionIdFromUrl, categoryIdFromUrl, collectionIdFromUrl, typeIdFromUrl]);
```

#### Product Fetching
```typescript
useEffect(() => {
  const loadProducts = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchProducts({
        sectionId: selectedSectionId,
        categoryId: selectedCategoryId,
        collectionId: selectedCollectionId,
        typeId: selectedTypeId, // NEW
        sortBy: sortBy,
        page: currentPage,
        itemsPerPage: parseInt(itemsPerPage, 10),
      });

      setApiProducts(response.data);
      setTotalProducts(response.pagination.totalItems);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError(err instanceof Error ? err.message : 'Failed to load products');
    } finally {
      setIsLoading(false);
    }
  };

  loadProducts();
}, [selectedSectionId, selectedCategoryId, selectedCollectionId, selectedTypeId, sortBy, currentPage, itemsPerPage]);
```

#### Type Filter UI
```tsx
{/* УРОВЕНЬ 3b: ДИНАМИЧЕСКИЕ ТАБЫ для фильтрации по типам - NEW */}
{selectedCategoryId !== null && availableTypes.length > 0 && (
  <div className="flex flex-wrap gap-3 md:gap-3.5 mb-8">
    <Button
      className="h-8 md:h-10 py-1 md:py-2 px-3 md:px-4"
      variant={selectedTypeId === null && selectedCollectionId === null ? 'primary' : 'outline'}
      onClick={() => handleTypeClick(null)}
    >
      Все типы
    </Button>

    {availableTypes.map((type) => (
      <Button
        key={type.id}
        className="h-8 md:h-10 py-1 md:py-2 px-3 md:px-4"
        variant={isTypeActive(type.id) ? 'primary' : 'outline'}
        onClick={() => handleTypeClick(type.id)}
      >
        {type.name}
      </Button>
    ))}
  </div>
)}
```

#### Handler Functions
```typescript
// Type click handler
const handleTypeClick = (typeId: number | null) => {
  setTypeId(typeId);
  setCurrentPage(1);
};

// Type active state checker
const isTypeActive = (typeId: number | null) => {
  return selectedTypeId === typeId;
};
```

---

## Обратная совместимость

### Переименование Brand → Section

Все упоминания "Brand" были заменены на "Section" с сохранением обратной совместимости:

#### Backend
```python
# Product model
section = models.ForeignKey(Section, ...)  # NEW name

# API parameters support both names
section_id = filters.sectionId ?? filters.brandId  # Accepts both
```

#### Frontend
```typescript
// Store
selectedSectionId: number | null;  // NEW name
selectedBrandId: number | null;    // DEPRECATED alias

// API filters
interface ProductsFilters {
  sectionId?: number | null;  // NEW name
  brandId?: number | null;    // DEPRECATED - redirects to sectionId
}

// URL parameters
const sectionId = searchParams.get('sectionId') || searchParams.get('brandId');
```

### Миграция данных

**Шаг 1**: Обновить код (завершено)
**Шаг 2**: Обновить клиентские приложения для использования новых полей
**Шаг 3**: Удалить deprecated поля в будущей версии (2.0)

### Deprecated методы

```typescript
// Store
setBrandId: async (brandId: number | null) => {
  console.log('⚠️ [DEPRECATED] setBrandId called, using setSectionId instead');
  await get().setSectionId(brandId);
}
```

---

## Использование API

### Базовые примеры

#### 1. Получить все типы для секции
```bash
GET /api/v1/types/?section_id=1

Response:
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Раковины",
      "slug": "sinks",
      "section": 1,
      "section_name": "Lamis",
      "category": 2,
      "category_name": "Санитарная керамика",
      "description": "Встроенные и накладные раковины",
      "created_at": "2025-01-15T10:30:00Z"
    },
    ...
  ]
}
```

#### 2. Получить типы для секции и категории
```bash
GET /api/v1/types/?section_id=1&category_id=2

Response:
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Раковины",
      "slug": "sinks",
      ...
    },
    {
      "id": 2,
      "name": "Унитазы",
      "slug": "toilets",
      ...
    },
    {
      "id": 3,
      "name": "Биде",
      "slug": "bidets",
      ...
    }
  ]
}
```

#### 3. Фильтровать продукты по типу
```bash
GET /api/v1/products/?section_id=1&category_id=2&type_id=1

Response:
{
  "count": 12,
  "results": [
    {
      "id": 101,
      "name": "Раковина встроенная Classic",
      "section": 1,
      "section_name": "Lamis",
      "category": 2,
      "category_name": "Санитарная керамика",
      "type": 1,
      "type_name": "Раковины",
      "collection": null,
      "collection_name": null,
      ...
    },
    ...
  ]
}
```

#### 4. SEO-friendly навигация
```bash
# Получить категории секции
GET /api/v1/catalog/lamis/

# Получить коллекции и типы категории
GET /api/v1/catalog/lamis/sanitary-ceramics/

# Получить продукты типа
GET /api/v1/catalog/lamis/sanitary-ceramics/sinks/

# Получить полную структуру каталога
GET /api/v1/catalog/browse/
```

### Frontend примеры

#### 1. Загрузить типы в store
```typescript
import { useFiltersStore } from '@/store/filtersStore';

function MyComponent() {
  const { selectedSectionId, selectedCategoryId, loadTypes, availableTypes } = useFiltersStore();

  useEffect(() => {
    if (selectedSectionId && selectedCategoryId) {
      loadTypes(selectedSectionId, selectedCategoryId);
    }
  }, [selectedSectionId, selectedCategoryId]);

  return (
    <div>
      {availableTypes.map(type => (
        <div key={type.id}>{type.name}</div>
      ))}
    </div>
  );
}
```

#### 2. Фильтровать продукты по типу
```typescript
import { fetchProducts } from '@/services/api/products';

async function loadProducts() {
  const response = await fetchProducts({
    sectionId: 1,
    categoryId: 2,
    typeId: 1, // Filter by Type
    page: 1,
    itemsPerPage: 20
  });

  console.log('Products:', response.data);
  console.log('Total:', response.pagination.totalItems);
}
```

#### 3. Установить фильтр типа
```typescript
import { useFiltersStore } from '@/store/filtersStore';

function TypeFilter() {
  const { selectedTypeId, setTypeId, availableTypes } = useFiltersStore();

  return (
    <div>
      {availableTypes.map(type => (
        <button
          key={type.id}
          onClick={() => setTypeId(type.id)}
          className={selectedTypeId === type.id ? 'active' : ''}
        >
          {type.name}
        </button>
      ))}
    </div>
  );
}
```

---

## Миграции базы данных

### История миграций

#### 0005_type_product_products_section_c18087_idx_and_more.py

**Дата**: 2025-01-15

**Изменения**:
1. Создание модели Type
2. Добавление связей Type → Section и Type → Category
3. Добавление поля Product.type (nullable ForeignKey)
4. Создание индексов для оптимизации запросов

**Важно**: Порядок операций критичен - поле должно существовать до создания индексов на него.

```python
operations = [
    # Шаг 1: Создать модель Type
    migrations.CreateModel(
        name='Type',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('name', models.CharField(db_index=True, max_length=150)),
            ('slug', models.SlugField(blank=True, max_length=180, unique=True)),
            ('description', models.TextField(blank=True, null=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ],
        options={
            'db_table': 'types',
            'ordering': ['section', 'category', 'name'],
        },
    ),

    # Шаг 2: Добавить ForeignKeys к Type
    migrations.AddField(
        model_name='type',
        name='category',
        field=models.ForeignKey(on_delete=models.CASCADE, related_name='types', to='products.category'),
    ),
    migrations.AddField(
        model_name='type',
        name='section',
        field=models.ForeignKey(on_delete=models.CASCADE, related_name='types', to='products.section'),
    ),

    # Шаг 3: Добавить поле type к Product ПЕРЕД созданием индексов
    migrations.AddField(
        model_name='product',
        name='type',
        field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='products', to='products.type'),
    ),

    # Шаг 4: Теперь создать индексы, которые ссылаются на поле type
    migrations.AddIndex(
        model_name='product',
        index=models.Index(fields=['section', 'category', 'collection'], name='products_section_c18087_idx'),
    ),
    migrations.AddIndex(
        model_name='product',
        index=models.Index(fields=['section', 'category', 'type'], name='products_section_c18088_idx'),
    ),

    # Шаг 5: Ограничения unique_together для Type
    migrations.AlterUniqueTogether(
        name='type',
        unique_together={('section', 'category', 'name')},
    ),
]
```

### Команды для применения миграций

```bash
# Создать миграции
python manage.py makemigrations

# Просмотреть SQL миграций (без применения)
python manage.py sqlmigrate products 0005

# Применить миграции
python manage.py migrate

# Откатить миграцию (если нужно)
python manage.py migrate products 0004
```

---

## Тестирование

### Backend тесты

#### Создание Type через API
```bash
curl -X POST http://127.0.0.1:8000/api/v1/types/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Раковины",
    "section": 1,
    "category": 2,
    "description": "Встроенные и накладные раковины"
  }'
```

#### Получение типов
```bash
curl http://127.0.0.1:8000/api/v1/types/?section_id=1&category_id=2
```

#### Фильтрация продуктов
```bash
curl http://127.0.0.1:8000/api/v1/products/?type_id=1
```

### Frontend тесты

#### Проверка загрузки типов
```typescript
// В DevTools Console
const store = useFiltersStore.getState();
await store.setSectionId(1);
await store.setCategoryId(2);
console.log('Available Types:', store.availableTypes);
```

#### Проверка взаимоисключения фильтров
```typescript
const store = useFiltersStore.getState();

// Выбрать коллекцию
store.setCollectionId(1);
console.log('Collection:', store.selectedCollectionId); // 1
console.log('Type:', store.selectedTypeId); // null

// Выбрать тип - коллекция должна сброситься
store.setTypeId(2);
console.log('Collection:', store.selectedCollectionId); // null
console.log('Type:', store.selectedTypeId); // 2
```

---

## Производительность

### Оптимизация запросов

#### Backend
```python
# select_related для оптимизации запросов
Type.objects.select_related('section', 'category').all()

# prefetch_related для обратных связей
Section.objects.prefetch_related('types').all()

# Индексы для быстрой фильтрации
class Meta:
    indexes = [
        models.Index(fields=['section', 'category']),
        models.Index(fields=['section', 'category', 'type']),
    ]
```

#### Frontend
```typescript
// Zustand persist для кеширования state
persist(
  (set, get) => ({...}),
  { name: 'filters-storage-v4' }
)

// useMemo для оптимизации пересчетов
const filteredProducts = useMemo(() => {
  return apiProducts;
}, [apiProducts]);
```

---

## Контрольный список внедрения

### Backend ✅
- [x] Создана модель Type
- [x] Добавлено поле Product.type
- [x] Создан TypeSerializer
- [x] Создан TypeViewSet
- [x] Добавлен TypeFilter
- [x] Обновлен ProductFilter для type_id
- [x] Зарегистрированы URL маршруты
- [x] Настроен Django Admin
- [x] Создана и применена миграция
- [x] Созданы catalog views для SEO URL
- [x] Протестированы API endpoints

### Frontend ✅
- [x] Обновлен Product type definition
- [x] Добавлен Type interface
- [x] Создана функция fetchTypes()
- [x] Обновлен ProductsFilters interface
- [x] Обновлен Zustand store (4-level hierarchy)
- [x] Добавлен loadTypes action
- [x] Реализована логика взаимоисключения
- [x] Обновлен Catalog component
- [x] Добавлен UI для Type фильтров
- [x] Обновлена обработка URL параметров
- [x] Протестирована функциональность

### Документация ✅
- [x] Создан IMPLEMENTATION_SUMMARY.md
- [x] Документированы архитектурные решения
- [x] Описаны все API endpoints
- [x] Добавлены примеры использования
- [x] Документирована обратная совместимость

---

## Следующие шаги

### Рекомендации по дальнейшему развитию

1. **ЭТАП 7: Обновление роутинга**
   - Добавить динамические маршруты в Next.js
   - Создать страницы для Type-based навигации
   - Реализовать breadcrumbs

2. **ЭТАП 8: Административная панель**
   - Улучшить UI для управления Type
   - Добавить bulk operations
   - Создать preview режим

3. **ЭТАП 9: SEO оптимизация**
   - Добавить мета-теги для Type страниц
   - Создать XML sitemap
   - Настроить Open Graph tags

4. **Удаление deprecated кода (версия 2.0)**
   - Удалить поля brandId
   - Удалить deprecated методы
   - Обновить все компоненты

5. **Тестирование**
   - Написать unit тесты для backend
   - Написать integration тесты
   - Добавить E2E тесты для frontend

---

## Контакты и поддержка

**Версия документа**: 1.0
**Дата последнего обновления**: 2025-01-15
**Автор**: LAMIS Development Team

Для вопросов и предложений создайте issue в репозитории проекта.

---

---

## ЭТАП 7: Frontend - Динамические маршруты и навигация

### 7.1 Обзор

Созданы SEO-friendly динамические маршруты в Next.js 13+ App Router для навигации по каталогу с поддержкой Type.

### 7.2 Структура маршрутов

```
/catalog/[sectionSlug]/                                    - Категории секции
/catalog/[sectionSlug]/[categorySlug]/                    - Коллекции и типы категории
/catalog/[sectionSlug]/[categorySlug]/[itemSlug]/         - Продукты (Collection или Type)
```

### 7.3 API функции для навигации

**Файл**: `services/api/products.ts` (добавлены функции)

```typescript
// Интерфейсы ответов
export interface Section {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
}

export interface CatalogSectionResponse {
  section: Section;
  categories: Category[];
}

export interface CatalogCategoryResponse {
  section: Section;
  category: Category;
  collections: Collection[];
  types: Type[];
}

export interface CatalogProductsResponse {
  section: Section;
  category: Category;
  collection: Collection | null;
  type: Type | null;
  products: Product[];
}

// API функции
export async function fetchCatalogSection(sectionSlug: string): Promise<CatalogSectionResponse>
export async function fetchCatalogCategory(sectionSlug: string, categorySlug: string): Promise<CatalogCategoryResponse>
export async function fetchCatalogProducts(sectionSlug: string, categorySlug: string, itemSlug: string): Promise<CatalogProductsResponse>
export async function fetchCatalogBrowse(): Promise<{ catalog: CatalogStructure[] }>
```

### 7.4 Страница секции

**Файл**: `app/catalog/[sectionSlug]/page.tsx`

**Функциональность**:
- Отображает список категорий для выбранной секции
- Breadcrumbs: Главная → Каталог → {Section}
- Grid layout с карточками категорий
- Ссылки на страницы категорий

**Пример URL**: `/catalog/lamis/`

### 7.5 Страница категории

**Файл**: `app/catalog/[sectionSlug]/[categorySlug]/page.tsx`

**Функциональность**:
- Отображает коллекции И типы для категории
- Breadcrumbs: Главная → Каталог → {Section} → {Category}
- Два раздела: "Коллекции" и "Или выберите по типу"
- Grid layout с карточками
- Поддержка изображений для коллекций

**Пример URL**: `/catalog/lamis/bathroom-furniture/`

### 7.6 Страница продуктов

**Файл**: `app/catalog/[sectionSlug]/[categorySlug]/[itemSlug]/page.tsx`

**Функциональность**:
- Отображает продукты для коллекции ИЛИ типа
- Breadcrumbs: Главная → Каталог → {Section} → {Category} → {Collection/Type}
- Автоматически определяет, что отображать (коллекция или тип)
- Grid товаров с использованием CatalogCardResponsive
- Empty state для пустых результатов

**Примеры URL**:
- `/catalog/lamis/bathroom-furniture/siena/` (Коллекция)
- `/catalog/lamis/sanitary-ceramics/sinks/` (Тип)

### 7.7 Breadcrumbs

Breadcrumbs реализованы на всех страницах с использованием компонента `Breadcrumbs`:

```tsx
<Breadcrumbs
  items={[
    { label: 'Главная', href: '/' },
    { label: 'Каталог', href: '/catalog' },
    { label: section.name, href: `/catalog/${sectionSlug}` },
    { label: category.name },
  ]}
  variant="light"
  resetPosition
/>
```

---

## ЭТАП 8: Django Admin - Улучшения и Bulk Operations

### 8.1 Обзор

Значительно улучшена административная панель Django для управления Type и Collection с добавлением bulk operations.

### 8.2 Улучшенный TypeAdmin

**Файл**: `apps/products/admin.py`

#### Новые возможности:

**1. Fieldsets с группировкой полей**
```python
fieldsets = (
    ('Основная информация', {
        'fields': ('name', 'slug', 'description'),
        'description': 'Базовая информация о типе продукта'
    }),
    ('Классификация', {
        'fields': ('section', 'category'),
    }),
    ('Статистика', {
        'fields': ('product_count', 'created_at'),
        'classes': ('collapse',),
    }),
)
```

**2. Inline редактирование продуктов**
```python
inlines = [ProductInline]

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ['name', 'price', 'is_new', 'is_on_sale', 'slug']
    readonly_fields = ['slug']
    show_change_link = True
```

**3. Кастомные колонки в списке**
- `product_count` - количество товаров с кликабельной ссылкой
- `slug_display` - красиво отформатированный slug в `<code>` теге

**4. Оптимизированные запросы**
```python
def get_queryset(self, request):
    queryset = super().get_queryset(request)
    queryset = queryset.select_related('section', 'category')
    queryset = queryset.annotate(
        _product_count=Count('products', distinct=True)
    )
    return queryset
```

**5. Bulk Actions**

##### a) Дублирование типов
```python
def duplicate_type(self, request, queryset):
    for type_obj in queryset:
        type_obj.pk = None
        type_obj.name = f"{type_obj.name} (копия)"
        type_obj.slug = ""  # Auto-generated
        type_obj.save()
```

##### b) Экспорт в CSV
```python
def export_as_csv(self, request, queryset):
    # Exports: ID, Название, Slug, Секция, Категория, Товаров, Дата создания
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="types.csv"'
    # ... write CSV data
    return response
```

### 8.3 Улучшенный CollectionAdmin

Аналогичные улучшения для Collection:
- Fieldsets с группировкой
- Inline редактирование продуктов
- `product_count` с ссылкой
- Bulk action "Дублировать коллекции"

### 8.4 Использование админ-панели

#### Дублирование типов:
1. Выберите типы в списке (checkbox)
2. Выберите "Дублировать выбранные типы" в dropdown
3. Нажмите "Выполнить"

#### Экспорт в CSV:
1. Выберите типы для экспорта
2. Выберите "Экспортировать в CSV"
3. Файл `types.csv` загрузится автоматически

---

## ЭТАП 9: SEO Оптимизация

### 9.1 Обзор

Добавлены комплексные SEO мета-теги, Open Graph теги, и автоматическая генерация XML sitemap.

### 9.2 Мета-теги для динамических страниц

Все три уровня динамических маршрутов получили функцию `generateMetadata()` для Next.js 13+.

#### Страница секции (Level 1)

**Файл**: `app/catalog/[sectionSlug]/page.tsx`

```typescript
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const data = await fetchCatalogSection(sectionSlug);
  const { section, categories } = data;

  return {
    title: `${section.name} - Каталог | LAMIS`,
    description: section.description || `Выберите категорию в секции ${section.name}...`,
    keywords: `${section.name}, каталог, ${categories.map(c => c.name).join(', ')}`,
    openGraph: {
      title: `${section.name} - Каталог`,
      description: section.description || `Каталог товаров ${section.name}`,
      url: `https://lamis.ru/catalog/${sectionSlug}`,
      siteName: 'LAMIS',
      type: 'website',
      images: [{ url: section.image, width: 1200, height: 630 }]
    },
    twitter: {
      card: 'summary_large_image',
      title: `${section.name} - Каталог`,
    },
    alternates: {
      canonical: `https://lamis.ru/catalog/${sectionSlug}`,
    },
  };
}
```

#### Страница категории (Level 2)

**Файл**: `app/catalog/[sectionSlug]/[categorySlug]/page.tsx`

Аналогичная структура с:
- Динамическим title включающим section и category
- Keywords из коллекций и типов
- Open Graph теги

#### Страница продуктов (Level 3)

**Файл**: `app/catalog/[sectionSlug]/[categorySlug]/[itemSlug]/page.tsx`

Расширенные мета-теги:
- Изображения продуктов для Open Graph (до 4 изображений)
- Robots meta tags для индексации
- Keywords из названий продуктов
- Поддержка как Collection, так и Type

```typescript
openGraph: {
  images: productImages.length
    ? productImages.map(img => ({
        url: img,
        width: 800,
        height: 600,
        alt: itemName,
      }))
    : [],
},
robots: {
  index: true,
  follow: true,
  'max-image-preview': 'large',
  'max-snippet': -1,
}
```

### 9.3 XML Sitemap Generator

**Файл**: `app/sitemap.ts`

Автоматически генерирует sitemap со всеми страницами каталога.

```typescript
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const { catalog } = await fetchCatalogBrowse();

  const routes: MetadataRoute.Sitemap = [
    // Static pages
    { url: baseUrl, priority: 1, changeFrequency: 'daily' },
    { url: `${baseUrl}/catalog`, priority: 0.9 },

    // Dynamic section pages
    { url: `${baseUrl}/catalog/${section.slug}`, priority: 0.8 },

    // Dynamic category pages
    { url: `${baseUrl}/catalog/${section.slug}/${category.slug}`, priority: 0.7 },

    // Dynamic collection/type pages
    { url: `${baseUrl}/catalog/${section.slug}/${category.slug}/${item.slug}`, priority: 0.6 },
  ];

  return routes;
}
```

**Характеристики**:
- Автоматическое обновление при добавлении новых секций/категорий/типов
- Приоритеты страниц (1.0 для главной, 0.6 для товаров)
- Change frequency для управления частотой индексации
- Fallback к минимальному sitemap при ошибках API

**URL**: `https://lamis.ru/sitemap.xml`

### 9.4 Robots.txt

**Файл**: `app/robots.ts`

```typescript
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/admin/', '/profile/', '/login/'],
      },
      {
        userAgent: 'Googlebot',
        allow: '/',
        disallow: ['/api/', '/admin/'],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
    host: baseUrl,
  };
}
```

**URL**: `https://lamis.ru/robots.txt`

### 9.5 SEO Best Practices

#### Canonical URLs
Все страницы имеют canonical URL для предотвращения дублирования:
```typescript
alternates: {
  canonical: `https://lamis.ru/catalog/${sectionSlug}`,
}
```

#### Structured Data
Рекомендуется добавить JSON-LD для:
- Breadcrumbs
- Product schema
- Organization schema

#### Performance
- Server-side rendering (SSR) для всех динамических страниц
- Оптимизированные API запросы с `select_related`
- Image optimization через Next.js Image component (рекомендуется)

---

## Тестирование этапов 7-9

### ЭТАП 7: Роутинг

```bash
# Запустить frontend
cd frontend-lamis
npm run dev

# Проверить маршруты
# http://localhost:3000/catalog/lamis/
# http://localhost:3000/catalog/lamis/bathroom-furniture/
# http://localhost:3000/catalog/lamis/sanitary-ceramics/sinks/
```

### ЭТАП 8: Django Admin

```bash
# Запустить backend
cd backend-lamis
python manage.py runserver

# Открыть админку
# http://127.0.0.1:8000/admin/products/type/
# Проверить bulk actions, inline editing, fieldsets
```

### ЭТАП 9: SEO

```bash
# Проверить sitemap
# http://localhost:3000/sitemap.xml

# Проверить robots.txt
# http://localhost:3000/robots.txt

# Проверить мета-теги (View Page Source)
# http://localhost:3000/catalog/lamis/bathroom-furniture/siena/
```

---

## Контрольный список (обновленный)

### ЭТАП 7: Роутинг ✅
- [x] Изучена структура Next.js App Router
- [x] Созданы API функции для catalog navigation
- [x] Создана страница секции `/catalog/[sectionSlug]/`
- [x] Создана страница категории `/catalog/[sectionSlug]/[categorySlug]/`
- [x] Создана страница продуктов `/catalog/[sectionSlug]/[categorySlug]/[itemSlug]/`
- [x] Реализованы breadcrumbs на всех уровнях
- [x] Добавлена обработка ошибок (notFound)

### ЭТАП 8: Django Admin ✅
- [x] Добавлены fieldsets для TypeAdmin
- [x] Добавлен ProductInline для inline editing
- [x] Создана кастомная колонка product_count с ссылкой
- [x] Создана кастомная колонка slug_display
- [x] Оптимизирован queryset с select_related и annotate
- [x] Добавлен bulk action "Дублировать типы"
- [x] Добавлен bulk action "Экспортировать в CSV"
- [x] Улучшен CollectionAdmin аналогично

### ЭТАП 9: SEO ✅
- [x] Добавлена generateMetadata для секции
- [x] Добавлена generateMetadata для категории
- [x] Добавлена generateMetadata для продуктов
- [x] Добавлены Open Graph теги
- [x] Добавлены Twitter Card теги
- [x] Добавлены canonical URLs
- [x] Создан sitemap.ts с автогенерацией
- [x] Создан robots.ts
- [x] Добавлены robots meta tags

### Документация ✅
- [x] Обновлен IMPLEMENTATION_SUMMARY.md для ЭТАП 7-9

---

## Следующие шаги (опционально)

### Улучшения производительности
1. **Image Optimization**
   - Использовать Next.js Image component
   - Настроить image loader для внешних изображений
   - Добавить blur placeholders

2. **Caching**
   - Настроить ISR (Incremental Static Regeneration)
   - Добавить client-side caching
   - Настроить HTTP caching headers

3. **API Optimization**
   - Добавить Redis cache для API responses
   - Оптимизировать database queries
   - Добавить pagination для больших списков

### Аналитика и мониторинг
1. **Google Analytics**
   - Добавить GA4 tracking
   - Настроить event tracking для навигации
   - Отслеживание конверсий

2. **Search Console**
   - Подключить Google Search Console
   - Отслеживать индексацию sitemap
   - Мониторить ошибки crawling

### Дополнительные SEO улучшения
1. **Structured Data**
   ```typescript
   // Добавить JSON-LD для продуктов
   const structuredData = {
     "@context": "https://schema.org",
     "@type": "Product",
     "name": product.name,
     "image": product.image,
     "description": product.description,
   };
   ```

2. **Multilingual Support**
   - Добавить hreflang tags
   - Локализация контента
   - Языковые версии sitemap

---

## История изменений

| Версия | Дата | Описание |
|--------|------|----------|
| 1.0 | 2025-01-15 | Первая версия документации после завершения ЭТАП 2-6 |
| 2.0 | 2025-01-15 | Добавлена документация ЭТАП 7-9 (Роутинг, Admin, SEO) |
