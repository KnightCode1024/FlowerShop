import { ApiError, type ApiErrorPayload } from "./authApi";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ??
  "http://localhost:8000/api";

export interface CategoryListItem {
  id: number;
  name: string;
  products_count: number;
}

export interface ProductListItem {
  id: number;
  name: string;
  description: string | null;
  price: number | string;
  in_stock: boolean;
  category_id: number;
  main_image_url: string | null;
  category_name: string;
}

export interface ProductImage {
  url: string;
  order: number;
  is_primary: boolean;
}

export interface ProductDetails {
  id: number;
  name: string;
  description: string | null;
  price: number | string;
  in_stock: boolean;
  category_id: number;
  images: ProductImage[];
  category: {
    id: number;
    name: string;
  };
}

export interface ProductFilters {
  offset?: number;
  limit?: number;
  min_price?: number;
  max_price?: number;
  category_id?: number;
  in_stock?: boolean;
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
  });

  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as ApiErrorPayload;
  throw new ApiError(data.detail ?? "Ошибка запроса", response.status);
  }

  return (await response.json()) as T;
}

export async function getCategories(limit = 100): Promise<CategoryListItem[]> {
  return request<CategoryListItem[]>(`/categories?offset=0&limit=${limit}`);
}

export async function getProducts(
  filters: ProductFilters = {},
): Promise<ProductListItem[]> {
  const params = new URLSearchParams();

  if (filters.offset !== undefined) {
    params.set("offset", String(filters.offset));
  }
  if (filters.limit !== undefined) {
    params.set("limit", String(filters.limit));
  }
  if (filters.min_price !== undefined) {
    params.set("min_price", String(filters.min_price));
  }
  if (filters.max_price !== undefined) {
    params.set("max_price", String(filters.max_price));
  }
  if (filters.category_id !== undefined) {
    params.set("category_id", String(filters.category_id));
  }
  if (filters.in_stock !== undefined) {
    params.set("in_stock", String(filters.in_stock));
  }

  const query = params.toString();
  return request<ProductListItem[]>(`/products${query ? `?${query}` : ""}`);
}

export async function getProduct(productId: number): Promise<ProductDetails> {
  return request<ProductDetails>(`/products/${productId}`);
}

export function formatPrice(value: number | string): string {
  const amount = typeof value === "string" ? Number(value) : value;
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 2,
  }).format(Number.isFinite(amount) ? amount : 0);
}
